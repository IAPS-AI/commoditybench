"""Build the CommodityBench results site (3 sections: leaderboard, tool uplift, mistakes).

Reads the pooled aggregates from aggregate_runs.py (dashboard/site_data.json), gathers
per-question example rows (predictions + reasoning + tool traces) for the mistake explorer,
and injects everything into results_template.html -> dashboard/index.html.

    py -3.12 scripts/aggregate_runs.py        # refresh the pooled stats first
    py -3.12 scripts/build_results_site.py
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from aggregate_runs import classify_mistake, CATEGORY_NAMES  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
HERE = Path(__file__).resolve().parent
TEMPLATE = HERE / "results_template.html"
GRADE_WEIGHTS = {"exact": 1.0, "eccn": 0.7, "group": 0.4, "category": 0.2, "none": 0.0}

# One representative run per (model, condition) for the example explorer (predictions +
# reasoning + tool traces). Pooled stats live in site_data.json; examples need single rows.
BASELINE_SRC = {
    "claude-opus-4-8": "expanded", "gpt-4o": "expanded", "qwen3-32b": "expanded",
    "gpt-5.5": "frontier", "qwen3-235b": "frontier",
    # The `gen` ladder (Opus 4.1-4.7) is deliberately absent: it's excluded from the
    # leaderboard (see aggregate_runs.py) and its frozen rows are never re-scored after
    # gold corrections, so loading them here would overwrite qmeta with stale golds.
}
AGENTIC_SRC = {
    "claude-opus-4-8": "expanded_agentic", "gpt-5.5": "frontier_agentic",
    "qwen3-235b": "frontier_agentic",
}
EXPLORER_MODELS = ["claude-opus-4-8", "gpt-5.5", "qwen3-235b"]  # models with both conditions


def load(run, model):
    p = RESULTS / f"{run}__{model}.jsonl"
    if not p.exists():
        return None
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def _row_view(r):
    """Trim a per-question row to what the explorer renders."""
    mistake = "no_answer" if r["error"] else classify_mistake(
        r["gold_eccn"], r["predicted_eccn"], r["score"])
    tools = [c.get("tool") for c in r["usage"].get("tool_calls", [])] if isinstance(r["usage"], dict) else []
    return {
        "pred": r["predicted_eccn"] or "—",
        "level": r["score"]["level"] if not r["error"] else "error",
        "grade": 0 if r["error"] else r["score"]["grade"],
        "mistake": mistake,
        "reasoning": (r.get("reasoning") or "")[:700],
        "n_tools": len(tools), "tools": tools,
        "error": bool(r["error"]),
    }


def build_examples():
    """Per verified question: gold + each explorer model's baseline & agentic prediction."""
    # index baseline + agentic rows by (model, qid)
    base_idx, ag_idx, qmeta = {}, {}, {}
    for m, run in BASELINE_SRC.items():
        for r in (load(run, m) or []):
            if r["verified"]:
                base_idx[(m, r["id"])] = r
                qmeta[r["id"]] = {"item_name": r["item_name"], "category": r["category"],
                                  "gold": r["gold_eccn"]}
    for m, run in AGENTIC_SRC.items():
        for r in (load(run, m) or []):
            if r["verified"]:
                ag_idx[(m, r["id"])] = r
    examples = []
    for qid, meta in sorted(qmeta.items(),
                            key=lambda kv: (kv[1]["category"] == "EAR99", kv[1]["category"], kv[0])):
        models = {}
        for m in EXPLORER_MODELS:
            entry = {}
            if (m, qid) in base_idx:
                entry["baseline"] = _row_view(base_idx[(m, qid)])
            if (m, qid) in ag_idx:
                entry["agentic"] = _row_view(ag_idx[(m, qid)])
            if entry:
                models[m] = entry
        examples.append({"id": qid, **meta, "models": models})
    return examples


def curate(examples):
    """Pick one representative item per error type (by the with-tools predictions), so the
    section leads with a compact, type-covering set instead of all 23 items at once."""
    targets = ["over_control", "under_control", "wrong_subparagraph", "wrong_entry",
               "wrong_control", "wrong_category", "correct"]
    chosen, used = [], set()
    for t in targets:
        for ex in examples:
            if ex["id"] in used:
                continue
            ag = [m["agentic"]["mistake"] for m in ex["models"].values() if "agentic" in m]
            if t in ag:
                chosen.append(ex["id"]); used.add(ex["id"]); break
    return chosen


def main():
    data_path = ROOT / "dashboard" / "site_data.json"
    agg = json.loads(data_path.read_text(encoding="utf-8"))

    # count distinct runs pooled (for the masthead)
    all_runs = set(agg["baseline_runs"]) | set(agg["agentic_runs"])
    runs_present = sorted({p.name.split("__")[0] for p in RESULTS.glob("*__*.jsonl")
                           if p.name.split("__")[0] in all_runs})
    n_obs = sum(c["n_obs"] for c in agg["leaderboard"]["baseline"]) + \
        sum(c["n_obs"] for c in agg["leaderboard"]["agentic"])

    data = {
        "generated": date.today().isoformat(),
        "meta": {
            "n_models_baseline": len(agg["leaderboard"]["baseline"]),
            "n_models_agentic": len(agg["leaderboard"]["agentic"]),
            "n_runs": len(runs_present), "runs": runs_present,
            "n_verified": agg["leaderboard"]["baseline"][0]["n_items"] if agg["leaderboard"]["baseline"] else 0,
            "n_obs": n_obs,
        },
        "leaderboard": agg["leaderboard"],
        "uplift": agg["uplift"],
        "taxonomy": agg["taxonomy"],
        "mistake_order": agg["mistake_order"],
        "mistake_label": agg["mistake_label"],
        "category_names": CATEGORY_NAMES,
        "grade_weights": GRADE_WEIGHTS,
        "examples": build_examples(),
    }
    data["curated"] = curate(data["examples"])
    html = TEMPLATE.read_text(encoding="utf-8").replace(
        "/*__DATA__*/", json.dumps(data, ensure_ascii=False))
    out = ROOT / "dashboard" / "index.html"
    out.write_text(html, encoding="utf-8")
    print(f"Wrote {out}  ({data['meta']['n_runs']} runs pooled, {n_obs} observations, "
          f"{len(data['examples'])} example items)")


if __name__ == "__main__":
    main()
