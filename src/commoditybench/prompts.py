"""Prompt construction for the classification task.

We keep the system prompt provider-agnostic and ask every model for the same structured
JSON answer, so scoring is uniform. Adapters that support native structured outputs
(e.g. the Anthropic adapter) enforce the schema; others rely on the instruction plus a
robust fallback extractor (see :func:`commoditybench.eccn.extract_eccn`).
"""

from __future__ import annotations

from .dataset import Question

# JSON Schema for the answer, reused by adapters that support structured outputs.
ANSWER_SCHEMA = {
    "type": "object",
    "properties": {
        "eccn": {
            "type": "string",
            "description": "The single most likely ECCN (e.g. '3A001.a.1.a') or 'EAR99' "
            "if the item is subject to the EAR but not listed on the CCL.",
        },
        "category": {
            "type": "string",
            "description": "The single-digit CCL category (0-9) you assigned, or 'EAR99'.",
        },
        "reasoning": {
            "type": "string",
            "description": "A brief justification citing the controlling CCL text or "
            "technical parameters that drove the decision.",
        },
    },
    # All properties are listed in `required`: OpenAI's strict json_schema mode mandates
    # that every key in `properties` also appear in `required` (with additionalProperties
    # false), or the request 400s. Anthropic/Gemini accept this too.
    "required": ["eccn", "category", "reasoning"],
    "additionalProperties": False,
}

SYSTEM_PROMPT = """\
You are an expert US export-control classification analyst. Your task is the same one \
performed by the Bureau of Industry and Security (BIS): given a description of a \
commodity, determine the single Export Control Classification Number (ECCN) under which \
it falls on the Commerce Control List (CCL, Supplement No. 1 to Part 774 of the EAR).

Rules:
- Return exactly one ECCN, as specific as the description supports (include the \
subparagraph when it is determinable, e.g. "3A001.a.1.a").
- If the item is subject to the EAR but is not described by any CCL entry, return \
"EAR99".
- Base the classification on the item's technical characteristics and function, not on \
its country of origin or end use.
- Respond ONLY with the requested JSON object. Do not add commentary outside it."""

USER_TEMPLATE = """\
Classify the following item and return the JSON object described by the schema.

Item name: {item_name}
Description: {description}
{context_block}
Respond with a JSON object: {{"eccn": "...", "category": "...", "reasoning": "..."}}"""

CONTEXT_TEMPLATE = """
Relevant excerpts from the Commerce Control List (retrieved automatically; they may or \
may not be on point — judge for yourself):
\"\"\"
{context}
\"\"\"
"""


def build_user_prompt(question: Question, context: str | None = None) -> str:
    """Build the user prompt. When ``context`` is given (RAG mode), CCL excerpts are
    injected between the item description and the answer instruction."""
    context_block = CONTEXT_TEMPLATE.format(context=context) if context else ""
    return USER_TEMPLATE.format(
        item_name=question.item_name,
        description=question.description,
        context_block=context_block,
    )
