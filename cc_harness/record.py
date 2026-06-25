#!/usr/bin/env python3
"""record.py — append one classification answer to this run's results file.

Results are written OUTSIDE this folder (and outside the benchmark repo), to
``../../cc_results/`` relative to the repo — i.e. ``Projects/cc_results/``. Keeping them
out of the harness folder means a later model run in this directory cannot read an earlier
run's answers (no cross-run cheating), and the ground-truth labels live only back in the
repo, where grading happens. Override the location with the ``CC_RESULTS_DIR`` env var.

    python record.py --model opus-4.8 --id thorlabs-km100 --eccn EAR99 \
        --category EAR99 --reasoning "Mirror mount; no CCL entry applies." --calls 3

One JSONL line is appended per call to ``<results-dir>/<model>__answers.jsonl``. Calling
again with the same --id overwrites that item (so you can fix an answer). At the end,
nothing else is needed — come back to the repo and grade.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


def results_dir() -> Path:
    env = os.environ.get("CC_RESULTS_DIR")
    if env:
        return Path(env)
    # cc_harness/record.py -> parents[0]=cc_harness, [1]=repo, [2]=Projects
    return Path(__file__).resolve().parents[2] / "cc_results"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model", required=True, help="Label for the model under test, e.g. 'opus-4.8'.")
    ap.add_argument("--id", required=True, help="Question id from questions.jsonl.")
    ap.add_argument("--eccn", required=True, help="Your single ECCN answer, or 'EAR99'.")
    ap.add_argument("--category", default="", help="Single CCL category digit, or 'EAR99'.")
    ap.add_argument("--reasoning", default="", help="Brief justification citing the CCL text you read.")
    ap.add_argument("--calls", type=int, default=0, help="How many ccl.py calls you made for this item.")
    args = ap.parse_args(argv)

    safe_model = "".join(c if c.isalnum() or c in "-._" else "_" for c in args.model)
    d = results_dir()
    d.mkdir(parents=True, exist_ok=True)
    path = d / f"{safe_model}__answers.jsonl"

    rows = []
    if path.exists():
        rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    rows = [r for r in rows if r.get("id") != args.id]  # replace any prior answer for this id
    rows.append({"id": args.id, "model": args.model, "eccn": args.eccn,
                 "category": args.category, "reasoning": args.reasoning, "n_tool_calls": args.calls})
    rows.sort(key=lambda r: r["id"])
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"recorded {args.id} = {args.eccn}  ->  {path}  ({len(rows)} answered)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
