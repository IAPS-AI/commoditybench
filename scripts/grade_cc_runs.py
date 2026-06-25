"""Grade Claude-Code subscription runs (cc_harness) against ground truth.

The ``cc_harness/`` kit lets you run the *agentic* (read-the-CCL) condition through a Claude
Code session on a Max subscription instead of paying for API tokens: you switch model in
``/model``, paste the kickoff prompt, and the model classifies every item using ``ccl.py``,
saving answers to ``cc_results/<label>__answers.jsonl`` OUTSIDE the harness (so runs can't
peek at each other, and no gold lives next to the questions).

This script closes the loop: it joins those answers to the gold labels in
``data/questions.jsonl`` (which never left the repo), scores them with the SAME graded
scorer as the API benchmark, and writes run_eval-shaped summaries so the numbers are
directly comparable to the no-tools ``gen`` run and the API agentic A/B.

    PYTHONPATH=src py -3.12 scripts/grade_cc_runs.py            # grade all labels found
    PYTHONPATH=src py -3.12 scripts/grade_cc_runs.py --results-dir <dir> --run-id cc_agentic
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from commoditybench.dataset import load_questions
from commoditybench.eccn import score_prediction

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DEFAULT_RESULTS = ROOT.parent / "cc_results"  # Projects/cc_results — matches record.py


def _aggregate(label: str, rows: list[dict]) -> dict:
    """Headline metrics over all rows (unanswered/errored count as 0) — mirrors run_eval."""
    n = len(rows) or 1
    errors = sum(1 for r in rows if r["error"])
    scored = [r["score"] for r in rows if not r["error"]]

    def rate(key: str) -> float:
        return round(sum(1 for s in scored if s[key]) / n, 4)

    return {
        "model": label, "n": len(rows), "answered": len(scored),
        "errors": errors, "error_rate": round(errors / n, 4),
        "exact_accuracy": rate("exact_match"), "eccn_accuracy": rate("eccn_match"),
        "group_accuracy": rate("group_match"), "category_accuracy": rate("category_match"),
        "parse_rate": rate("parsed"),
        "mean_grade": round(sum(s["grade"] for s in scored) / n, 4),
    }


def grade_label(label: str, answers: list[dict], gold: dict) -> tuple[dict, list[dict]]:
    by_id = {a["id"]: a for a in answers}
    rows = []
    for qid, q in gold.items():
        a = by_id.get(qid)
        if a is None:  # not answered in this run — counts as wrong, like an API error
            rows.append({
                "id": qid, "item_name": q.item_name, "gold_eccn": q.gold_eccn,
                "predicted_eccn": "", "category": q.category, "verified": q.verified,
                "reasoning": "", "parsed_ok": False, "error": "not answered",
                "n_tool_calls": 0, "usage": {}, "score": score_prediction("", q.gold_eccn).to_dict(),
            })
            continue
        pred = (a.get("eccn") or "").strip()
        score = score_prediction(pred, q.gold_eccn)
        rows.append({
            "id": qid, "item_name": q.item_name, "gold_eccn": q.gold_eccn,
            "predicted_eccn": pred, "category": q.category, "verified": q.verified,
            "reasoning": a.get("reasoning", ""), "parsed_ok": score.parsed, "error": None,
            "n_tool_calls": a.get("n_tool_calls", 0), "usage": {},
            "score": score.to_dict(),
        })
    rows.sort(key=lambda r: r["id"])
    return _aggregate(label, rows), rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--results-dir", default=str(DEFAULT_RESULTS),
                    help=f"Where record.py wrote answers (default {DEFAULT_RESULTS}).")
    ap.add_argument("--dataset", default=str(ROOT / "data" / "questions.jsonl"))
    ap.add_argument("--out-dir", default=str(ROOT / "results"))
    ap.add_argument("--run-id", default="cc_agentic")
    args = ap.parse_args(argv)

    rdir = Path(args.results_dir)
    files = sorted(rdir.glob("*__answers.jsonl")) if rdir.exists() else []
    if not files:
        print(f"No '*__answers.jsonl' files in {rdir}. Run the harness first (see cc_harness/).")
        return 1

    gold = {q.id: q for q in load_questions(args.dataset, verified_only=True)}
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    summaries = []
    for f in files:
        label = f.name[: -len("__answers.jsonl")]
        answers = [json.loads(l) for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]
        summ, rows = grade_label(label, answers, gold)
        summaries.append(summ)
        (out_dir / f"{args.run_id}__{label}.jsonl").write_text(
            "\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")

    summaries.sort(key=lambda s: s["mean_grade"], reverse=True)
    report = {"run_id": args.run_id, "dataset": args.dataset, "condition": "agentic (Claude Code, subscription)",
              "n_questions": len(gold), "verified_only": True, "citable": True,
              "note": "Agentic CCL-navigation run via Claude Code on a Max subscription, "
                      "graded against the verified set. Comparable to the no-tools 'gen' run.",
              "models": summaries}
    (out_dir / f"{args.run_id}__summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    # comparison table, with the no-tools baseline pulled in where a label matches
    nt = {}
    gen_path = out_dir / "gen__summary.json"
    if gen_path.exists():
        for m in json.loads(gen_path.read_text(encoding="utf-8"))["models"]:
            nt[m["model"]] = m

    def baseline(label: str):
        key = "claude-" + label.replace("opus-", "opus-").replace(".", "-")  # opus-4.8 -> claude-opus-4-8
        return nt.get(key) or nt.get(label)

    print(f"\nGraded {len(summaries)} run(s) on {len(gold)} verified items "
          f"(answers from {rdir}):\n")
    hdr = f"{'model (label)':22}{'answered':>9}{'exact':>8}{'grade':>8}{'no-tools grade':>16}{'lift':>9}"
    print(hdr); print("-" * len(hdr))
    for s in summaries:
        b = baseline(s["model"])
        bg = b["mean_grade"] if b else None
        delta = f"{s['mean_grade'] - bg:+.3f}" if bg is not None else "n/a"
        print(f"{s['model']:22}{s['answered']:>9}{s['exact_accuracy']:>8.3f}{s['mean_grade']:>8.3f}"
              f"{(f'{bg:.3f}' if bg is not None else 'n/a'):>16}{delta:>9}")
    print(f"\nWrote {out_dir / (args.run_id + '__summary.json')} (+ per-label rows).")
    print("'no-tools grade' is the same model's score in the API no-tools 'gen' run, when the "
          "label maps to it (e.g. opus-4.8 -> claude-opus-4-8).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
