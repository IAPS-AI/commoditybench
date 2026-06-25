"""Load and query the parsed CCL index.

``CCLIndex`` is the read side of the agentic-navigation tools. It answers the three
questions a classifier needs while walking the list:

    * ``category_outline(cat)`` — every ECCN header + title in a category, grouped A-E,
      so the high-performance controls and the ``x991``/``x992`` catch-alls are visible
      together (the catch-alls being exactly what models forget exist).
    * ``read(eccn)`` — the full controlling text of one entry, including the "Items:"
      subparagraph list where the control thresholds live.
    * ``search(query)`` — a keyword fallback for finding entries by description.

The index is a plain JSON file built by ``parse_ecfr.py``; no vector store or network is
needed, which keeps the agentic condition cheap and fully reproducible.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Optional

from ..eccn import CATEGORY_NAMES, GROUP_NAMES, normalize_eccn_text, parse as parse_eccn

DEFAULT_INDEX_PATH = Path(__file__).resolve().parents[3] / "data" / "ccl" / "ccl_index.json"


@dataclass(frozen=True)
class CCLEntry:
    eccn: str
    category: str
    group: str
    number: str
    title: str
    reason_for_control: str
    is_catchall: bool
    text: str


class CCLIndex:
    def __init__(self, entries: list[CCLEntry]):
        self._entries = entries
        self._by_eccn = {e.eccn: e for e in entries}

    # -- construction ------------------------------------------------------------------
    @classmethod
    def load(cls, path: str | Path = DEFAULT_INDEX_PATH) -> "CCLIndex":
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(
                f"No CCL index at {p}. Build one first:\n"
                "  py -3.12 -m commoditybench.ccl.parse_ecfr --fetch"
            )
        data = json.loads(p.read_text(encoding="utf-8"))
        entries = [CCLEntry(**{k: e[k] for k in CCLEntry.__annotations__}) for e in data["entries"]]
        return cls(entries)

    # -- basic access ------------------------------------------------------------------
    def __len__(self) -> int:
        return len(self._entries)

    @staticmethod
    def _head(eccn: str) -> str:
        """The 5-char CGNNN head for a (possibly messy) ECCN string."""
        return parse_eccn(eccn).head or normalize_eccn_text(eccn)[:5]

    def get(self, eccn: str) -> Optional[CCLEntry]:
        """Look up an entry by its 5-char head, tolerant of formatting/subparagraphs."""
        return self._by_eccn.get(self._head(eccn))

    # -- tool-facing queries -----------------------------------------------------------
    def list_categories(self) -> list[dict]:
        """The ten CCL categories with names and how many entries each has."""
        counts: dict[str, int] = {}
        for e in self._entries:
            counts[e.category] = counts.get(e.category, 0) + 1
        return [
            {"category": c, "name": CATEGORY_NAMES[c], "n_entries": counts.get(c, 0)}
            for c in sorted(CATEGORY_NAMES)
        ]

    def category_outline(self, category: str) -> dict:
        """Headers + titles for every entry in a category, grouped by product group.

        This is the workhorse: it lets the model see, for (say) Category 5, that besides
        the controlled ``5A002`` there is a ``5A991`` ("not controlled by 5A001") and a
        ``5A992`` ("not controlled by 5A002", which carries mass-market encryption) — the
        catch-alls it otherwise misses.
        """
        category = _norm_category(category)
        groups: dict[str, list[dict]] = {}
        for e in self._entries:
            if e.category != category:
                continue
            groups.setdefault(e.group, []).append(
                {
                    "eccn": e.eccn,
                    "title": e.title,
                    "reason_for_control": e.reason_for_control,
                    "is_catchall": e.is_catchall,
                }
            )
        ordered = {
            g: sorted(groups[g], key=lambda x: x["eccn"]) for g in sorted(groups)
        }
        return {
            "category": category,
            "name": CATEGORY_NAMES.get(category, ""),
            "group_names": {g: GROUP_NAMES[g] for g in ordered},
            "entries_by_group": ordered,
        }

    def read(self, eccn: str, *, max_chars: int = 8000) -> dict:
        """Full controlling text of one entry (truncated to a sane budget)."""
        e = self.get(eccn)
        if e is None:
            head = self._head(eccn)
            return {
                "eccn": head,
                "found": False,
                "message": f"No CCL entry {head!r}. Use category_outline to list valid "
                "ECCNs for its category, or search to find one.",
                "suggestions": self._neighbors(head),
            }
        text = e.text if len(e.text) <= max_chars else e.text[:max_chars] + "\n...[truncated]"
        return {
            "eccn": e.eccn,
            "found": True,
            "title": e.title,
            "category": e.category,
            "category_name": CATEGORY_NAMES.get(e.category, ""),
            "group": e.group,
            "group_name": GROUP_NAMES.get(e.group, ""),
            "reason_for_control": e.reason_for_control,
            "is_catchall": e.is_catchall,
            "text": text,
        }

    def search(self, query: str, *, top_k: int = 8) -> list[dict]:
        """Keyword search over titles + body text, ranked by term overlap.

        Deliberately simple (token-overlap, title-weighted) and *unbiased* — the model
        supplies the query and judges the hits; this just surfaces plausible entries
        verbatim from the CCL, without a vector store and without favouring any entry
        class. (An earlier version up-weighted catch-alls; that was a thumb on the scale
        toward this dataset's answers and has been removed.)
        """
        terms = _tokens(query)
        if not terms:
            return []
        scored: list[tuple[float, CCLEntry]] = []
        for e in self._entries:
            title_toks = _tokens(e.title)
            body_toks = _tokens(e.text)
            score = 3.0 * sum(t in title_toks for t in terms) + sum(
                t in body_toks for t in terms
            )
            if score > 0:
                scored.append((score, e))
        scored.sort(key=lambda s: (-s[0], s[1].eccn))
        return [
            {
                "eccn": e.eccn,
                "title": e.title,
                "reason_for_control": e.reason_for_control,
                "is_catchall": e.is_catchall,
                "score": round(score, 2),
            }
            for score, e in scored[:top_k]
        ]

    def _neighbors(self, head: str) -> list[str]:
        """ECCNs sharing the category+group of a missing head, for error recovery."""
        if len(head) < 2:
            return []
        prefix = head[:2]
        return [e.eccn for e in self._entries if e.eccn.startswith(prefix)][:20]

    @cached_property
    def catchalls(self) -> list[str]:
        return [e.eccn for e in self._entries if e.is_catchall]


def _norm_category(category: str) -> str:
    c = str(category).strip()
    m = re.search(r"[0-9]", c)
    return m.group(0) if m else c


_STOP = {
    "the", "a", "an", "and", "or", "of", "for", "to", "in", "with", "on", "by", "is",
    "as", "at", "be", "are", "not", "any", "all", "this", "that", "from", "up", "its",
}


def _tokens(text: str) -> set[str]:
    return {
        t for t in re.split(r"[^a-z0-9]+", text.lower()) if len(t) > 2 and t not in _STOP
    }
