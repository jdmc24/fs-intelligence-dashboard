"""Tools exposed to Claude during regulatory enrichment.

Both tools are read-only DB queries against the existing app schema:
- `search_related_regulations`: keyword search over prior Federal Register docs.
- `lookup_company_profile`: fetch a ticker's regulatory profile.

The model decides when (and whether) to call them. The dispatcher returns
JSON-serializable dicts so results can be both sent back to the model and
stored as a reasoning trace.
"""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CompanyRegProfile, RegDocument, RegEnrichment

TOOLS: list[dict[str, Any]] = [
    {
        "name": "search_related_regulations",
        "description": (
            "Search previously-ingested Federal Register documents by keyword. "
            "Use this when the current document references prior rules, amendments, or guidance, "
            "or when you need context to calibrate severity. "
            "Returns up to `limit` brief matches with id, title, agencies, publication_date, "
            "and (if already enriched) severity and a short summary excerpt."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Keyword phrase matched against document title and abstract.",
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 10,
                    "description": "Max results (default 5).",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "lookup_company_profile",
        "description": (
            "Look up a known issuer's regulatory profile by ticker. "
            "Returns institution_types, primary_products, and primary_functions for the ticker. "
            "Use this when the document obviously implicates a specific issuer's regulated activity."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker, e.g. JPM, BAC, HBAN.",
                },
            },
            "required": ["ticker"],
        },
    },
]


async def _search_related_regulations(session: AsyncSession, query: str, limit: int = 5) -> dict[str, Any]:
    q = (query or "").strip()
    if not q:
        return {"matches": [], "count": 0, "note": "empty query"}
    like = f"%{q}%"
    n = max(1, min(int(limit or 5), 10))
    stmt = (
        select(RegDocument, RegEnrichment)
        .outerjoin(RegEnrichment, RegEnrichment.document_id == RegDocument.id)
        .where(or_(RegDocument.title.ilike(like), RegDocument.abstract.ilike(like)))
        .order_by(RegDocument.publication_date.desc())
        .limit(n)
    )
    rows = (await session.execute(stmt)).all()
    matches: list[dict[str, Any]] = []
    for d, e in rows:
        matches.append(
            {
                "id": d.id,
                "document_number": d.document_number,
                "title": (d.title or "")[:240],
                "publication_date": d.publication_date.isoformat(),
                "agencies": json.loads(d.agencies or "[]"),
                "severity": e.severity if e else None,
                "summary_excerpt": (e.summary[:300] if e and e.summary else None),
            }
        )
    return {"matches": matches, "count": len(matches), "query": q, "limit": n}


async def _lookup_company_profile(session: AsyncSession, ticker: str) -> dict[str, Any]:
    t = (ticker or "").strip().upper()
    if not t:
        return {"found": False, "note": "empty ticker"}
    p = await session.get(CompanyRegProfile, t)
    if p is None:
        return {"found": False, "ticker": t}
    return {
        "found": True,
        "ticker": p.ticker,
        "name": p.name,
        "institution_types": json.loads(p.institution_types or "[]"),
        "primary_products": json.loads(p.primary_products or "[]"),
        "primary_functions": json.loads(p.primary_functions or "[]"),
        "gics_sector": p.gics_sector,
        "gics_sub_industry": p.gics_sub_industry,
    }


async def execute_tool(session: AsyncSession, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Dispatch a tool by name. Returns a JSON-serializable dict result.

    Unknown tools return a structured error rather than raising; the model is
    expected to recover by either re-asking or producing a final JSON answer.
    """
    args = arguments or {}
    if name == "search_related_regulations":
        return await _search_related_regulations(
            session,
            query=str(args.get("query") or ""),
            limit=int(args.get("limit") or 5),
        )
    if name == "lookup_company_profile":
        return await _lookup_company_profile(session, ticker=str(args.get("ticker") or ""))
    return {"error": f"unknown tool: {name}"}
