# cc_harness — run the agentic benchmark on a Claude subscription

Run the **agentic (read-the-CCL) condition through Claude Code** on your Max subscription
instead of paying for API tokens. You switch models in `/model`, paste one prompt, and the
model classifies all 23 verified items by reading the Commerce Control List via `ccl.py`.
Answers are saved **outside** this folder; you grade them back in the repo against ground
truth (which never lives here).

## What's in here

| File | Role |
|---|---|
| `CLAUDE.md` | The system prompt + tool guide. Claude Code auto-loads it, so the session *is* the model under test. |
| `ccl.py` | The CCL navigation tool as a CLI (`categories` / `outline` / `read` / `search`) — the exact tool surface the API benchmark exposes. Self-contained. |
| `ccl_index.json` | The parsed Control List (637 entries) the tool reads. No answer key. |
| `questions.jsonl` | The 23 verified items, sanitized to `{id, item_name, description}` — no gold ECCN, no category hint. |
| `record.py` | Saves one answer to `../../cc_results/<label>__answers.jsonl` (outside this folder, outside the repo). |
| `PROMPT.txt` | The kickoff prompt to paste. |

## How to run a model

```
cd cc_harness
claude                       # open Claude Code here (it loads CLAUDE.md)
/model                       # pick the model to test (e.g. Opus, Sonnet, Haiku)
```
Then paste `PROMPT.txt`, replacing `MODEL_LABEL` with a short label for the model you
selected (e.g. `opus-4.8`, `sonnet-4.6`, `haiku-4.5`). The model works through all 23 items,
reading the list and calling `record.py` for each. Repeat for each model: `/model` to switch,
paste the prompt with the new label. Each label writes its own answers file, so runs stay
separate and can't see each other.

> **Which models can you test?** Only the ones your Claude Code `/model` menu offers — in
> practice the current generation (Opus 4.8 / Sonnet 4.6 / Haiku 4.5), not the older Opus
> 4.1–4.7. So this gives the **tools** condition for current models (e.g. completing the
> Opus 4.8 tool-lift point, and a cross-tier tools comparison), not the full 4.1→4.8
> generation ladder.

## How to grade (back in the repo)

```
cd ..
PYTHONPATH=src py -3.12 scripts/grade_cc_runs.py
```
It scores every `cc_results/*__answers.jsonl` against the gold labels in
`data/questions.jsonl`, prints a table (with the matching no-tools `gen` grade and the tool
lift), and writes `results/cc_agentic__summary.json` (+ per-label rows) in the same shape as
the API runs.

## Fairness notes

- The model is told (in `CLAUDE.md`) to use **only** `ccl.py` for Control-List content — no
  web search, no classifying from memory, no hunting for an answer key, no reading outside
  this folder. Honest results depend on that; don't override it.
- Same 23 verified items and the same graded scorer as the API benchmark, so the grade is
  directly comparable to the no-tools `gen` run and the API agentic A/B.
- `cc_results/` lives outside this folder and outside the repo, so a later run here can't read
  an earlier run's answers, and no ground truth sits next to the questions.
