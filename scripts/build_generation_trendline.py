"""Build a METR-style capability-vs-release-date trendline across Claude generations.

Ingests two cross-generation runs produced by ``commoditybench.run_eval`` —
``--run-id gen`` (no tools) and ``--run-id gen_agentic`` (CCL navigation tools) — and
plots each headline metric against each model's *release date* (the METR x-axis). The
output is a self-contained, offline HTML page with an inline SVG chart (no JS, no CDN,
no plotting dependency — matching the rest of the dashboard tooling) plus a data table.

The five points are the Opus generation ladder, each run in its strongest NATIVE
reasoning config (see registry.py / results/generation_ab_findings.md). This is a
capability snapshot, NOT an equalized comparison — the page says so.

Usage:
    PYTHONPATH=src py -3.12 scripts/build_generation_trendline.py \
        --notools results/gen__summary.json --agentic results/gen_agentic__summary.json \
        --out dashboard/generation_trendline.html
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

# Authoritative release dates from the Anthropic Models API (created_at), used as the
# trendline x-axis. Keep in sync with the ladder registered in models/registry.py.
RELEASE_DATES: dict[str, date] = {
    "claude-opus-4-1": date(2025, 8, 5),
    "claude-opus-4-5": date(2025, 11, 24),
    "claude-opus-4-6": date(2026, 2, 4),
    "claude-opus-4-7": date(2026, 4, 14),
    "claude-opus-4-8": date(2026, 5, 28),
}
LABELS = {
    "claude-opus-4-1": "Opus 4.1",
    "claude-opus-4-5": "Opus 4.5",
    "claude-opus-4-6": "Opus 4.6",
    "claude-opus-4-7": "Opus 4.7",
    "claude-opus-4-8": "Opus 4.8",
}


def _load(path: str) -> dict[str, dict]:
    report = json.loads(Path(path).read_text(encoding="utf-8"))
    return {m["model"]: m for m in report["models"]}, report


def _series(summary: dict[str, dict], metric: str) -> list[tuple[date, float, str]]:
    pts = []
    for model, d in RELEASE_DATES.items():
        if model in summary:
            pts.append((d, summary[model][metric], model))
    return sorted(pts, key=lambda t: t[0])


# --- SVG helpers ---------------------------------------------------------------------
W, H = 860, 480
ML, MR, MT, MB = 70, 180, 48, 64  # margins (wide right margin for the legend)
PLOT_W, PLOT_H = W - ML - MR, H - MT - MB


def _x(d: date, d0: date, d1: date) -> float:
    span = (d1 - d0).days or 1
    return ML + PLOT_W * (d - d0).days / span


def _y(v: float) -> float:
    return MT + PLOT_H * (1 - v)  # y axis 0..1, top = 1.0


def _line(summary, metric, d0, d1, color, dash, label, legend_y):
    pts = _series(summary, metric)
    if not pts:
        return ""
    coords = [(_x(d, d0, d1), _y(v)) for d, v, _ in pts]
    path = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in coords)
    dots = "".join(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="{color}" />'
        for x, y in coords
    )
    da = f' stroke-dasharray="{dash}"' if dash else ""
    legend = (
        f'<line x1="{W-MR+12}" y1="{legend_y}" x2="{W-MR+44}" y2="{legend_y}" '
        f'stroke="{color}" stroke-width="2.5"{da}/>'
        f'<text x="{W-MR+50}" y="{legend_y+4}" font-size="12" fill="#1f2933">{label}</text>'
    )
    return (
        f'<path d="{path}" fill="none" stroke="{color}" stroke-width="2.5"{da}/>'
        f"{dots}{legend}"
    )


def build_svg(notools, agentic) -> str:
    d0 = min(RELEASE_DATES.values())
    d1 = max(RELEASE_DATES.values())
    parts = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" '
             'font-family="system-ui,-apple-system,Segoe UI,Roboto,sans-serif">']
    parts.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="#fbfaf7"/>')

    # y gridlines + labels (0..1 by 0.2)
    for i in range(6):
        v = i / 5
        y = _y(v)
        parts.append(f'<line x1="{ML}" y1="{y:.1f}" x2="{ML+PLOT_W}" y2="{y:.1f}" '
                     'stroke="#e6e1d6" stroke-width="1"/>')
        parts.append(f'<text x="{ML-10}" y="{y+4:.1f}" font-size="11" fill="#6b7280" '
                     f'text-anchor="end">{v:.1f}</text>')

    # x ticks at each generation
    for d, _, model in _series(notools, "exact_accuracy") or _series(agentic, "exact_accuracy"):
        x = _x(d, d0, d1)
        parts.append(f'<line x1="{x:.1f}" y1="{MT+PLOT_H}" x2="{x:.1f}" y2="{MT+PLOT_H+5}" '
                     'stroke="#9ca3af"/>')
        parts.append(f'<text x="{x:.1f}" y="{MT+PLOT_H+20}" font-size="11" fill="#374151" '
                     f'text-anchor="middle">{LABELS[model]}</text>')
        parts.append(f'<text x="{x:.1f}" y="{MT+PLOT_H+34}" font-size="9" fill="#9ca3af" '
                     f'text-anchor="middle">{d.strftime("%b %Y")}</text>')

    # axes
    parts.append(f'<line x1="{ML}" y1="{MT}" x2="{ML}" y2="{MT+PLOT_H}" stroke="#374151"/>')
    parts.append(f'<line x1="{ML}" y1="{MT+PLOT_H}" x2="{ML+PLOT_W}" y2="{MT+PLOT_H}" '
                 'stroke="#374151"/>')
    parts.append(f'<text x="{ML+PLOT_W/2:.0f}" y="{H-12}" font-size="12" fill="#374151" '
                 'text-anchor="middle">Model release date →</text>')
    parts.append(f'<text transform="translate(18,{MT+PLOT_H/2:.0f}) rotate(-90)" '
                 'font-size="12" fill="#374151" text-anchor="middle">Accuracy on '
                 'verified set (n=23)</text>')

    # legend header
    parts.append(f'<text x="{W-MR+12}" y="{MT+2}" font-size="11" fill="#9ca3af" '
                 'font-weight="600">SERIES</text>')

    # four series: grade + exact, each for tools (solid) and no-tools (dashed)
    AMBER, TEAL = "#c2730a", "#0f766e"
    parts.append(_line(agentic, "mean_grade", d0, d1, AMBER, None, "grade · tools", MT+24))
    parts.append(_line(notools, "mean_grade", d0, d1, AMBER, "5,4", "grade · no tools", MT+44))
    parts.append(_line(agentic, "exact_accuracy", d0, d1, TEAL, None, "exact · tools", MT+72))
    parts.append(_line(notools, "exact_accuracy", d0, d1, TEAL, "5,4", "exact · no tools", MT+92))

    parts.append("</svg>")
    return "".join(parts)


def build_table(notools, agentic) -> str:
    rows = []
    for model, d in RELEASE_DATES.items():
        nt = notools.get(model, {})
        ag = agentic.get(model, {})
        rows.append(
            f"<tr><td>{LABELS[model]}</td><td>{d.isoformat()}</td>"
            f"<td>{nt.get('exact_accuracy','—')}</td><td>{nt.get('mean_grade','—')}</td>"
            f"<td>{ag.get('exact_accuracy','—')}</td><td>{ag.get('mean_grade','—')}</td>"
            f"<td>{(ag.get('errors','—'))}/{(nt.get('errors','—'))}</td></tr>"
        )
    return "\n".join(rows)


HTML = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>CommodityBench — capability across Claude generations</title>
<style>
 body{{margin:0;background:#fbfaf7;color:#1f2933;font-family:system-ui,-apple-system,
   "Segoe UI",Roboto,sans-serif;line-height:1.55}}
 .wrap{{max-width:920px;margin:0 auto;padding:32px 24px 64px}}
 h1{{font-size:24px;margin:0 0 4px}} .sub{{color:#6b7280;font-size:14px;margin:0 0 24px}}
 .card{{background:#fff;border:1px solid #ece7dc;border-radius:12px;padding:20px;
   box-shadow:0 1px 2px rgba(0,0,0,.03);margin-bottom:24px}}
 table{{border-collapse:collapse;width:100%;font-size:13px}}
 th,td{{text-align:left;padding:7px 10px;border-bottom:1px solid #eee}}
 th{{color:#6b7280;font-weight:600;font-size:11px;text-transform:uppercase;letter-spacing:.04em}}
 td:first-child{{font-weight:600}}
 .note{{background:#fff7ec;border:1px solid #f3dcb5;border-radius:10px;padding:12px 16px;
   font-size:13px;color:#7c4a03}}
 code{{background:#f3f0e8;padding:1px 5px;border-radius:4px;font-size:12px}}
</style></head><body><div class="wrap">
<h1>Capability across Claude generations</h1>
<p class="sub">ECCN commodity classification · Opus generation ladder · verified set (n=23)
 · METR-style trendline of accuracy vs. model release date</p>
<div class="card">{svg}</div>
{pending}
<div class="card">
 <table>
  <tr><th>Generation</th><th>Released</th><th>exact · no tools</th><th>grade · no tools</th>
      <th>exact · tools</th><th>grade · tools</th><th>errors (tools/no)</th></tr>
  {table}
 </table>
</div>
<div class="note"><strong>Capability snapshot, not an equalized comparison.</strong>
 Each generation runs in its strongest <em>native</em> reasoning config — Opus 4.1/4.5 use
 extended thinking (<code>budget_tokens</code>); 4.6/4.7/4.8 use adaptive thinking; 4.1 has
 no <code>effort</code> parameter. n=23 verified questions, so each item is ≈0.04 of the
 score — read the <em>shape</em> of the trend, not single-point gaps. "tools" = the model
 navigates the parsed CCL via the <code>--agentic</code> condition before answering.</div>
</div></body></html>"""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--notools", required=True, help="gen__summary.json (no-tools run)")
    ap.add_argument("--agentic", default=None,
                    help="gen_agentic__summary.json (tools run); optional — omit to plot "
                    "the no-tools trendline alone.")
    ap.add_argument("--out", default="dashboard/generation_trendline.html")
    args = ap.parse_args(argv)

    notools, _ = _load(args.notools)
    agentic, _ = _load(args.agentic) if args.agentic else ({}, None)
    svg = build_svg(notools, agentic)
    pending = "" if agentic else (
        '<div class="note" style="background:#fdeceb;border-color:#f3b6b3;color:#8a2a24">'
        "<strong>Tools condition pending.</strong> The agentic (CCL-navigation) run did "
        "not complete — the API account hit its credit balance partway through. Only the "
        "<em>no-tools</em> trendline is shown here. Re-run "
        "<code>--agentic --run-id gen_agentic</code> once credits are available, then "
        "rebuild with both <code>--notools</code> and <code>--agentic</code>.</div>"
    )
    html = HTML.format(svg=svg, table=build_table(notools, agentic), pending=pending)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
