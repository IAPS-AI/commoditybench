"""Aggregate CommodityBench results across ALL runs to reduce per-run stochastic noise.

For each (model, condition) we pool every run that scored it on the verified set, treating
each run as a repeated measurement. Per item we average the score across runs; then we
average across items. This denoises models that were run many times (Opus 4.8: 5 no-tools
runs, 3 agentic runs) and reports how many runs/observations back each cell.

Also derives the error taxonomy used by the site's mistake analysis (over- vs under-control,
wrong subparagraph, wrong entry, wrong category) from predicted-vs-gold, pooled the same way.

Output: dashboard/site_data.json — consumed by build_results_site.py.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"

# Which run-ids feed each condition. A run contributes a model only if its jsonl exists.
# All listed runs are verified-only or include the verified items (we filter to verified).
BASELINE_RUNS = ["ab_baseline", "ab2_baseline", "comparison", "expanded", "gen",
                 "qwen3_32b_runpod", "frontier"]
AGENTIC_RUNS = ["ab_agentic", "ab2_agentic", "expanded_agentic", "frontier_agentic"]

MODEL_META = {
    "claude-opus-4-1": ("Claude Opus 4.1", "Anthropic", "closed", "2025-08-05"),
    "claude-opus-4-5": ("Claude Opus 4.5", "Anthropic", "closed", "2025-11-24"),
    "claude-opus-4-6": ("Claude Opus 4.6", "Anthropic", "closed", "2026-02-04"),
    "claude-opus-4-7": ("Claude Opus 4.7", "Anthropic", "closed", "2026-04-14"),
    "claude-opus-4-8": ("Claude Opus 4.8", "Anthropic", "closed", "2026-05-28"),
    "gpt-4o": ("GPT-4o", "OpenAI", "closed", "2024-05-13"),
    "gpt-5.5": ("GPT-5.5", "OpenAI", "closed", "2026-04-23"),
    "qwen3-32b": ("Qwen3-32B", "Alibaba", "open", "2025-04-28"),
    "qwen3-235b": ("Qwen3-235B-A22B", "Alibaba", "open", "2025-07-21"),
}
CATEGORY_NAMES = {
    "0": "Nuclear", "1": "Materials & Chemicals", "2": "Materials Processing",
    "3": "Electronics", "4": "Computers", "5": "Telecom & Info-Security",
    "6": "Sensors & Lasers", "7": "Navigation & Avionics", "8": "Marine",
    "9": "Aerospace & Propulsion", "EAR99": "EAR99 (not listed)",
}


def load(run, model):
    p = RESULTS / f"{run}__{model}.jsonl"
    if not p.exists():
        return None
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def models_in(runs):
    found = set()
    for run in runs:
        for p in RESULTS.glob(f"{run}__*.jsonl"):
            found.add(p.name[len(run) + 2:-6])
    return found


def aggregate_cell(model, runs):
    """Pool all runs for (model); return per-item mean scores over verified items."""
    per_item = defaultdict(list)   # qid -> [score dict, ...] across runs
    item_meta = {}                 # qid -> {item_name, category, gold}
    run_grades = []                # run-level mean grade (for spread)
    used_runs = []
    for run in runs:
        rows = load(run, model)
        if not rows:
            continue
        vrows = [r for r in rows if r["verified"]]
        if not vrows:
            continue
        used_runs.append(run)
        gsum = 0.0
        for r in vrows:
            per_item[r["id"]].append(r)
            gsum += 0 if r["error"] else r["score"]["grade"]
            item_meta[r["id"]] = {"item_name": r["item_name"],
                                  "category": r["category"], "gold": r["gold_eccn"]}
        run_grades.append(round(gsum / len(vrows), 4))
    if not per_item:
        return None
    # Per-item mean across runs (errors score 0); then mean across items.
    n_items = len(per_item)
    exact = grade = cat = eccn = group = 0.0
    obs = 0
    tool_calls_total, tool_rows = 0, 0
    for rs in per_item.values():
        for r in rs:
            tc = r.get("usage", {}).get("tool_calls") if isinstance(r.get("usage"), dict) else None
            if tc is not None:
                tool_calls_total += len(tc); tool_rows += 1
    for qid, rs in per_item.items():
        ex = gr = ca = ec = gp = 0.0
        for r in rs:
            obs += 1
            if r["error"]:
                continue
            s = r["score"]
            ex += 1 if s["exact_match"] else 0
            gr += s["grade"]
            ca += 1 if s["category_match"] else 0
            ec += 1 if s["eccn_match"] else 0
            gp += 1 if s["group_match"] else 0
        k = len(rs)
        exact += ex / k; grade += gr / k; cat += ca / k; eccn += ec / k; group += gp / k
    name, vendor, weight, date = MODEL_META.get(model, (model, "", "", ""))
    return {
        "model": model, "name": name, "vendor": vendor, "weight": weight, "date": date,
        "exact": round(exact / n_items, 4), "grade": round(grade / n_items, 4),
        "eccn": round(eccn / n_items, 4), "group": round(group / n_items, 4),
        "category": round(cat / n_items, 4),
        "n_items": n_items, "n_runs": len(used_runs), "n_obs": obs,
        "mean_tool_calls": round(tool_calls_total / tool_rows, 1) if tool_rows else 0,
        "runs": used_runs,
        "run_grades": run_grades,
        "grade_min": min(run_grades), "grade_max": max(run_grades),
    }


# ---- Error taxonomy ----------------------------------------------------------------
def classify_mistake(gold, pred, score):
    """Bucket a single prediction vs gold into an interpretable error type."""
    if score["parsed"] is False or not pred:
        return "no_answer"
    gold_ear99 = gold.upper() == "EAR99"
    pred_ear99 = pred.upper() == "EAR99"
    if score["exact_match"]:
        return "correct"
    if gold_ear99 and not pred_ear99:
        return "over_control"          # EAR99 item pushed onto the CCL
    if not gold_ear99 and pred_ear99:
        return "under_control"         # controlled item called EAR99
    if score["eccn_match"]:
        return "wrong_subparagraph"    # right 5-char ECCN, wrong leaf
    if score["group_match"]:
        return "wrong_entry"           # right category+group, wrong number
    if score["category_match"]:
        return "wrong_control"         # right category, wrong product group/entry
    return "wrong_category"            # missed the category entirely


MISTAKE_ORDER = ["correct", "over_control", "under_control", "wrong_subparagraph",
                 "wrong_entry", "wrong_control", "wrong_category", "no_answer"]
MISTAKE_LABEL = {
    "correct": "Correct", "over_control": "Over-classified (EAR99 → controlled)",
    "under_control": "Under-classified (controlled → EAR99)",
    "wrong_subparagraph": "Right ECCN, wrong subparagraph",
    "wrong_entry": "Right group, wrong entry",
    "wrong_control": "Right category, wrong control",
    "wrong_category": "Wrong category", "no_answer": "No parseable answer",
}


def taxonomy_for(model, runs):
    counts = defaultdict(float)
    n_items = 0
    per_item = defaultdict(list)
    for run in runs:
        rows = load(run, model)
        if not rows:
            continue
        for r in rows:
            if r["verified"]:
                per_item[r["id"]].append(r)
    if not per_item:
        return None
    for qid, rs in per_item.items():
        n_items += 1
        local = defaultdict(float)
        for r in rs:
            t = "no_answer" if r["error"] else classify_mistake(
                r["gold_eccn"], r["predicted_eccn"], r["score"])
            local[t] += 1
        for t, c in local.items():
            counts[t] += c / len(rs)   # per-item fraction, so each item weighs 1
    return {"model": model, "n_items": n_items,
            "counts": {t: round(counts.get(t, 0.0), 3) for t in MISTAKE_ORDER}}


def per_category_uplift(model):
    base = {}
    for run in BASELINE_RUNS:
        rows = load(run, model)
        if not rows:
            continue
        for r in rows:
            if r["verified"]:
                base.setdefault(r["category"], []).append(0 if r["error"] else r["score"]["grade"])
    ag = {}
    for run in AGENTIC_RUNS:
        rows = load(run, model)
        if not rows:
            continue
        for r in rows:
            if r["verified"]:
                ag.setdefault(r["category"], []).append(0 if r["error"] else r["score"]["grade"])
    cats = sorted(set(base) | set(ag))
    out = []
    for c in cats:
        b = base.get(c, []); a = ag.get(c, [])
        out.append({"category": c, "name": CATEGORY_NAMES.get(c, c),
                    "n_base": len(b), "n_ag": len(a),
                    "baseline": round(sum(b) / len(b), 3) if b else None,
                    "agentic": round(sum(a) / len(a), 3) if a else None})
    return out


def main():
    baseline = []
    for m in models_in(BASELINE_RUNS):
        cell = aggregate_cell(m, BASELINE_RUNS)
        if cell:
            baseline.append(cell)
    agentic = []
    for m in models_in(AGENTIC_RUNS):
        cell = aggregate_cell(m, AGENTIC_RUNS)
        if cell:
            agentic.append(cell)
    baseline.sort(key=lambda c: c["grade"], reverse=True)
    agentic.sort(key=lambda c: c["grade"], reverse=True)

    bmap = {c["model"]: c for c in baseline}
    amap = {c["model"]: c for c in agentic}
    uplift = []
    for m in amap:
        if m in bmap:
            uplift.append({
                "model": m, "name": bmap[m]["name"], "vendor": bmap[m]["vendor"],
                "weight": bmap[m]["weight"],
                "baseline": bmap[m], "agentic": amap[m],
                "per_category": per_category_uplift(m),
            })
    uplift.sort(key=lambda u: u["agentic"]["grade"], reverse=True)

    taxonomy = {"baseline": [], "agentic": []}
    for m in models_in(BASELINE_RUNS):
        t = taxonomy_for(m, BASELINE_RUNS)
        if t:
            t.update({k: bmap[m][k] for k in ("name", "vendor", "weight")} if m in bmap else {})
            taxonomy["baseline"].append(t)
    for m in models_in(AGENTIC_RUNS):
        t = taxonomy_for(m, AGENTIC_RUNS)
        if t:
            t.update({k: amap[m][k] for k in ("name", "vendor", "weight")} if m in amap else {})
            taxonomy["agentic"].append(t)

    data = {
        "leaderboard": {"baseline": baseline, "agentic": agentic},
        "uplift": uplift,
        "taxonomy": taxonomy,
        "mistake_order": MISTAKE_ORDER, "mistake_label": MISTAKE_LABEL,
        "category_names": CATEGORY_NAMES,
        "baseline_runs": BASELINE_RUNS, "agentic_runs": AGENTIC_RUNS,
    }
    out = ROOT / "dashboard" / "site_data.json"
    out.write_text(json.dumps(data, indent=2), encoding="utf-8")
    # console summary
    print("BASELINE (no tools), pooled across runs, verified-23:")
    for c in baseline:
        print(f"  {c['name']:<20} grade={c['grade']:.3f} exact={c['exact']:.3f} "
              f"runs={c['n_runs']} obs={c['n_obs']} range=[{c['grade_min']:.2f},{c['grade_max']:.2f}]")
    print("AGENTIC (tools):")
    for c in agentic:
        print(f"  {c['name']:<20} grade={c['grade']:.3f} exact={c['exact']:.3f} runs={c['n_runs']} obs={c['n_obs']}")
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
