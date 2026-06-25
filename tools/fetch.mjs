#!/usr/bin/env node
// fetch.mjs — Playwright-based web fetcher for 403-resistant scraping
// Usage: node fetch.mjs <url> [--selector "css selector"] [--wait ms]
//
// Outputs clean text content of the page (or selected element).
// Falls back to raw page text if selector not found.

import { chromium } from "playwright";

const args = process.argv.slice(2);
if (args.length === 0) {
  console.error("Usage: node fetch.mjs <url> [--selector 'css'] [--wait ms]");
  process.exit(1);
}

const url = args[0];
let selector = null;
let waitMs = 3000;

for (let i = 1; i < args.length; i++) {
  if (args[i] === "--selector" && args[i + 1]) selector = args[++i];
  if (args[i] === "--wait" && args[i + 1]) waitMs = parseInt(args[++i], 10);
}

async function fetchPage() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    userAgent:
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    viewport: { width: 1280, height: 800 },
  });
  const page = await context.newPage();

  try {
    await page.goto(url, { waitUntil: "domcontentloaded", timeout: 30000 });
    await page.waitForTimeout(waitMs);

    let text;
    if (selector) {
      const el = await page.$(selector);
      text = el
        ? await el.innerText()
        : await page.locator("body").innerText();
    } else {
      text = await page.locator("body").innerText();
    }

    // Collapse excessive whitespace but keep paragraph breaks
    text = text
      .split("\n")
      .map((l) => l.trim())
      .filter((l, i, arr) => !(l === "" && arr[i - 1] === ""))
      .join("\n")
      .trim();

    console.log(text);
  } catch (err) {
    console.error(`Error fetching ${url}: ${err.message}`);
    process.exit(1);
  } finally {
    await browser.close();
  }
}

fetchPage();
