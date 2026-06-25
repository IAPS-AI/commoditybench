# tools/ — ECCN-verification helpers

Small standalone Node scripts used to vet candidate ECCN labels (next-steps item 1).
Vendored into the repo so they travel with a clone. None contain machine-specific paths.

## Setup (per machine)

```bash
npm init -y                 # if no package.json in this dir yet
npm install playwright
npx playwright install chromium      # for fetch.mjs (headless Chromium)
# adichrome.mjs additionally needs a REAL Chrome install (channel:"chrome"):
npx playwright install chrome        # or have desktop Chrome installed
```

Node 18+ (uses global `fetch` and `getSetCookie`).

## Scripts

- **fetch.mjs** — Playwright headless fetcher that bypasses most 403/WAF bot
  protection. `node tools/fetch.mjs "<url>" [--selector "css"] [--wait 6000]`.
  Prints cleaned page text. Use for JS-rendered / blocked pages.

- **mchpeccn.mjs** — hits Microchip's export-control API and prints the ECCN JSON
  for a part. `node tools/mchpeccn.mjs <PART>` (e.g. `ATTINY817-MFR`). Pure
  `fetch`, no browser. Cross-check distributor data against the manufacturer.

- **adichrome.mjs** — drives the Analog Devices export-classification search under
  the **real Chrome engine** (headless Chromium fails ADI's JS with
  `ERR_HTTP2_PROTOCOL_ERROR`). Types each part into the search box, reads the
  human-visible US ECCN cell, and cross-checks the `FetchExportClassificationData`
  XHR JSON. `node tools/adichrome.mjs <PART> [<PART> ...]`.

See the repo `CLAUDE.md` ("Environment / tooling") for context on why manufacturer
export endpoints are session/XHR-gated and why the real Chrome engine is required.
