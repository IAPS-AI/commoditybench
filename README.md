# CommodityBench

**A benchmark measuring how well LLMs perform commodity classification** — assigning a
commodity its correct **Export Control Classification Number (ECCN)** under the US
**Commerce Control List (CCL)**, the task performed by the Bureau of Industry and
Security (BIS).

Built by the [Institute for AI Policy and Strategy (IAPS)](https://www.iaps.ai/) to
quantify how capable current closed- and open-source models are at this task, as input
to the question of whether BIS should adopt LLM assistance for classification.

📊 **[Live results site →](https://iaps-ai.github.io/commoditybench/)** — the cross-model
leaderboard (tooled + untooled), within-model tool uplift, and mistake taxonomy.

> **Status: working benchmark.** The evaluation harness (ECCN scoring, provider adapters,
> concurrent runner) is implemented and tested (**40 passing tests, tagged `v1.0`**). The
> dataset holds **34 human-verified questions** ([`data/questions.jsonl`](data/questions.jsonl))
> spanning CCL Categories 1/2/3/5/7/9 + EAR99. Multiple closed and open models have been run
> in both a one-shot and an **agentic CCL-navigation** condition; results are summarized below
> and on the [live site](https://iaps-ai.github.io/commoditybench/). Still open: backfilling
> empty Categories 0/4/6/8, fully equalizing cross-provider reasoning settings, and the RAG
> stretch goal.

---

## What it measures

Given a commodity description, a model must return one ECCN (e.g. `3A001.a.1.a`) or
`EAR99`. Because partial correctness is genuinely useful in a classification workflow,
scoring is **graded**, not all-or-nothing:

| Level | Meaning | Default weight |
|---|---|---|
| `exact` | Exact ECCN incl. subparagraph | 1.0 |
| `eccn` | Correct `CGNNN` head, wrong/over-precise subparagraph | 0.7 |
| `group` | Correct category + product group (e.g. `3A`) | 0.4 |
| `category` | Correct category only (e.g. `3`) | 0.2 |
| `none` | No shared structure | 0.0 |

`EAR99` is its own equivalence class: confusing "not on the CCL" with a real control
number (in either direction) scores 0. The summary reports exact / eccn / group /
category accuracy and a mean graded score per model. See
[`src/commoditybench/eccn.py`](src/commoditybench/eccn.py).

## Results

Full interactive results — cross-model leaderboard, within-model tool uplift, and a mistake
taxonomy — are on the **[live site](https://iaps-ai.github.io/commoditybench/)**. Headline
numbers below are **mean grade / exact-match** over the **23 human-verified items**, pooled
across all runs of each model/condition to damp per-run noise. Each model runs in its own
strongest native config, so this is **not equalized** — a capability snapshot, not a clean
ranking.

**One-shot (no tools)**

| Model | grade | exact |
|---|---|---|
| GPT-5.5 (reasoning) | **0.57** | **0.39** |
| Claude Opus 4.5 | 0.52 | 0.39 |
| Claude Opus 4.8 | 0.42 | 0.26 |
| Qwen3-235B-A22B (open) | 0.44 | 0.26 |
| GPT-4o | 0.37 | 0.17 |
| Qwen3-32B (open) | 0.18 | 0.04 |

**With CCL tools (agentic — the model reads the actual rules before answering)**

| Model | grade | exact | lift (grade) |
|---|---|---|---|
| GPT-5.5 | **0.66** | **0.61** | +0.10 |
| Qwen3-235B-A22B | 0.62 | 0.48 | +0.18 |
| Claude Opus 4.8 | 0.62 | 0.52 | +0.20 |

Takeaways: **grounding is the biggest lever** — reading the CCL adds +0.10 to +0.20 grade,
more than any difference between models. A credible open-weight model (235B) matches the
closed frontier. And even the best model **tops out around 0.61 exact with the rules in
hand** — no model yet classifies these commodities reliably. Full write-up:
[`results/frontier_comparison_findings.md`](results/frontier_comparison_findings.md).

## Install

```bash
python -m pip install -e .            # core (Anthropic adapter included)
python -m pip install -e ".[openai]"  # add GPT
python -m pip install -e ".[gemini]"  # add Gemini
python -m pip install -e ".[all]"     # everything incl. RAG + dev tools
```

Copy `.env.example` to `.env` and add the API keys for the providers you want to run.

## Run

```bash
# List enrolled models
commoditybench --list-models

# Smoke-test the harness end-to-end on the (unverified) example data
commoditybench --dataset data/questions.example.jsonl --models claude-opus-4-8

# Real run: verified data only, multiple models, 8 concurrent calls each
commoditybench --dataset data/questions.jsonl \
  --models claude-opus-4-8 gpt-5.5 qwen3-235b \
  --verified-only --workers 8

# Agentic condition: the model navigates the CCL via tools before answering
commoditybench --dataset data/questions.jsonl \
  --models claude-opus-4-8 --agentic --verified-only --workers 4
```

Results land in `results/`: per-question predictions + scores
(`<run_id>__<model>.jsonl`) and an aggregate table (`<run_id>__summary.json`).
Regenerate the [results site](https://iaps-ai.github.io/commoditybench/) from the pooled
runs with `python scripts/aggregate_runs.py && python scripts/build_results_site.py`.

Enroll a new model by adding one line to
[`src/commoditybench/models/registry.py`](src/commoditybench/models/registry.py).
Default Anthropic model is `claude-opus-4-8` with adaptive thinking and native
structured outputs.

## Dataset

The credibility of the benchmark rests entirely on its labels, so this is the careful
part. Primary source: **manufacturer self-classifications** — real products that vendors
publish with an official ECCN — starting from
[BIS's own index of participating companies](https://www.bis.gov/licensing/classify-your-item/publicly-available-classification-information).

⚠️ **BIS does not validate those classifications** ("BIS will not validate or be
responsible for the accuracy of the classification information"). So self-classified
ECCNs are strong candidate labels that a human must confirm before they count. The
`verified` flag enforces this: `--verified-only` drops everything unconfirmed, and
**every reported number must use it**.

**Current set.** [`data/questions.jsonl`](data/questions.jsonl) holds **34 real products**,
**all `verified: true`** — each ECCN is a published self-classification confirmed by the
maintainer against its `source_url`. They span **11 distinct ECCNs plus EAR99** across CCL
Categories 1/2/3/5/7/9 (sourced from Analog Devices, Microchip, Digi-Key, Honeywell, LND,
and others). Each row carries its `source_url` and a verbatim source quote in `notes`. The
set deliberately includes hard cases — e.g. EAR99 items that invite over-classification and
catch-all entries — to probe model judgment. Distribution is still skewed toward Category 5
and EAR99, and Categories **0/4/6/8 remain empty** (next backfill target).

The bundled [`data/questions.example.jsonl`](data/questions.example.jsonl) is a separate,
fully synthetic illustrative set for exercising the harness — never a result. Full schema
and sourcing methodology: [`data/schema.md`](data/schema.md).

```bash
# Validate a dataset file and see category coverage
python scripts/build_dataset.py validate data/questions.example.jsonl
# Print a blank question record to fill in
python scripts/build_dataset.py template
```

## RAG (stretch goal)

`run_eval --rag` injects retrieved CCL excerpts into the prompt so we can A/B model
accuracy with vs. without retrieval over the Commerce Control List. The retriever and
index scaffolding live in [`src/commoditybench/rag/`](src/commoditybench/rag/); building
the index from the eCFR (15 CFR 774, Supplement No. 1) is the next concrete task.

## Layout

```
src/commoditybench/
  eccn.py            # ECCN parsing, normalization, graded scoring  (core)
  dataset.py         # Question schema + JSONL loader
  prompts.py         # provider-agnostic prompt + answer JSON schema
  run_eval.py        # CLI: run models, score, write results
  models/            # provider adapters behind one interface + registry
  ccl/               # agentic condition: parsed CCL + navigation tools the model calls
  rag/               # stretch: CCL retrieval (retriever + index builder)
data/                # schema.md + verified question set + parsed CCL index
scripts/             # build_dataset.py (validate/template), aggregate_runs.py,
                     #   build_results_site.py (regenerates the live site)
tests/               # ECCN scoring + aggregation tests (pytest)
```

## Comparability & limitations

Read before citing any cross-model number:

- **Scoring denominator.** Headline accuracy is computed over **all** questions; an API
  error or an unparseable answer counts as wrong (0). This keeps models with different
  failure rates comparable. `exact_accuracy_attempted` (non-errored only) is reported for
  diagnostics but is never the headline. `parse_rate` and `error_rate` are surfaced so you
  can see *how* a model failed, not just that it scored low.
- **Reasoning settings are not equalized across providers.** Each model runs in its own
  strongest native config: Anthropic with adaptive thinking, GPT-5.5 at `reasoning_effort=high`,
  Qwen3 in thinking mode, but GPT-4o at `temperature=0` with no reasoning budget. That is
  **not** a clean apples-to-apples comparison. Headline numbers are also **pooled across runs**
  (483 observations over 11 runs) to damp per-run stochasticity. Equalize the per-provider
  config (or sweep reasoning settings) before publishing a definitive head-to-head ranking.
- **Structured-output enforcement differs.** Anthropic and OpenAI use strict JSON-schema
  enforcement; the Gemini adapter uses best-effort `response_schema`. The base parser has a
  prose-ECCN fallback (`extract_eccn`) that takes the *first* ECCN token it finds — robust,
  but it can misread a model that argues itself out of an answer. Watch `parse_rate`.
- **Self-classification labels.** Manufacturer ECCNs are not BIS-validated (see
  [Dataset](#dataset)); `--verified-only` is mandatory for any reported number.

## Development

```bash
python -m pip install -e ".[dev]"
pytest          # ECCN scoring tests
ruff check .
```

## License

MIT — see [LICENSE](LICENSE).
