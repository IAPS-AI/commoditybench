"""Generate the CommodityBench results website (self-contained, offline-capable).

Ingests TWO runs and derives everything the site shows:
  - a cross-model NO-TOOL run (default: run-id ``expanded``) — the capability snapshot
  - a within-model AGENTIC run (default: run-id ``expanded_agentic``) — the tool lift

Metrics are computed from the per-question rows (not just the summary) so the site can
show both the full-dataset and verified-only slices, per-category lift, and per-question
detail with the agent's CCL tool-trace. Output is a single static ``dashboard/index.html``
with the data embedded (works via ``file://``; fonts come from Google Fonts with system
fallbacks).

    PYTHONPATH=src py -3.12 scripts/build_site.py \
        --crossmodel results/expanded__summary.json \
        --agentic    results/expanded_agentic__summary.json
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
TEMPLATE = HERE / "site_template.html"

GRADE_WEIGHTS = {"exact": 1.0, "eccn": 0.7, "group": 0.4, "category": 0.2, "none": 0.0}
LEVELS = ["exact", "eccn", "group", "category", "none"]

MODEL_META = {
    "claude-opus-4-8": {"name": "Claude Opus 4.8", "vendor": "Anthropic",
                        "mode": "adaptive thinking", "weight": "frontier"},
    "gpt-4o": {"name": "GPT-4o", "vendor": "OpenAI", "mode": "temp 0",
               "weight": "frontier"},
    "qwen3-32b": {"name": "Qwen3-32B", "vendor": "Alibaba (open weights)",
                  "mode": "thinking, RunPod", "weight": "open"},
}

CATEGORY_NAMES = {
    "0": "Nuclear", "1": "Materials & Chemicals", "2": "Materials Processing",
    "3": "Electronics", "4": "Computers", "5": "Telecom & Info-Security",
    "6": "Sensors & Lasers", "7": "Navigation & Avionics", "8": "Marine",
    "9": "Aerospace & Propulsion", "EAR99": "EAR99 (not listed)",
}

# The Opus generation ladder for the across-generations (METR-style) trendline. Dates are
# the Anthropic Models API ``created_at`` (the trendline x-axis). Keep in sync with the
# ladder in models/registry.py and scripts/build_generation_trendline.py.
GEN_LADDER = {
    "claude-opus-4-1": ("Opus 4.1", "2025-08-05", "Aug 2025"),
    "claude-opus-4-5": ("Opus 4.5", "2025-11-24", "Nov 2025"),
    "claude-opus-4-6": ("Opus 4.6", "2026-02-04", "Feb 2026"),
    "claude-opus-4-7": ("Opus 4.7", "2026-04-14", "Apr 2026"),
    "claude-opus-4-8": ("Opus 4.8", "2026-05-28", "May 2026"),
}


def _rows(results_dir: Path, run_id: str, model: str) -> list[dict]:
    p = results_dir / f"{run_id}__{model}.jsonl"
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def _metrics(rows: list[dict]) -> dict:
    """Headline metrics over a row list (errors/unparsed count as 0 — same as the harness)."""
    n = len(rows) or 1
    errors = sum(1 for r in rows if r["error"])
    def rate(key: str) -> float:
        return round(sum(1 for r in rows if not r["error"] and r["score"][key]) / n, 4)
    grade = round(sum(r["score"]["grade"] for r in rows if not r["error"]) / n, 4)
    ladder = {lvl: sum(1 for r in rows if not r["error"] and r["score"]["level"] == lvl)
              for lvl in LEVELS}
    ladder["error"] = errors
    return {
        "n": len(rows), "errors": errors,
        "exact": rate("exact_match"), "eccn": rate("eccn_match"),
        "group": rate("group_match"), "category": rate("category_match"),
        "parse": rate("parsed"), "grade": grade, "ladder": ladder,
    }


def _split(rows: list[dict]) -> dict:
    return {
        "all": _metrics(rows),
        "verified": _metrics([r for r in rows if r["verified"]]),
        "unverified": _metrics([r for r in rows if not r["verified"]]),
    }


def _per_category(base: list[dict], ag: list[dict]) -> list[dict]:
    by = {}
    bidx = {r["id"]: r for r in base}
    for r in ag:
        c = r["category"]
        b = bidx[r["id"]]
        d = by.setdefault(c, {"n": 0, "bg": 0.0, "ag": 0.0})
        d["n"] += 1
        d["bg"] += 0 if b["error"] else b["score"]["grade"]
        d["ag"] += 0 if r["error"] else r["score"]["grade"]
    out = []
    for c, d in by.items():
        out.append({"cat": c, "name": CATEGORY_NAMES.get(c, c), "n": d["n"],
                    "base_grade": round(d["bg"] / d["n"], 3),
                    "ag_grade": round(d["ag"] / d["n"], 3)})
    return sorted(out, key=lambda x: (x["cat"] == "EAR99", x["cat"]))


def _generations(results_dir: Path, gen_summary: Path | None) -> list[dict]:
    """Per-generation metrics for the across-generations trendline (verified set).

    Returns [] when the run isn't present so the section degrades out cleanly. The tools
    (agentic) half is intentionally absent — it's run separately once credits allow.
    """
    if not gen_summary or not gen_summary.exists():
        return []
    report = json.loads(gen_summary.read_text(encoding="utf-8"))
    run_id = report["run_id"]
    out = []
    for m in report["models"]:
        model = m["model"]
        if model not in GEN_LADDER:
            continue
        label, released, released_label = GEN_LADDER[model]
        out.append({
            "model": model, "label": label,
            "released": released, "released_label": released_label,
            "metrics": _metrics(_rows(results_dir, run_id, model)),
        })
    out.sort(key=lambda g: g["released"])
    return out


def build(crossmodel_summary: Path, agentic_summary: Path, out_path: Path,
          generations_summary: Path | None = None) -> None:
    results_dir = crossmodel_summary.parent
    cm = json.loads(crossmodel_summary.read_text(encoding="utf-8"))
    ag_report = json.loads(agentic_summary.read_text(encoding="utf-8"))
    cm_run, ag_run = cm["run_id"], ag_report["run_id"]
    ag_model = ag_report["models"][0]["model"]  # the agentic model (claude)

    cm_rows = {m["model"]: _rows(results_dir, cm_run, m["model"]) for m in cm["models"]}
    ag_rows = _rows(results_dir, ag_run, ag_model)
    base_rows = cm_rows[ag_model]  # same model, no tools = the within-model baseline

    # Cross-model leaderboard (no tools), ranked by all-set grade.
    crossmodel = []
    for model, rows in cm_rows.items():
        meta = MODEL_META.get(model, {"name": model, "vendor": "", "mode": "", "weight": ""})
        crossmodel.append({"model": model, **meta, **{"split": _split(rows)}})
    crossmodel.sort(key=lambda m: m["split"]["all"]["grade"], reverse=True)

    # Within-model tool lift.
    toollift = {
        "model": MODEL_META[ag_model]["name"],
        "baseline": _split(base_rows),
        "agentic": _split(ag_rows),
        "per_category": _per_category(base_rows, ag_rows),
        "mean_tool_calls": round(
            sum(len(r["usage"].get("tool_calls", [])) for r in ag_rows) / (len(ag_rows) or 1), 1
        ),
    }

    # Per-question merge: gold + every model's no-tool prediction + the agentic prediction.
    bidx = {r["id"]: r for r in base_rows}
    aidx = {r["id"]: r for r in ag_rows}
    questions = []
    for r in sorted(base_rows, key=lambda x: (x["category"] == "EAR99", x["category"], x["id"])):
        qid = r["id"]
        preds = {}
        for model, rows in cm_rows.items():
            row = next((x for x in rows if x["id"] == qid), None)
            if row:
                preds[model] = {"eccn": row["predicted_eccn"] or "—",
                                "grade": row["score"]["grade"], "level": row["score"]["level"],
                                "error": bool(row["error"])}
        a = aidx[qid]
        preds[ag_model + "::agentic"] = {
            "eccn": a["predicted_eccn"] or "—", "grade": a["score"]["grade"],
            "level": a["score"]["level"], "error": bool(a["error"]),
            "tool_calls": a["usage"].get("tool_calls", []),
            "reasoning": (a.get("reasoning") or "")[:600],
        }
        questions.append({
            "id": qid, "item_name": r["item_name"], "category": r["category"],
            "gold": r["gold_eccn"], "verified": r["verified"], "preds": preds,
        })

    total = len(base_rows)
    verified = sum(1 for r in base_rows if r["verified"])
    by_cat = {}
    for r in base_rows:
        by_cat[r["category"]] = by_cat.get(r["category"], 0) + 1

    data = {
        "generated": date.today().isoformat(),
        "dataset": {"total": total, "verified": verified, "unverified": total - verified,
                    "by_category": by_cat, "category_names": CATEGORY_NAMES},
        "crossmodel": crossmodel,
        "agentic_model_key": ag_model + "::agentic",
        "model_keys": list(cm_rows.keys()),
        "model_meta": MODEL_META,
        "toollift": toollift,
        "generations": _generations(results_dir, generations_summary),
        "generations_pending_tools": True,
        "questions": questions,
        "grade_weights": GRADE_WEIGHTS,
        "equalized": False,
    }

    html = TEMPLATE.read_text(encoding="utf-8").replace("/*__DATA__*/", json.dumps(data, ensure_ascii=False))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    print(f"Wrote {out_path}  ({len(crossmodel)} models, {len(questions)} questions, "
          f"tool-lift grade {toollift['baseline']['all']['grade']} -> {toollift['agentic']['all']['grade']})")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--crossmodel", default=str(ROOT / "results" / "expanded__summary.json"))
    ap.add_argument("--agentic", default=str(ROOT / "results" / "expanded_agentic__summary.json"))
    ap.add_argument("--generations", default=str(ROOT / "results" / "gen__summary.json"),
                    help="No-tools cross-generation run (run-id 'gen'); section hides if absent.")
    ap.add_argument("--out", default=str(ROOT / "dashboard" / "index.html"))
    args = ap.parse_args(argv)
    build(Path(args.crossmodel), Path(args.agentic), Path(args.out),
          generations_summary=Path(args.generations))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
