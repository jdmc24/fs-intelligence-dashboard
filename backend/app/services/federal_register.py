"""Federal Register API v1 client (https://www.federalregister.gov/reader/api).

federalregister.gov blocks requests with the default httpx user-agent
(`python-httpx/X.Y.Z`), returning CAPTCHA / access-denial HTML on the
public document endpoints. We send a descriptive User-Agent (the same
identifier used for SEC EDGAR) so the site treats us as a known caller.
Without this header, raw_text and html document fetches succeed with
status 200 but return CAPTCHA pages — invisible to `raise_for_status`
but catastrophic for any downstream LLM that treats the body as the
rule text.
"""

from __future__ import annotations

import datetime as dt
from typing import Any

import httpx

from app.settings import settings

FR_BASE = "https://www.federalregister.gov/api/v1"


def _request_headers() -> dict[str, str]:
    """Headers sent on every federalregister.gov request.

    The User-Agent identifies us as a known caller; without it the site
    returns CAPTCHA pages on the public document URLs (200 OK, but the
    body is an access-denial page). Accept-Language and Accept hint we
    are a real client rather than a default bot.
    """
    return {
        "User-Agent": settings.sec_user_agent,
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/plain,text/html;q=0.9,*/*;q=0.5",
    }

# Slugs from regulatory-monitor-prd-v2.md
DEFAULT_AGENCY_SLUGS: tuple[str, ...] = (
    "consumer-financial-protection-bureau",
    "comptroller-of-the-currency",
    "federal-reserve-system",
    "federal-deposit-insurance-corporation",
    "securities-and-exchange-commission",
    "financial-crimes-enforcement-network",
)

# API filter slugs (not the same strings as `type` on each result row).
DEFAULT_DOC_TYPES: tuple[str, ...] = ("RULE", "PRORULE", "NOTICE")


def _build_params(
    *,
    agencies: list[str],
    page: int,
    per_page: int,
    publication_date_gte: dt.date | None,
    publication_date_lte: dt.date | None,
    doc_types: tuple[str, ...] | None,
) -> list[tuple[str, str]]:
    """Federal Register expects repeated keys for array conditions."""
    pairs: list[tuple[str, str]] = []
    for a in agencies:
        pairs.append(("conditions[agencies][]", a))
    dts = doc_types or DEFAULT_DOC_TYPES
    for t in dts:
        pairs.append(("conditions[type][]", t))
    if publication_date_gte is not None:
        pairs.append(("conditions[publication_date][gte]", publication_date_gte.isoformat()))
    if publication_date_lte is not None:
        pairs.append(("conditions[publication_date][lte]", publication_date_lte.isoformat()))
    pairs.append(("per_page", str(per_page)))
    pairs.append(("page", str(page)))
    pairs.append(("order", "newest"))
    return pairs


async def fetch_documents_page(
    *,
    agencies: list[str] | None = None,
    page: int = 1,
    per_page: int = 100,
    publication_date_gte: dt.date | None = None,
    publication_date_lte: dt.date | None = None,
    doc_types: tuple[str, ...] | None = None,
    timeout: float = 60.0,
) -> dict[str, Any]:
    ag = list(agencies) if agencies else list(DEFAULT_AGENCY_SLUGS)
    params = _build_params(
        agencies=ag,
        page=page,
        per_page=min(per_page, 1000),
        publication_date_gte=publication_date_gte,
        publication_date_lte=publication_date_lte,
        doc_types=doc_types,
    )
    url = f"{FR_BASE}/documents.json"
    async with httpx.AsyncClient(timeout=timeout, headers=_request_headers()) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        return r.json()


# Markers that indicate federalregister.gov served a bot-protection page
# instead of the actual document body. We treat any response containing
# one of these as a failed fetch so the caller falls through to the next
# strategy (raw_text → body_html → html → abstract).
#
# "Request Access" is the title FR uses on its current bot-challenge
# page (e.g. when the public html_url is hit by an automated client).
# We match a few variants in case the wording changes.
_BOT_BLOCK_MARKERS: tuple[str, ...] = (
    "Federal Register :: Request Access",
    "Request Access",
    "Please complete the security check",
    "Pardon Our Interruption",
    "you've been blocked",
    "Access Denied",
    "Are you a robot",
    "challenge-platform",
)


def _looks_like_bot_block(body: str) -> bool:
    if not body:
        return True
    head = body[:4000].lower()
    for marker in _BOT_BLOCK_MARKERS:
        if marker.lower() in head:
            return True
    return False


async def fetch_raw_text(raw_text_url: str, timeout: float = 120.0) -> str:
    """Fetch a document's plain-text body from federalregister.gov.

    Raises RuntimeError if the response is bot-blocked even with a
    proper User-Agent — caller can fall back to other strategies.
    """
    async with httpx.AsyncClient(
        timeout=timeout, follow_redirects=True, headers=_request_headers()
    ) as client:
        r = await client.get(raw_text_url)
        r.raise_for_status()
        text = r.text
        if _looks_like_bot_block(text):
            raise RuntimeError(
                f"federalregister.gov returned a bot-protection page for {raw_text_url}; "
                "raw_text fetch did not yield the document body"
            )
        return text


def normalize_fr_result(item: dict[str, Any]) -> dict[str, Any]:
    """Map API JSON item to fields we persist."""
    agencies_raw = item.get("agencies") or []
    agency_labels: list[str] = []
    if isinstance(agencies_raw, list):
        for a in agencies_raw:
            if isinstance(a, dict) and a.get("name"):
                agency_labels.append(str(a["name"]))
            elif isinstance(a, str):
                agency_labels.append(a)

    topics_raw = item.get("topics") or []
    topics: list[str] = []
    if isinstance(topics_raw, list):
        for t in topics_raw:
            if isinstance(t, dict) and t.get("name"):
                topics.append(str(t["name"]))
            elif isinstance(t, str):
                topics.append(t)

    cfr_raw = item.get("cfr_references") or []
    cfr: list[str] = []
    if isinstance(cfr_raw, list):
        for c in cfr_raw:
            if isinstance(c, dict):
                title = c.get("title")
                part = c.get("part")
                if title is not None and part is not None:
                    cfr.append(f"{title} CFR Part {part}")
            elif isinstance(c, str):
                cfr.append(c)

    pub = item.get("publication_date")
    if isinstance(pub, str) and len(pub) >= 10:
        pub_date = dt.date.fromisoformat(pub[:10])
    else:
        pub_date = dt.date.today()

    doc_type = item.get("type") or item.get("document_type") or "Notice"
    if isinstance(doc_type, dict):
        doc_type = doc_type.get("name") or "Notice"
    doc_type_str = str(doc_type)

    return {
        "document_number": str(item.get("document_number") or item.get("id") or ""),
        "title": str(item.get("title") or "(untitled)"),
        "abstract": item.get("abstract"),
        "publication_date": pub_date,
        "document_type": doc_type_str,
        "agencies": agency_labels,
        "federal_register_url": str(item.get("html_url") or ""),
        "pdf_url": item.get("pdf_url"),
        "raw_text_url": item.get("raw_text_url"),
        # body_html_url is the clean HTML body without the user-facing
        # chrome that triggers FR's bot-challenge page. Prefer this as a
        # fallback to html_url.
        "body_html_url": item.get("body_html_url"),
        "html_url": str(item.get("html_url") or ""),
        "cfr_references": cfr,
        "topics": topics,
    }
