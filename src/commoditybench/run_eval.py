"""CLI: run one or more models over a dataset, score them, and write results.

Examples
--------
    # List enrolled models
    commoditybench --list-models

    # Evaluate two models on the verified set, 8 concurrent calls each
    commoditybench --dataset data/questions.jsonl \\
        --models claude-opus-4-8 gpt-4o --verified-only --workers 8

    # A/B the RAG condition (requires the rag extra + a built index)
    commoditybench --dataset data/questions.jsonl --models claude-opus-4-8 --rag

Outputs (under ``results/`` by default):
    - ``<run_id>__<model>.jsonl``  : per-question predictions + scores
    - ``<run_id>__summary.json``   : aggregate metrics per model
"""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from pathlib import Path

from .dataset import Question, load_questions
from .eccn import score_prediction
from .models import build_model, available_models


def _evaluate_model(
    model_name: str,
    questions: list[Question],
    *,
    workers: int,
    retriever=None,
    out_dir: Path,
    run_id: str,
) -> dict:
    model = build_model(model_name)
    rows: list[dict] = []

    def work(q: Question) -> dict:
        context = retriever.retrieve(q) if retriever is not None else None
        pred = model.classify(q, context=context)
        score = score_prediction(pred.predicted_eccn, q.gold_eccn)
        return {
            "id": q.id,
            "item_name": q.item_name,
            "gold_eccn": q.gold_eccn,
            "predicted_eccn": pred.predicted_eccn,
            "category": q.category,
            "verified": q.verified,
            "reasoning": pred.reasoning,
            "parsed_ok": pred.parsed_ok,
            "error": pred.error,
            "usage": pred.usage,
            "score": score.to_dict(),
        }

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(work, q): q for q in questions}
        for i, fut in enumerate(as_completed(futures), 1):
            rows.append(fut.result())
            print(f"  [{model_name}] {i}/{len(questions)}", end="\r", file=sys.stderr)
    print(file=sys.stderr)

    rows.sort(key=lambda r: r["id"])
    out_path = out_dir / f"{run_id}__{model_name}.jsonl"
    with out_path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")

    return _aggregate(model_name, rows)


def _aggregate(model_name: str, rows: list[dict]) -> dict:
    n = len(rows)
    errors = sum(1 for r in rows if r["error"])
    scored = [r["score"] for r in rows if not r["error"]]
    n_scored = len(scored) or 1  # avoid div-by-zero in an all-error run

    def rate(key: str) -> float:
        return round(sum(1 for s in scored if s[key]) / n_scored, 4)

    return {
        "model": model_name,
        "n": n,
        "errors": errors,
        "exact_accuracy": rate("exact_match"),
        "eccn_accuracy": rate("eccn_match"),  # ignores subparagraph
        "group_accuracy": rate("group_match"),  # category + product group
        "category_accuracy": rate("category_match"),
        "parse_rate": rate("parsed"),
        "mean_grade": round(sum(s["grade"] for s in scored) / n_scored, 4),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="commoditybench", description=__doc__)
    parser.add_argument("--dataset", help="Path to a .jsonl dataset file.")
    parser.add_argument(
        "--models", nargs="+", help="Model names to evaluate (see --list-models)."
    )
    parser.add_argument("--out-dir", default="results", help="Where to write results.")
    parser.add_argument("--run-id", default="run", help="Prefix for output filenames.")
    parser.add_argument("--workers", type=int, default=4, help="Concurrent calls/model.")
    parser.add_argument(
        "--verified-only",
        action="store_true",
        help="Only score human-verified questions (required for headline metrics).",
    )
    parser.add_argument(
        "--rag",
        action="store_true",
        help="Inject retrieved CCL excerpts (requires the 'rag' extra + a built index).",
    )
    parser.add_argument(
        "--list-models", action="store_true", help="List enrolled models and exit."
    )
    args = parser.parse_args(argv)

    if args.list_models:
        print("\n".join(available_models()))
        return 0

    if not args.dataset or not args.models:
        parser.error("--dataset and --models are required (or use --list-models).")

    # Load .env if present so keys come through without manual export.
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass

    questions = load_questions(args.dataset, verified_only=args.verified_only)
    if not questions:
        print(
            "No questions loaded. If you used --verified-only, note that the bundled "
            "example set is intentionally unverified — see data/schema.md.",
            file=sys.stderr,
        )
        return 1

    retriever = None
    if args.rag:
        from .rag.retriever import CCLRetriever  # lazy: optional dependency

        retriever = CCLRetriever()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(
        f"Evaluating {len(args.models)} model(s) on {len(questions)} question(s)"
        f"{' [RAG]' if args.rag else ''}.",
        file=sys.stderr,
    )
    summaries = []
    for model_name in args.models:
        summaries.append(
            _evaluate_model(
                model_name,
                questions,
                workers=args.workers,
                retriever=retriever,
                out_dir=out_dir,
                run_id=args.run_id,
            )
        )

    summary_path = out_dir / f"{args.run_id}__summary.json"
    summary_path.write_text(json.dumps(summaries, indent=2), encoding="utf-8")
    _print_table(summaries)
    print(f"\nWrote per-question results and {summary_path}", file=sys.stderr)
    return 0


def _print_table(summaries: list[dict]) -> None:
    cols = [
        ("model", "model", 22),
        ("n", "n", 5),
        ("exact_accuracy", "exact", 7),
        ("eccn_accuracy", "eccn", 7),
        ("group_accuracy", "group", 7),
        ("category_accuracy", "cat", 7),
        ("mean_grade", "grade", 7),
        ("errors", "err", 5),
    ]
    header = "".join(f"{label:<{w}}" for _, label, w in cols)
    print("\n" + header)
    print("-" * len(header))
    for s in summaries:
        print("".join(f"{str(s[key]):<{w}}" for key, _, w in cols))


if __name__ == "__main__":
    raise SystemExit(main())
