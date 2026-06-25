"""CCL navigation tools the model can call while classifying.

These are the tools of the *agentic-navigation* condition. They are provider-agnostic:
each tool is described once here, with helpers to emit the schema in Anthropic's and
OpenAI's tool-calling formats, plus a single :class:`CCLToolbox` dispatcher that executes
a tool call against a :class:`CCLIndex`. The agent loops "call a tool -> read result ->
call another" until it is ready to answer.

The toolset mirrors how a human analyst walks the CCL, and is aimed squarely at the
benchmark's observed error modes:

    list_ccl_categories  -> pick the right category
    get_category_outline -> see controls AND the x991/x992 catch-alls together
    read_eccn            -> check the exact thresholds / subparagraphs of a candidate
    search_ccl           -> find a candidate entry by description
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .index import CCLIndex


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    input_schema: dict


TOOL_SPECS: list[ToolSpec] = [
    ToolSpec(
        name="list_ccl_categories",
        description=(
            "List the ten CCL categories (0-9) with their names and entry counts. Use "
            "this first to decide which category the item most plausibly falls in."
        ),
        input_schema={"type": "object", "properties": {}, "additionalProperties": False},
    ),
    ToolSpec(
        name="get_category_outline",
        description=(
            "List every ECCN in a category, grouped by product group (A-E), with each "
            "entry's title and reason for control. Entries flagged is_catchall (titled "
            "'not controlled by ...') are basket entries that may describe items not "
            "captured by the specific controls; an item is EAR99 only when no entry — "
            "specific or catch-all — applies. Call this once you have a candidate category."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "A single CCL category digit, '0' through '9'.",
                }
            },
            "required": ["category"],
            "additionalProperties": False,
        },
    ),
    ToolSpec(
        name="read_eccn",
        description=(
            "Return the full controlling text of one ECCN entry: license requirements, "
            "reason for control, related controls, and the 'Items:' list with its "
            "subparagraphs and numeric thresholds. Use this to check whether the item "
            "actually meets a candidate entry's parameters, and to resolve the correct "
            "subparagraph down to the matching leaf. Accepts a 5-char head or a full ECCN."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "eccn": {
                    "type": "string",
                    "description": "An ECCN such as '5A992' or '3A001.a.5.b.2'.",
                }
            },
            "required": ["eccn"],
            "additionalProperties": False,
        },
    ),
    ToolSpec(
        name="search_ccl",
        description=(
            "Keyword-search the CCL by a short description of the item and its salient "
            "specs. Returns candidate ECCN entries ranked by term overlap (no class is "
            "favoured). Use when you are unsure which entry or category applies."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Free-text description of the item or its function.",
                }
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    ),
]


def anthropic_tools() -> list[dict]:
    """Tool specs in Anthropic Messages-API format."""
    return [
        {"name": t.name, "description": t.description, "input_schema": t.input_schema}
        for t in TOOL_SPECS
    ]


def openai_tools() -> list[dict]:
    """Tool specs in OpenAI Chat-Completions function-calling format."""
    return [
        {
            "type": "function",
            "function": {
                "name": t.name,
                "description": t.description,
                "parameters": t.input_schema,
            },
        }
        for t in TOOL_SPECS
    ]


class CCLToolbox:
    """Executes CCL tool calls against an index, tracking a usage trace for auditing."""

    def __init__(self, index: CCLIndex | None = None):
        self.index = index or CCLIndex.load()
        self.calls: list[dict] = []  # audit trail: [{tool, input, ...}]
        self._dispatch: dict[str, Callable[[dict], Any]] = {
            "list_ccl_categories": lambda _inp: self.index.list_categories(),
            "get_category_outline": lambda inp: self.index.category_outline(
                str(inp.get("category", ""))
            ),
            "read_eccn": lambda inp: self.index.read(str(inp.get("eccn", ""))),
            "search_ccl": lambda inp: self.index.search(str(inp.get("query", ""))),
        }

    def call(self, name: str, tool_input: dict | None = None) -> Any:
        """Run one tool call; returns a JSON-serializable result (never raises)."""
        tool_input = tool_input or {}
        fn = self._dispatch.get(name)
        if fn is None:
            result: Any = {"error": f"Unknown tool {name!r}."}
        else:
            try:
                result = fn(tool_input)
            except Exception as exc:  # surface to the model rather than crashing the run
                result = {"error": f"{type(exc).__name__}: {exc}"}
        self.calls.append({"tool": name, "input": tool_input})
        return result
