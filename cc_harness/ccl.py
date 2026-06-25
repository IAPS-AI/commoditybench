#!/usr/bin/env python3
"""ccl.py — read the US Commerce Control List (the benchmark's navigation tools, as a CLI).

This is the *exact* tool surface the API benchmark exposes to the model under test, wrapped
as four shell commands so a Claude Code session can call them via Bash. It loads the parsed
CCL (``ccl_index.json``, 637 entries from the eCFR) sitting next to this script. No network,
no answer key — just the list.

    python ccl.py categories                 # list_ccl_categories
    python ccl.py outline <0-9>              # get_category_outline (controls + catch-alls)
    python ccl.py read <ECCN>                # read_eccn (full text, thresholds, subparagraphs)
    python ccl.py search "<free-text>"       # search_ccl (keyword, ranked, unbiased)

Every command prints a JSON object/array to stdout — that JSON is your tool result. Read it,
then make your next call or submit your answer. See CLAUDE.md for the procedure.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

INDEX_PATH = Path(__file__).resolve().parent / "ccl_index.json"

# --- vendored verbatim from the benchmark (commoditybench.eccn / .ccl.index) so behaviour
#     is byte-identical to the scored API runs ------------------------------------------
CATEGORY_NAMES = {
    "0": "Nuclear Materials, Facilities, and Equipment (and Miscellaneous)",
    "1": "Materials, Chemicals, Microorganisms, and Toxins",
    "2": "Materials Processing",
    "3": "Electronics",
    "4": "Computers",
    "5": "Telecommunications (Part 1) and Information Security (Part 2)",
    "6": "Sensors and Lasers",
    "7": "Navigation and Avionics",
    "8": "Marine",
    "9": "Aerospace and Propulsion",
}
GROUP_NAMES = {
    "A": "Systems, Equipment, and Components",
    "B": "Test, Inspection, and Production Equipment",
    "C": "Materials",
    "D": "Software",
    "E": "Technology",
}
_ECCN_HEAD_RE = re.compile(r"^([0-9])([A-E])([0-9]{3})(.*)$")
_STOP = {
    "the", "a", "an", "and", "or", "of", "for", "to", "in", "with", "on", "by", "is",
    "as", "at", "be", "are", "not", "any", "all", "this", "that", "from", "up", "its",
}


def _normalize(text: str) -> str:
    t = text.strip().upper()
    t = re.sub(r"^ECCN[:\s]*", "", t)
    t = t.replace(" ", "").replace("-", "")
    t = re.sub(r"\.+", ".", t).strip(".")
    return t


def _head(eccn: str) -> str:
    norm = _normalize(eccn)
    m = _ECCN_HEAD_RE.match(norm)
    return f"{m.group(1)}{m.group(2)}{m.group(3)}" if m else norm[:5]


def _norm_category(category: str) -> str:
    c = str(category).strip()
    m = re.search(r"[0-9]", c)
    return m.group(0) if m else c


def _tokens(text: str) -> set:
    return {t for t in re.split(r"[^a-z0-9]+", text.lower()) if len(t) > 2 and t not in _STOP}


class CCL:
    def __init__(self, entries):
        self.entries = entries
        self.by_head = {e["eccn"]: e for e in entries}

    @classmethod
    def load(cls):
        if not INDEX_PATH.exists():
            sys.exit(f"Missing {INDEX_PATH.name} next to ccl.py — the CCL data file.")
        data = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
        return cls(data["entries"])

    def get(self, eccn):
        return self.by_head.get(_head(eccn))

    def categories(self):
        counts = {}
        for e in self.entries:
            counts[e["category"]] = counts.get(e["category"], 0) + 1
        return [{"category": c, "name": CATEGORY_NAMES[c], "n_entries": counts.get(c, 0)}
                for c in sorted(CATEGORY_NAMES)]

    def outline(self, category):
        category = _norm_category(category)
        groups = {}
        for e in self.entries:
            if e["category"] != category:
                continue
            groups.setdefault(e["group"], []).append({
                "eccn": e["eccn"], "title": e["title"],
                "reason_for_control": e["reason_for_control"], "is_catchall": e["is_catchall"],
            })
        ordered = {g: sorted(groups[g], key=lambda x: x["eccn"]) for g in sorted(groups)}
        return {"category": category, "name": CATEGORY_NAMES.get(category, ""),
                "group_names": {g: GROUP_NAMES[g] for g in ordered},
                "entries_by_group": ordered}

    def read(self, eccn, max_chars=8000):
        e = self.get(eccn)
        if e is None:
            head = _head(eccn)
            prefix = head[:2]
            nbrs = [x["eccn"] for x in self.entries if x["eccn"].startswith(prefix)][:20]
            return {"eccn": head, "found": False,
                    "message": f"No CCL entry {head!r}. Use outline to list a category's ECCNs, "
                               "or search to find one.", "suggestions": nbrs}
        text = e["text"] if len(e["text"]) <= max_chars else e["text"][:max_chars] + "\n...[truncated]"
        return {"eccn": e["eccn"], "found": True, "title": e["title"],
                "category": e["category"], "category_name": CATEGORY_NAMES.get(e["category"], ""),
                "group": e["group"], "group_name": GROUP_NAMES.get(e["group"], ""),
                "reason_for_control": e["reason_for_control"], "is_catchall": e["is_catchall"],
                "text": text}

    def search(self, query, top_k=8):
        terms = _tokens(query)
        if not terms:
            return []
        scored = []
        for e in self.entries:
            tt, bt = _tokens(e["title"]), _tokens(e["text"])
            score = 3.0 * sum(t in tt for t in terms) + sum(t in bt for t in terms)
            if score > 0:
                scored.append((score, e))
        scored.sort(key=lambda s: (-s[0], s[1]["eccn"]))
        return [{"eccn": e["eccn"], "title": e["title"],
                 "reason_for_control": e["reason_for_control"],
                 "is_catchall": e["is_catchall"], "score": round(score, 2)}
                for score, e in scored[:top_k]]


def main(argv=None):
    ap = argparse.ArgumentParser(description="Read the Commerce Control List.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("categories", help="List the ten CCL categories (0-9) with entry counts.")
    o = sub.add_parser("outline", help="List every ECCN in a category (controls + catch-alls).")
    o.add_argument("category")
    r = sub.add_parser("read", help="Full controlling text of one ECCN (thresholds, subparagraphs).")
    r.add_argument("eccn")
    s = sub.add_parser("search", help="Keyword-search the CCL; ranked, unbiased.")
    s.add_argument("query", nargs="+")
    args = ap.parse_args(argv)

    ccl = CCL.load()
    if args.cmd == "categories":
        out = ccl.categories()
    elif args.cmd == "outline":
        out = ccl.outline(args.category)
    elif args.cmd == "read":
        out = ccl.read(args.eccn)
    else:
        out = ccl.search(" ".join(args.query))
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
