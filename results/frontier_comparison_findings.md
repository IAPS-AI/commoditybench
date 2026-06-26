# Frontier-model comparison (addressing the model-choice review comment)

## Why this run

A reviewer flagged the round-1 model choice: the benchmark pitted frontier **Claude Opus
4.8** (reasoning + CCL tools) against a **non-frontier GPT-4o** (no reasoning, no tools) and a
**small/obscure Qwen3-32B**, and only Opus got the tools — "seeing the actual rules it has to
apply seems like a bare minimum to give it a fair go." This run closes the gap on both axes:

1. **OpenAI's actual best.** Added **GPT-5.5** (OpenAI's strongest reasoning model on our
   account, released 2026-04-23, high reasoning effort) — the contemporary peer to Opus 4.8.
2. **A credible frontier open-weight model.** Added **Qwen3-235B-A22B-Instruct-2507** (235B
   MoE, 22B active; 4-bit AWQ on a self-hosted vLLM endpoint).
3. **Equal tooling.** Every model can now run the **agentic CCL-navigation condition** (the
   same read-the-rules tools Opus 4.8 had), via a new OpenAI/OpenAI-compatible agentic loop —
   the Responses API for GPT-5 reasoning models, Chat Completions for open-weight vLLM endpoints.

## Numbers

All figures are **mean grade** (partial credit: exact 1.0 / same ECCN 0.7 / product group 0.4 /
category 0.2) and **exact-match rate** over the **23 human-verified items**, **pooled across every
run** of each model/condition to damp per-run stochastic noise (errors/unparsed = 0). Not
equalized: each model runs in its own strongest native config (reasoning on for Opus/GPT-5.5/
Qwen3; GPT-4o is temp-0, no reasoning).

### No tools (one-shot classification)
| Model | Vendor | grade | exact | runs pooled |
|---|---|---|---|---|
| **GPT-5.5** (reasoning) | OpenAI | **0.565** | **0.391** | 1 |
| Claude Opus 4.5 | Anthropic | 0.517 | 0.391 | 1 |
| Claude Opus 4.6 | Anthropic | 0.504 | 0.391 | 1 |
| Claude Opus 4.7 | Anthropic | 0.487 | 0.391 | 1 |
| Claude Opus 4.1 | Anthropic | 0.461 | 0.348 | 1 |
| Qwen3-235B-A22B | Alibaba (open) | 0.439 | 0.261 | 1 |
| Claude Opus 4.8 | Anthropic | 0.416 | 0.261 | 5 |
| GPT-4o (round-1) | OpenAI | 0.370 | 0.174 | 2 |
| Qwen3-32B (round-1) | Alibaba (open) | 0.175 | 0.043 | 3 |

### With CCL tools (agentic — model reads the actual rules)
| Model | grade | exact | runs pooled | lift vs no-tools (grade) |
|---|---|---|---|---|
| **GPT-5.5** | **0.661** | **0.609** | 1 | 0.565 → 0.661 (+0.10) |
| Qwen3-235B-A22B | 0.622 | 0.478 | 1 | 0.439 → 0.622 (+0.18) |
| Claude Opus 4.8 | 0.615 | 0.522 | 3 | 0.416 → 0.615 (+0.20) |

## What this shows

- **The round-1 comparison was not "frontier vs handicapped."** With OpenAI's best model and
  equal tooling, the picture is frontier-vs-frontier: **GPT-5.5 is the strongest model tested**,
  both unaided and with tools. The earlier GPT-4o result understated OpenAI.
- **A real open-weight model is competitive.** Qwen3-235B matches Opus 4.8 unaided and, with
  tools, edges it on grade (0.622 vs 0.615) — far above the round-1 Qwen3-32B. The small model
  was the weak link, not open weights.
- **Pooling matters.** Opus 4.8 unaided spans grade 0.39–0.45 across its 5 runs (mean 0.416);
  single-run snapshots are noisy. Pooling 11 runs / 483 observations stabilizes the ranking.
- **Newer ≠ better unaided.** Across the Opus ladder, 4.8 scores *below* 4.5/4.6/4.7 without
  tools (over-classification), consistent with the cross-generation finding.
- **Grounding is the lever, not scale.** The largest single gain everywhere is reading the CCL
  (+0.10 to +0.20 grade). Yet even the best model **tops out at ~0.61 exact / ~0.66 grade with
  the rules in hand** — no frontier model, any vendor, reliably classifies these commodities.

## Reproducibility

- New registry models: `gpt-5.5` (reasoning_effort=high, Responses-API agentic path), `qwen3-235b`
  (OpenAI-compatible vLLM endpoint via `QWEN3_235B_BASE_URL`, hermes tool parser, Chat-Completions
  agentic path).
- Pooled runs (verified set): no-tools — `ab_baseline`, `ab2_baseline`, `comparison`, `expanded`,
  `gen`, `qwen3_32b_runpod`, `frontier`; agentic — `ab_agentic`, `ab2_agentic`, `expanded_agentic`,
  `frontier_agentic`. Aggregated by `scripts/aggregate_runs.py`.
- Caveat: Qwen3-235B agentic has 1 of 34 items unscored (the Piper Cat-9 item's tool context
  exceeds the model's 41k window; also the weakest-provenance Tier-C item), counted as 0.
- Qwen3-235B agentic ran on a dedicated 2×H100 vLLM pod after the RunPod *serverless* endpoint
  repeatedly wedged under sustained agentic load (a serverless scheduling issue, not code/model).
