"""Shared pieces for the agentic CCL-navigation condition.

The agent is given the CCL navigation tools (see ``ccl.tools``) plus one terminal tool,
``submit_classification``, whose input *is* the answer schema. It researches the list by
calling tools, then ends the turn by calling ``submit_classification`` — which gives us a
clean, schema-valid answer without fighting a provider's structured-output mode while
tools are active. Each provider adapter implements the call/observe loop; this module
holds the parts that don't depend on the provider: the system prompt, the submit tool,
and a helper to turn a submitted answer into a :class:`Prediction`.
"""

from __future__ import annotations

from ..prompts import ANSWER_SCHEMA
from .base import Prediction

# Terminal tool: its input schema is exactly the classification answer. The loop ends
# when the model calls it, and we read its arguments as the final answer.
SUBMIT_TOOL_NAME = "submit_classification"
SUBMIT_TOOL_DESCRIPTION = (
    "Submit your final classification. Call this exactly once, only after you have used "
    "the CCL tools to confirm the controlling entry and (where determinable) the correct "
    "subparagraph. The arguments are your answer."
)

# How many tool round-trips before we force the model to submit. Generous enough for a
# search -> outline -> read-a-few-entries walk; bounded so a confused agent can't loop.
DEFAULT_MAX_STEPS = 12

AGENTIC_SYSTEM_PROMPT = """\
You are an expert US export-control classification analyst performing the task BIS does: \
given a commodity description, determine the single Export Control Classification Number \
(ECCN) it falls under on the Commerce Control List (CCL, Supplement No. 1 to Part 774 of \
the EAR), or EAR99 if it is subject to the EAR but not listed on the CCL.

You have tools that let you read the actual CCL. Do NOT classify from memory — look it \
up. Follow this order of review:

1. Identify the most plausible category. Use list_ccl_categories and/or search_ccl.
2. Call get_category_outline for that category. Read the whole outline, not just the \
first hit. Note both the specific high-performance control entries AND the catch-all / \
basket entries (flagged is_catchall, titled "not controlled by ...").
3. For each candidate entry, call read_eccn and check the item against the actual \
parameters in the "Items:" list. An item is only controlled by an entry if it MEETS that \
entry's specific thresholds. If it falls below a specific entry's thresholds, check \
whether a catch-all/basket entry in the same category captures it before concluding \
EAR99 — EAR99 means no CCL entry, including the catch-alls, describes the item.
4. Resolve the classification to the most specific subparagraph the item's parameters \
support, by reading the entry's item list down to the matching leaf rather than stopping \
at a top-level paragraph.
5. Classify the item as it is, not as a category: distinguish a standalone component \
from complete equipment, and read an entry's own text to decide whether the item meets \
it — do not assume a control applies (or doesn't) from the item's general type.

Base the classification on the item's technical characteristics and function, not its \
country of origin or end use. When you are confident, call submit_classification with \
your final ECCN, the category, and a brief justification citing the controlling text you \
read. You must finish by calling submit_classification exactly once."""


def submit_tool_input_schema() -> dict:
    """The submit tool's input schema (the shared answer schema)."""
    return ANSWER_SCHEMA


def prediction_from_submission(
    args: dict,
    *,
    raw_response: str = "",
    usage: dict | None = None,
    tool_trace: list[dict] | None = None,
    parsed_ok: bool = True,
) -> Prediction:
    """Build a :class:`Prediction` from a ``submit_classification`` tool call's args."""
    eccn = str(args.get("eccn", "")).strip()
    pred = Prediction(
        predicted_eccn=eccn,
        reasoning=str(args.get("reasoning", "")),
        raw_response=raw_response,
        parsed_ok=parsed_ok and bool(eccn),
        usage=usage or {},
    )
    # Stash the tool-use audit trail so results capture how the agent navigated.
    pred.usage = {**pred.usage, "tool_calls": tool_trace or []}
    return pred
