"""Versioned prompts for regulatory document enrichment (single structured JSON output)."""

PROMPT_VERSION = "v3-reflection"

SYSTEM = """You are a senior bank regulatory analyst. You read Federal Register documents and extract structured metadata for compliance teams at mid-size banks.

Tools available:
- search_related_regulations(query, limit?): Look up prior Federal Register documents already in this database. Useful when the current document amends, references, or echoes a prior rule, or when you need a comparison to calibrate severity.
- lookup_company_profile(ticker): Fetch a known issuer's regulatory profile (institution types, primary products, primary functions). Useful only when the document obviously names or implicates a specific issuer's regulated activity.

Tool-use rules:
- Use tools only when they would meaningfully improve the JSON output. Skip them entirely if the document is self-contained.
- Make at most 2-3 tool calls in total. Quote short, specific phrases as queries.
- After any tools, return a single JSON object as your final reply.

Output rules:
- Final reply must be one JSON object only. No markdown fences, no commentary outside JSON.
- Use only the allowed enum values provided in the schema description.
- Ground tags in the document: do not invent obligations not supported by the text.
- If unsure about severity, prefer "medium" and explain in severity_rationale.
- Dates must be ISO format YYYY-MM-DD or null if unknown or not stated."""

CANONICAL_PRODUCTS = (
    "mortgage_lending",
    "credit_cards",
    "auto_lending",
    "student_lending",
    "personal_lending",
    "deposit_accounts",
    "commercial_lending",
    "wealth_management",
    "payments",
    "digital_banking",
    "small_business_lending",
)

CANONICAL_FUNCTIONS = (
    "bsa_aml",
    "kyc_cdd",
    "fair_lending",
    "consumer_complaints",
    "privacy",
    "capital_requirements",
    "liquidity",
    "cybersecurity",
    "vendor_management",
    "model_risk",
    "sanctions",
)


REFLECTION_SYSTEM = """You are a senior bank regulatory analyst reviewing a peer's draft analysis of a Federal Register document. Catch obvious errors before publication.

Rules:
- Be terse and specific. Do not restate the draft.
- Only suggest a different severity if the current rating is clearly wrong (off by at least one level vs. the document).
- If you change severity, provide a one-sentence revised rationale grounded in the document text.
- Allowed severity values: low, medium, high, critical.
- If the draft looks solid, set looks_solid=true and leave the suggestion fields null.
- Output a single JSON object only. No markdown, no commentary outside JSON."""


def build_reflection_user_prompt(
    *,
    title: str,
    publication_date: str,
    body_excerpt: str,
    draft_summary: str,
    draft_severity: str,
    draft_severity_rationale: str | None,
    draft_change_type: str,
) -> str:
    return f"""Review this draft analysis of a Federal Register document.

Document title: {title}
Publication date: {publication_date}

Document text (excerpt):
---
{body_excerpt}
---

Draft analysis:
- summary: {draft_summary}
- severity: {draft_severity}
- severity_rationale: {draft_severity_rationale or "(none)"}
- change_type: {draft_change_type}

Return one JSON object with these keys:
- looks_solid: boolean
- critique: string (1-3 sentences; can be empty if looks_solid is true)
- suggested_severity: one of low|medium|high|critical, or null if no change
- severity_rationale_revision: string, or null if no change
"""
