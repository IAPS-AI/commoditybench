# CommodityBench

**A benchmark measuring how well LLMs perform commodity classification** — assigning a
commodity its correct **Export Control Classification Number (ECCN)** under the US
**Commerce Control List (CCL)**, the task performed by the Bureau of Industry and
Security (BIS).

Built by the [Institute for AI Policy and Strategy (IAPS)](https://www.iaps.ai/) to
quantify how capable current closed- and open-source models are at this task, as input
to the question of whether BIS should adopt LLM assistance for classification.

> **Status: early scaffold + candidate dataset.** The evaluation harness, ECCN scoring,
> and model adapters are implemented and tested. A first batch of **29 candidate
> questions** ([`data/questions.jsonl`](data/questions.jsonl)) has been sourced from
> manufacturer self-classifications — but **every row is `verified: false`** pending
> human confirmation against its source. Do not cite any accuracy numbers until those
> labels are verified (see [Dataset](#dataset)).

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
  --models claude-opus-4-8 gpt-4o gemini-2.0-flash \
  --verified-only --workers 8
```

Results land in `results/`: per-question predictions + scores
(`<run_id>__<model>.jsonl`) and an aggregate table (`<run_id>__summary.json`).

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

**Candidate set.** [`data/questions.jsonl`](data/questions.jsonl) holds 29 real products
sourced from vendor export-classification pages/tools (Thorlabs, Analog Devices,
Microchip, Digi-Key), spanning 8 distinct ECCNs across Categories 3/5/6 plus EAR99. Each
row carries its `source_url` and a verbatim source quote in `notes`. **All are
`verified: false`** — they are candidate labels awaiting human confirmation, not results.
Two near-identical Ethernet PHYs are deliberately flagged with conflicting published
ECCNs (a real classification edge case to resolve during verification).

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
  rag/               # stretch: CCL retrieval (retriever + index builder)
data/                # schema.md + example/verified question sets
scripts/build_dataset.py   # validate + template tooling
tests/               # ECCN scoring tests (pytest)
```

## Comparability & limitations

Read before citing any cross-model number:

- **Scoring denominator.** Headline accuracy is computed over **all** questions; an API
  error or an unparseable answer counts as wrong (0). This keeps models with different
  failure rates comparable. `exact_accuracy_attempted` (non-errored only) is reported for
  diagnostics but is never the headline. `parse_rate` and `error_rate` are surfaced so you
  can see *how* a model failed, not just that it scored low.
- **Reasoning settings are not yet equalized across providers.** The Anthropic adapter
  currently runs with adaptive thinking + `effort=high`; the OpenAI and Gemini adapters
  run at `temperature=0` with no reasoning budget. That is **not** a clean apples-to-apples
  comparison — it gives Claude a reasoning advantage. Equalize the per-provider config (or
  sweep reasoning settings) before publishing a head-to-head ranking.
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
