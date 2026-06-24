"""Helper for assembling and validating the benchmark dataset.

This is curation tooling, not an automated scraper — manufacturer self-classifications
require human judgment to turn into clean questions (see data/schema.md). What it does:

    validate  : check a .jsonl file against the Question schema and the ECCN format,
                and report coverage (per-category counts, verified vs. unverified, EAR99).
    template  : print a blank question record you can fill in.

Usage:
    python scripts/build_dataset.py validate data/questions.example.jsonl
    python scripts/build_dataset.py template
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

# Allow running from a source checkout without installing.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from commoditybench.dataset import load_questions  # noqa: E402
from commoditybench.eccn import parse  # noqa: E402

TEMPLATE = {
    "id": "VENDOR-PRODUCT-001",
    "item_name": "",
    "description": "Functional + technical characteristics only. Do NOT include the "
    "vendor name or the ECCN here.",
    "gold_eccn": "",
    "manufacturer": "",
    "source_url": "",
    "source_type": "manufacturer_self_classification",
    "verified": False,
    "category": "",
    "difficulty": "medium",
    "notes": "",
}


def cmd_validate(path: str) -> int:
    questions = load_questions(path)
    problems: list[str] = []
    cats: Counter = Counter()
    verified = 0
    ear99 = 0
    seen_ids: set[str] = set()

    for q in questions:
        if q.id in seen_ids:
            problems.append(f"duplicate id: {q.id}")
        seen_ids.add(q.id)

        e = parse(q.gold_eccn)
        if not e.is_valid:
            problems.append(f"{q.id}: gold_eccn {q.gold_eccn!r} is not a valid ECCN/EAR99")
        if e.is_ear99:
            ear99 += 1
        elif e.category:
            cats[e.category] += 1
        if q.verified:
            verified += 1
        # Leakage check: neither the full ECCN nor its CGNNN head should appear in the
        # description (which is all the model sees). Normalize the description first so
        # "3 A 001" / "3a001" variants are caught, not just the exact string.
        if not e.is_ear99 and e.head:
            from commoditybench.eccn import normalize_eccn_text

            norm_desc = normalize_eccn_text(q.description)
            if e.head in norm_desc or normalize_eccn_text(q.gold_eccn) in norm_desc:
                problems.append(f"{q.id}: gold_eccn (or its head {e.head}) leaks into the description")

    print(f"Loaded {len(questions)} questions from {path}")
    print(f"  verified:   {verified}  unverified: {len(questions) - verified}")
    print(f"  EAR99:      {ear99}")
    print("  by category:")
    for c in sorted(cats):
        print(f"    {c} ({_cat_name(c)}): {cats[c]}")

    if problems:
        print(f"\n{len(problems)} problem(s):", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1
    print("\nOK: no schema/format problems found.")
    return 0


def _cat_name(c: str) -> str:
    from commoditybench.eccn import CATEGORY_NAMES

    return CATEGORY_NAMES.get(c, "?")


def cmd_template() -> int:
    print(json.dumps(TEMPLATE, indent=2))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("validate", help="Validate a dataset file and report coverage.")
    v.add_argument("path")
    sub.add_parser("template", help="Print a blank question record.")
    args = ap.parse_args()

    if args.cmd == "validate":
        return cmd_validate(args.path)
    if args.cmd == "template":
        return cmd_template()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
