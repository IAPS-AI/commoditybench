# BIS-listed ECCN publishers — sourcing map

Distilled from BIS's *Commodity Classification Information* table (the official list of
companies that asked BIS to link their published ECCN information), archived at
[`../../ccats-website-table-april-2018.pdf`](../../ccats-website-table-april-2018.pdf).
Live page: <https://www.bis.gov/licensing/classify-your-item/publicly-available-classification-information>.

**Why this matters.** For a benchmark meant to inform a BIS-facing recommendation, labels
sourced from companies *on BIS's own list* carry more weight than arbitrary vendor pages.
This is the preferred starting point for dataset sourcing.

**Two hard rules learned in round 1:**
1. **Provenance must be human-checkable.** The `source_url` must actually *display* the
   ECCN to a person opening it. (Thorlabs failed this: the value lived in a backend data
   field, not on the visible page — and Thorlabs isn't on this list. Those items were
   downgraded.)
2. **Prefer companies on this list.** Off-list manufacturer pages and distributor
   aggregators (e.g. Digi-Key) are acceptable fallbacks but weaker provenance.

**Caveat (BIS's own):** BIS does *not* validate these classifications — "for informational
purposes only." They are still self-classifications that a human must confirm.

**Dating caveat:** the table is from **April 2018**. Several firms have been renamed or
acquired (Freescale→NXP, Altera→Intel, Spansion→Cypress→Infineon, Sun→Oracle, LeCroy→
Teledyne, Maxim→Analog Devices); their export pages usually still exist under the successor.

---

## By CCL category (sourcing opportunities)

Marked ✅ = already used in `data/questions.jsonl`. Bold = has a public ECCN matrix/tool.

### Cat 3 — Electronics
- **Analog Devices** ✅ — `analog.com/export` (public ECCN search tool; BIS-listed). Strongest source we have.
- **Maxim Integrated** (now ADI) — `maximintegrated.com/trade-compliance`.
- **LeCroy** (Teledyne) — oscilloscopes / T&M — `lecroy.com`. Good for controlled test equipment (3A292, 3B).
- **Vectron International** — crystals, oscillators, filters, timing — `vectron.com`.
- Cirrus Logic (`cirrus.com`), Micron (memory), NXP, AmpliTech (microwave amps), Bourns.

### Cat 4 — Computers
- **Apple** — `apple.com/legal/export.html`. **Lenovo** — `lenovo.com/.../eccn.html`.
- **HP** — `classification.austin.hp.com`. **Oracle/Sun** — `oracle.com/us/products/export/eccn-matrix-345817.html`.
- **Seagate** (storage), NetApp, Unisys.

### Cat 5 Part 1 — Telecommunications
- **Cisco** — `tools.cisco.com/legal/export/pepd/Search.do` (public part-number ECCN lookup; BIS-listed). High value for networking.
- **Brocade** (Fibre Channel/SAN), Nortel, Avaya, Plantronics, Polycom (telepresence), Opengear, Research Concepts (satellite antenna controllers).

### Cat 5 Part 2 — Information Security (encryption)
- **Fortinet** (UTM/network security), **McAfee** (`mcafee.com/.../export_compliance`), **Sourcefire** (cybersecurity).
- Adobe, Novell, Quest, Synopsys (security/encryption-bearing software).

### Cat 6 — Sensors and Lasers  *(we have lasers; need detectors/cameras)*
- **DRS Infrared** — thermal imaging — `drsinfrared.com/Support/ExportGuidelines.aspx`. Prime Cat 6A003 source.
- **Pelco** — video security cameras — `pelco.com/.../export_compliance`. Good for 6A003 cameras.
- **Southwest Microwave** — perimeter security sensors. **Syris Scientific** — vascular laser.

### Cat 7 — Navigation and Avionics  *(currently empty)*
- **Rockwell Collins** — comms & avionics — shopcollins export portal. **Avtech** — aviation electronics. **Hawker Pacific Aerospace** — landing gear.

### Cat 0 / 1 — Nuclear & Materials  *(currently empty)*
- **LND, Inc.** — nuclear radiation detectors — `lndinc.com/faq`. Rare public source for Cat 0/1A.
- Wacker (polysilicon), Poco Graphite (artificial graphite), Pacific Cast (titanium castings), Eckart (effect pigments).

### Cat 2 — Materials Processing  *(currently empty)*
- **SKF** — bearings, machine-tool spindles, magnetic bearings — `skf.com`. **Oberg** (precision mfg), **Flowserve** (valves), **Fusion UV** (UV curing systems).

### Cat 9 — Aerospace & Propulsion  *(currently empty)*
- Rockwell Collins, Hawker Pacific Aerospace (overlap with Cat 7).

### Software (3D/4D/5D)
- Adobe (`adobe.com/support/eccnmatrix.html`), Synopsys, Novell, Quest, McAfee.

---

## Round-1 source assessment

| Source used | On BIS list? | Provenance | Verdict |
|---|---|---|---|
| Analog Devices (`analog.com/exportclassification`) | **Yes** | Public export tool | **Tier A — keep**; confirm each shows on the ADI tool |
| Maxim / MAXQ1061 (via ADI) | **Yes** | Public tool | Tier A |
| Microchip (`microchipdirect` export data) | No | Public-ish tool | Tier B — usable fallback |
| Digi-Key (distributor) | No | ECCN visible on product page | Tier B — visible but distributor self-class |
| Thorlabs | No | **Not shown on page** (backend field) | Tier C — re-source or invoice-verify |

For the Digi-Key items whose *underlying maker* is BIS-listed (AD9361, ADF7021 → Analog
Devices), re-source the label from the maker's own tool to upgrade them to Tier A.
