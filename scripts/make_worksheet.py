"""Generate data/verification_worksheet.md from the current data/questions.jsonl.

Each row's verification link (and the part to search, for tool-based sources) is placed
directly in the decision table so you can verify in-line without scrolling to the
evidence section. Re-run after editing the dataset:

    python scripts/make_worksheet.py
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

REPO = Path(__file__).resolve().parents[1]
QUESTIONS = REPO / "data" / "questions.jsonl"
OUT = REPO / "data" / "verification_worksheet.md"

ADI_TOOL = "analog.com"
MCHIP_TOOL = "microchipdirect"


def host(url: str) -> str:
    if url.startswith("human-review-sources"):
        return "invoice"
    return (urlparse(url).netloc or url).replace("www.", "")


def tier(r: dict) -> str:
    if r["verified"]:
        return "VERIFIED"
    h = host(r["source_url"])
    if ADI_TOOL in h:
        return "A · ADI"
    if MCHIP_TOOL in h:
        return "B · Microchip"
    if "digikey" in h:
        return "B · Digi-Key"
    if "thorlabs" in h:
        return "C · not visible"
    return "?"


def search_part(r: dict) -> str | None:
    """Tool-based sources (ADI/Microchip) need a part typed into a search box; pull it
    out of the note text where it was recorded as: search '<PART>'."""
    m = re.search(r"search '([^']+)'", r.get("notes", ""))
    return m.group(1) if m else None


def verify_cell(r: dict) -> str:
    """A clickable link plus, for tool sources, the exact part to search."""
    url = r["source_url"]
    h = host(r["source_url"])
    if h == "invoice":
        return f"[invoice]({url})"
    if ADI_TOOL in h:
        part = search_part(r) or ""
        return f"[ADI tool]({url}) → search `{part}`"
    if MCHIP_TOOL in h:
        part = search_part(r) or ""
        return f"[Microchip tool]({url}) → search `{part}`"
    if "digikey" in h:
        return f"[Digi-Key page]({url})"
    if "thorlabs" in h:
        return f"[page — ECCN not shown]({url})"
    return f"[link]({url})"


def main() -> None:
    rows = [
        json.loads(line)
        for line in QUESTIONS.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

    out: list[str] = ["# Verification worksheet — CommodityBench dataset\n"]
    out.append(
        "Generated from `data/questions.jsonl` by `scripts/make_worksheet.py`. The "
        "**Verify here** column links straight to each source (and gives the part to "
        "search for tool-based sources), so you can confirm in-line. Mark the **✅** column "
        "as you go, then tell the assistant which sources are confirmed and it flips "
        "`verified: true`.\n"
    )
    out.append(
        "**Tiers:** VERIFIED = you confirmed it. `A · ADI` = on the BIS list, ECCN "
        "human-visible in ADI's tool. `B` = human-visible but off the BIS list (Microchip "
        "tool / Digi-Key page). `C` = ECCN not human-visible on the source.\n"
    )

    tc = Counter(tier(r) for r in rows)
    out.append("## Status: " + "  ·  ".join(f"{n} {t}" for t, n in sorted(tc.items())) + "\n")

    out.append(
        "> **Bulk-confirm tip:** each source renders ECCNs the same way, so spot-check 2 "
        "rows per source; if they match, confirm the whole source. Any Tier C row (ECCN "
        "not human-visible on the source) needs an invoice or another human-visible "
        "source, else drop.\n"
    )

    out.append("## Decision table\n")
    out.append("| # | Item | ECCN | Tier | Verify here | ✅ | Your notes |")
    out.append("|---|------|------|------|-------------|:--:|------------|")
    for i, r in enumerate(rows, 1):
        done = "✅" if r["verified"] else ""
        item = r["item_name"].replace("|", "/")
        out.append(
            f"| {i} | {item} | `{r['gold_eccn']}` | {tier(r)} | {verify_cell(r)} | {done} |  |"
        )
    out.append("")

    out.append("## Evidence (per item)\n")
    for i, r in enumerate(rows, 1):
        out.append(f"### {i}. {r['id']} — `{r['gold_eccn']}`  [{tier(r)}]")
        out.append(f"- **Item:** {r['item_name']} ({r['manufacturer']})")
        out.append(f"- **Source:** {r['source_url']}")
        out.append(f"- **Notes:** {r.get('notes', '')}")
        out.append("")

    OUT.write_text("\n".join(out), encoding="utf-8")
    print(f"Wrote {OUT.relative_to(REPO)} ({len(rows)} items)")
    for t, n in sorted(tc.items()):
        print(f"  {t}: {n}")


if __name__ == "__main__":
    main()
