"""Build the CCL index from the eCFR source for 15 CFR 774, Supplement No. 1.

The eCFR serves the CCL as XML with a regular structure:

    <HD1>Category 3-Electronics</HD1>          # category heading
    <HD1>A. "End Items," ...</HD1>              # product-group heading (noise we skip)
    <FP-2><B>3A001 Electronic items ...</B>     # one ECCN entry header
      ... License Requirements / Reason for Control / List of Items Controlled ...
    <FP-2><B>3A002 ...</B>                       # next entry begins here

Each entry runs from its ``<FP-2><B>NNNN`` header to the next entry header or the next
heading, whichever comes first. We strip the markup to readable text (keeping the
"Items:" subparagraph list, which carries the control thresholds), derive the
category/group/number from the ECCN token itself, and write one JSON record per entry.

Run::

    py -3.12 -m commoditybench.ccl.parse_ecfr --fetch          # download + parse
    py -3.12 -m commoditybench.ccl.parse_ecfr --source ccl.xml # parse a local file

Output defaults to ``data/ccl/ccl_index.json`` (committed, so eval needs no network).
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

from ..eccn import parse as parse_eccn

# eCFR versioner endpoint for the CCL appendix. The date must be <= the title's most
# recent issue date; --fetch resolves it automatically from /titles.json.
ECFR_TITLES_URL = "https://www.ecfr.gov/api/versioner/v1/titles.json"
ECFR_CCL_URL = (
    "https://www.ecfr.gov/api/versioner/v1/full/{date}/title-15.xml"
    "?appendix=Supplement%20No.%201%20to%20Part%20774"
)

DEFAULT_OUTPUT = Path("data/ccl/ccl_index.json")

# An ECCN entry header: <FP-2><B>NNNN ...  (title may contain nested inline markup, so we
# only anchor on the token and recover the title from the block's stripped text).
_ENTRY_RE = re.compile(r"<FP-2><B>\s*([0-9][A-E][0-9]{3})")
_HEADING_RE = re.compile(r"<HD1>", re.IGNORECASE)
_FP2_BLOCK_RE = re.compile(r"<FP-2>(.*?)</FP-2>", re.S)

_UNICODE_FIXES = {
    "—": "-", "–": "-", "−": "-",  # em/en dash, minus
    "‘": "'", "’": "'",                  # curly single quotes
    "“": '"', "”": '"',                  # curly double quotes
    " ": " ", " ": " ", " ": " ",   # non-breaking spaces
}


def _norm(s: str) -> str:
    s = html.unescape(s)
    for k, v in _UNICODE_FIXES.items():
        s = s.replace(k, v)
    return s


def _to_text(span: str) -> str:
    """Strip XML markup from an entry span to readable text.

    Closing block tags and ``<br>`` become newlines; table cells are joined with " | "
    so the License Requirements / Country Chart tables stay legible. The result keeps the
    subparagraph ("Items:") list intact, which is where the control thresholds live.
    """
    s = re.sub(r"</(TR|P|FP-1|FP-2|FP|HED|NOTE|HD2|HD1|LI)>", "\n", span)
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.IGNORECASE)
    s = re.sub(r"</T[DH]>", " | ", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = _norm(s)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r" *\n *", "\n", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def _reason_for_control(text: str) -> str:
    m = re.search(r"Reason for Control:\s*([^\n]+)", text)
    return m.group(1).strip() if m else ""


def _title_from_block(block_xml: str, eccn: str) -> str:
    """Recover an entry's title (the bold header minus the ECCN token)."""
    txt = _norm(re.sub(r"<[^>]+>", "", block_xml)).strip()
    txt = txt[len(eccn):].strip() if txt.startswith(eccn) else txt
    # Trim the trailing pointer to the items list and any leftover period.
    txt = re.sub(r"\s*\(see List of Items Controlled\)\.?$", "", txt, flags=re.I)
    return txt.strip(" .")


def parse_ccl_xml(xml: str) -> list[dict]:
    """Parse the CCL appendix XML into per-ECCN entry records."""
    # Map FP-2 block start -> its inner XML, to recover titles with inline markup.
    fp2_blocks = {m.start(): m.group(1) for m in _FP2_BLOCK_RE.finditer(xml)}

    # Boundary positions: every ECCN entry header and every HD1 heading. An entry ends at
    # the next boundary of either kind.
    boundaries: list[tuple[int, str, str]] = []
    for m in _ENTRY_RE.finditer(xml):
        boundaries.append((m.start(), "entry", m.group(1)))
    for m in _HEADING_RE.finditer(xml):
        boundaries.append((m.start(), "heading", ""))
    boundaries.sort()

    entries: list[dict] = []
    seen: set[str] = set()
    for i, (pos, kind, eccn) in enumerate(boundaries):
        if kind != "entry":
            continue
        if eccn in seen:  # guard against any duplicate header
            continue
        seen.add(eccn)
        end = boundaries[i + 1][0] if i + 1 < len(boundaries) else len(xml)
        span = xml[pos:end]
        parsed = parse_eccn(eccn)
        block_xml = fp2_blocks.get(pos, "")
        title = _title_from_block(block_xml, eccn)
        text = _to_text(span)
        entries.append(
            {
                "eccn": eccn,
                "category": parsed.category,
                "group": parsed.group,
                "number": parsed.number,
                "title": title,
                "reason_for_control": _reason_for_control(text),
                # A control whose title says "not controlled by X" is a catch-all/basket
                # entry — the ones models systematically forget exist.
                "is_catchall": bool(re.search(r"not controlled by", title, re.I)),
                "text": text,
            }
        )
    entries.sort(key=lambda e: e["eccn"])
    return entries


def _latest_issue_date() -> str:
    import urllib.request

    with urllib.request.urlopen(ECFR_TITLES_URL, timeout=60) as r:
        data = json.load(r)
    for t in data.get("titles", []):
        if t.get("number") == 15:
            return t.get("up_to_date_as_of") or t.get("latest_issue_date")
    raise RuntimeError("Could not find Title 15 issue date in eCFR /titles.json")


def fetch_ccl_xml() -> str:
    import urllib.request

    date = _latest_issue_date()
    url = ECFR_CCL_URL.format(date=date)
    print(f"Fetching CCL as of {date} ...", file=sys.stderr)
    with urllib.request.urlopen(url, timeout=180) as r:
        return r.read().decode("utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--fetch", action="store_true", help="Download the CCL from eCFR.")
    src.add_argument("--source", help="Path to a local CCL appendix XML file.")
    ap.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Index JSON path.")
    ap.add_argument(
        "--save-xml", help="Also write the raw source XML here (for reproducibility)."
    )
    args = ap.parse_args(argv)

    xml = fetch_ccl_xml() if args.fetch else Path(args.source).read_text(encoding="utf-8")
    if args.save_xml:
        Path(args.save_xml).parent.mkdir(parents=True, exist_ok=True)
        Path(args.save_xml).write_text(xml, encoding="utf-8")

    entries = parse_ccl_xml(xml)
    if not entries:
        print("No ECCN entries parsed — check the source XML.", file=sys.stderr)
        return 1

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "source": "15 CFR 774, Supplement No. 1 (eCFR)",
        "n_entries": len(entries),
        "entries": entries,
    }
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")

    by_cat: dict[str, int] = {}
    for e in entries:
        by_cat[e["category"]] = by_cat.get(e["category"], 0) + 1
    print(f"Wrote {len(entries)} ECCN entries to {out}", file=sys.stderr)
    print("  per category: " + ", ".join(f"{k}:{by_cat[k]}" for k in sorted(by_cat)),
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
