# Frontier-model comparison (addressing the model-choice review comment)

**Status: DRAFT — Qwen3-235B agentic row pending the dedicated-pod run.**

## Why this run

A reviewer (Zoe) flagged the round-1 model choice: the benchmark pitted frontier
**Claude Opus 4.8** (reasoning + CCL tools) against a **non-frontier GPT-4o** (no reasoning,
no tools) and a **small/obscure Qwen3-32B**, and only Opus got the tools — "seeing the actual
rules it has to apply seems like a bare minimum to give it a fair go." That muddied the
narrative. This run closes the gap on both axes:

1. **OpenAI's actual best.** Replaced GPT-4o with **GPT-5.5** (OpenAI's strongest reasoning
   model on our account, released 2026-04-23, run at high reasoning effort) — the contemporary
   peer to Opus 4.8 (2026-05).
2. **A credible frontier open-weight model.** Replaced Qwen3-32B with **Qwen3-235B-A22B-
   Instruct-2507** (235B MoE, 22B active; 4-bit AWQ on a self-hosted vLLM endpoint).
3. **Equal tooling.** Every model can now run the **agentic CCL-navigation condition** (the same
   read-the-rules tools Opus 4.8 had). This required building the OpenAI/OpenAI-compatible
   agentic tool loop (Chat Completions for open-weight/vLLM endpoints; the Responses API for
   GPT-5-class reasoning models, which block tools+reasoning on Chat Completions).

All accuracy figures below are over the **23 human-verified questions** (the citable set);
errors/unparsed count as 0. "exact" = exact ECCN match; "grade" = the partial-credit ladder
(exact 1.0 / same-ECCN 0.7 / group 0.4 / category 0.2). Not equalized: each model runs in its
own strongest native config (reasoning on for Opus/GPT-5.5/Qwen3; GPT-4o is temp-0, no reasoning).

## Results (verified-23, headline)

### No tools (one-shot classification)
| Model | Vendor | exact | grade |
|---|---|---|---|
| **GPT-5.5** (reasoning) | OpenAI | **0.391** | **0.565** |
| Qwen3-235B-A22B | Alibaba (open) | 0.261 | 0.439 |
| Claude Opus 4.8 | Anthropic | 0.261 | 0.409 |
| GPT-4o (round-1) | OpenAI | 0.174 | 0.370 |
| Qwen3-32B (round-1) | Alibaba (open) | 0.000 | 0.148 |

### With CCL tools (agentic — model reads the actual rules)
| Model | exact | grade | lift vs no-tools (exact) |
|---|---|---|---|
| **GPT-5.5** | **0.609** | **0.661** | 0.391 → 0.609 |
| Claude Opus 4.8 | 0.565 | 0.648 | 0.261 → 0.565 |
| Qwen3-235B-A22B | _pending_ | _pending_ | _pending_ |

(All-34 figures, including unverified candidates, track the same ordering: GPT-5.5 no-tools
0.294/0.491, agentic 0.588/0.662; Opus 4.8 0.265/0.409 → 0.559/0.641; Qwen3-235B no-tools
0.235/0.379. All runs 0 API errors / 100% parse except where noted.)

## What this shows

- **The round-1 comparison was not "frontier vs handicapped."** With OpenAI's best model and
  equal tooling, the picture is frontier-vs-frontier: **GPT-5.5 is the strongest model tested**,
  edging Opus 4.8 both unaided and with tools. The earlier GPT-4o result understated OpenAI.
- **A real open-weight model is competitive unaided.** Qwen3-235B (0.261/0.439) matches Opus 4.8
  no-tools and far exceeds the round-1 Qwen3-32B (0.000/0.148) — the small model was the weak
  link, not open weights per se.
- **Grounding is the lever, not scale.** The biggest single gain everywhere is *reading the CCL*:
  Opus 4.8 +0.30 exact, GPT-5.5 +0.22 exact. Yet even the best model **tops out at ~0.61 exact
  with the rules in hand** — no frontier model, any vendor, reliably classifies these commodities.
  This reinforces the brief's thesis: the lever is grounding/tooling, and current models are not
  yet reliable enough for unsupervised commodity classification.

## Method / reproducibility notes

- New registry models: `gpt-5.5` (reasoning_effort=high, Responses-API agentic path), `qwen3-235b`
  (OpenAI-compatible vLLM endpoint, hermes tool parser, Chat-Completions agentic path).
- Runs: `frontier` (no-tools), `frontier_agentic` (agentic). Same 34-item dataset as `expanded`.
- The OpenAI adapter gained `reasoning_effort` handling (max_completion_tokens, no temperature)
  and `classify_agentic` (two transports). See the agentic A/B harness in `models/`.
- Qwen3-235B agentic was run on a **dedicated 2×H100 vLLM pod** after the RunPod *serverless*
  endpoint repeatedly wedged under sustained agentic load (a serverless worker-scheduling issue,
  not a code or model problem); the no-tools Qwen3-235B figures used the same AWQ checkpoint.
