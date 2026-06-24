"""Generate a self-contained results dashboard microsite from an eval run.

Reads a ``<run_id>__summary.json`` and its per-model ``<run_id>__<model>.jsonl`` files
and emits a single static ``index.html`` with the data embedded (works offline via
``file://`` — no server, no CDN, no build step). Regenerate after any run:

    PYTHONPATH=src py -3.12 scripts/build_dashboard.py \\
        --summary results/qwen3_32b_runpod__summary.json --out dashboard/index.html

If ``--summary`` is omitted, the most recently modified ``*__summary.json`` under
``results/`` is used.
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
TEMPLATE = HERE / "dashboard_template.html"


def _latest_summary(results_dir: Path) -> Path:
    cands = sorted(
        results_dir.glob("*__summary.json"), key=lambda p: p.stat().st_mtime, reverse=True
    )
    if not cands:
        raise SystemExit(f"No *__summary.json found under {results_dir}/. Run an eval first.")
    return cands[0]


def _load_rows(results_dir: Path, run_id: str, model: str) -> list[dict]:
    path = results_dir / f"{run_id}__{model}.jsonl"
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def build(summary_path: Path, out_path: Path) -> None:
    report = json.loads(summary_path.read_text(encoding="utf-8"))
    results_dir = summary_path.parent
    run_id = report["run_id"]

    rows_by_model = {m["model"]: _load_rows(results_dir, run_id, m["model"]) for m in report["models"]}

    data = {
        "report": report,
        "rows": rows_by_model,
        "generated": date.today().isoformat(),
        "grade_weights": {"exact": 1.0, "eccn": 0.7, "group": 0.4, "category": 0.2, "none": 0.0},
    }

    template = TEMPLATE.read_text(encoding="utf-8")
    html = template.replace("/*__DATA__*/", json.dumps(data, ensure_ascii=False))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    n_rows = sum(len(r) for r in rows_by_model.values())
    print(f"Wrote {out_path}  ({len(report['models'])} model(s), {n_rows} prediction rows)")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--summary", help="Path to a <run_id>__summary.json (default: latest under results/).")
    ap.add_argument("--out", default=str(ROOT / "dashboard" / "index.html"), help="Output HTML path.")
    args = ap.parse_args(argv)

    summary = Path(args.summary) if args.summary else _latest_summary(ROOT / "results")
    build(summary, Path(args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
