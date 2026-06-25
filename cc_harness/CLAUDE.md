# CommodityBench — agentic run (you are the model under test)

You are taking a benchmark. Your job is the task the US Bureau of Industry and Security
(BIS) performs: given a commodity description, determine the single **Export Control
Classification Number (ECCN)** under which it falls on the **Commerce Control List** (CCL,
Supplement No. 1 to Part 774 of the EAR) — or **EAR99** if the item is subject to the EAR
but not described by any CCL entry.

You have a tool that lets you read the actual CCL. **Do NOT classify from memory — look it
up.** This is the whole point of the test: we are measuring whether reading the list beats
reciting it.

## Rules of the test (read carefully — fairness depends on these)

- **Use ONLY `./ccl.py` for anything about the Control List.** Do not use web search, do not
  rely on ECCNs you remember, do not open any other files for CCL content. The list in
  `ccl_index.json` (via `ccl.py`) is the only sanctioned source.
- **Do not look for an answer key.** There is none in this folder, by design. Do not read
  files outside this directory, do not `cd` up into a parent project, do not grep the
  filesystem for ground truth. Classify each item on its merits using the list.
- **Answer every item yourself, one model, one pass.** Don't spawn subagents or ask another
  model. Work the items in order and don't stop for confirmation between them.
- Base the classification on the item's **technical characteristics and function**, not its
  country of origin or end use.

## The tool — `./ccl.py`

Four commands. Each prints JSON to stdout; that JSON is your tool result. Run them with
`python ccl.py …` (or `python3`).

| Command | What it does |
|---|---|
| `python ccl.py categories` | List the ten CCL categories (0–9) with entry counts. Start here to pick a category. |
| `python ccl.py outline <0-9>` | Every ECCN in a category, grouped A–E, with titles + reason for control. Shows the specific high-performance controls **and** the `x991`/`x992` catch-all / basket entries together (titled "not controlled by …", flagged `is_catchall`). |
| `python ccl.py read <ECCN>` | Full controlling text of one entry: license reqs, reason for control, and the **Items:** list with subparagraphs and numeric thresholds. Accepts a 5-char head (`5A992`) or a full ECCN (`3A001.a.5.b.2`). |
| `python ccl.py search "<free text>"` | Keyword-search the CCL by a short description of the item + its specs. Returns ranked candidate entries (no entry class is favoured). Use when unsure which entry or category applies. |

Examples:
```bash
python ccl.py categories
python ccl.py outline 3
python ccl.py search "ethernet phy transceiver 10/100"
python ccl.py read 5A991
```

## Procedure for each item (follow this order of review)

1. **Pick the most plausible category** — `ccl.py categories` and/or `ccl.py search`.
2. **Read that category's whole outline** — `ccl.py outline <c>`. Read all of it, not just the
   first hit. Note both the specific controls **and** the catch-all / basket entries.
3. **Check candidate entries against the item** — `ccl.py read <ECCN>`. An item is only
   controlled by an entry if it **meets that entry's specific thresholds**. If it falls below
   a specific entry's thresholds, check whether a catch-all/basket entry in the same category
   captures it **before** concluding EAR99 — EAR99 means *no* entry (specific or catch-all)
   describes the item.
4. **Resolve to the most specific subparagraph** the item's parameters support — read the
   entry's Items: list down to the matching leaf rather than stopping at a top-level paragraph.
5. **Classify the item as it is**, not as a category: distinguish a standalone component from
   complete equipment, and read an entry's own text to decide whether the item meets it.

When you're confident, **record your answer** (don't just print it):

```bash
python record.py --model <LABEL> --id <question-id> --eccn <ECCN> \
    --category <0-9 or EAR99> --reasoning "<one sentence citing the controlling text you read>" \
    --calls <how many ccl.py calls you made for this item>
```

`<LABEL>` is the model identity the user gives you at the start (e.g. `opus-4.8`). Use the
**same label** for every item in this session. Answers are saved outside this folder; you
won't be able to read them back, and that's intentional.

## Answer shape

One ECCN per item, as specific as the description supports (include the subparagraph when
determinable, e.g. `3A001.a.1.a`), or `EAR99`. The category is the single leading digit
(`3` for `3A001…`), or `EAR99`. Keep the reasoning to one sentence pointing at the
controlling CCL text or threshold you actually read.

## Input

`questions.jsonl` — one item per line: `{"id", "item_name", "description"}`. That's all you
get (the same input the API benchmark gives the model): no gold answer, no category hint.
Work through every line in order.
