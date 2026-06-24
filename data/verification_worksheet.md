# Verification worksheet — CommodityBench dataset

Regenerated from `data/questions.jsonl`. Status reflects the full-set verification pass: an automated agent confirmed each non-Thorlabs item's ECCN is **human-visible** on its `source_url` and **matches**. Final `verified: true` still requires your sign-off (spot-check a sample per source).

**Tiers:** VERIFIED = you confirmed it. A = Analog Devices (on the BIS list; ECCN human-visible in ADI's tool). B = human-visible but off the BIS list (Microchip tool / Digi-Key page). C = ECCN not human-visible on the source.

## Status summary

- **A (ADI, human-visible)**: 9
- **B (Digi-Key page, human-visible)**: 5
- **B (Microchip tool, human-visible)**: 7
- **C (not human-visible)**: 6
- **VERIFIED**: 2

## How to sign off (per source — spot-check a couple, then bulk-confirm)

- **ADI (Tier A, 9):** open <https://www.analog.com/en/support/view-export-classification.html>, search e.g. `AD9081BBPZ-4D4AB` (3A001.a.5.a.3), `AD7768BSTZ` (EAR99). If they match -> confirm all 9.
- **Microchip (Tier B, 7):** open <https://www.microchipdirect.com/exportcontroldata/>, search e.g. `ATECC608B-MAHDA-T` (5A992.c), `LAN8720A-CP-TR` (EAR99, corrected). -> confirm all 7.
- **Digi-Key (Tier B, 5):** open each product `source_url`, read 'Environmental & Export Classifications -> ECCN'. Distributor data — was wrong on 2 sibling Microchip parts, so check these.
- **Thorlabs (Tier C, 6):** ECCN is NOT shown on the page (backend field only). Needs an invoice (like KM100/BB1-E02) or a different human-visible source, else drop.

## Decision table

| # | ID | Item | ECCN | Tier | Source | ✅ Confirm? | Corrected ECCN | Notes |
|---|----|------|------|------|--------|:-----------:|----------------|-------|
| 1 | thorlabs-km100 | Kinematic mirror mount for 1-inch optics | `EAR99` | VERIFIED | invoice | ✅ DONE |  |  |
| 2 | thorlabs-det36a2 | Biased silicon photodetector, 350-1100 nm | `EAR99` | C (not human-visible) | thorlabs.com |  |  |  |
| 3 | thorlabs-cs165mu | 1.6 MP monochrome CMOS camera | `EAR99` | C (not human-visible) | thorlabs.com |  |  |  |
| 4 | thorlabs-bb1-e02 | 1-inch broadband dielectric mirror, 400-750 nm | `EAR99` | VERIFIED | invoice | ✅ DONE |  |  |
| 5 | thorlabs-sfl1550p | 1550 nm 40 mW external-cavity butterfly laser, PM fiber | `6A995.b.1.b` | C (not human-visible) | thorlabs.com |  |  |  |
| 6 | thorlabs-lp1550-sad2 | 1550 nm 2 mW DFB laser with isolator, SM fiber | `6A995.b.1.b` | C (not human-visible) | thorlabs.com |  |  |  |
| 7 | thorlabs-fpl1009s | 1550 nm 100 mW butterfly laser diode, SM fiber | `6A995.b.2` | C (not human-visible) | thorlabs.com |  |  |  |
| 8 | thorlabs-mx10a | Benchtop electro-optic modulator driver, 12.5 Gb/s | `5B991` | C (not human-visible) | thorlabs.com |  |  |  |
| 9 | st-stm32f407vgt6 | 32-bit ARM Cortex-M4 microcontroller, 168 MHz | `3A991.a.2` | B (Digi-Key page, human-visible) | digikey.com |  |  |  |
| 10 | espressif-esp32-wroom-32e-n4 | 2.4 GHz Wi-Fi + Bluetooth module, 4 MB flash | `5A992.c` | B (Digi-Key page, human-visible) | digikey.com |  |  |  |
| 11 | ti-am3358bzcz100 | 1 GHz ARM Cortex-A8 applications microprocessor | `5A992.c` | B (Digi-Key page, human-visible) | digikey.com |  |  |  |
| 12 | rpi-sc0668 | Quad-core ARM Cortex-A72 compute module (2 GB / 16 GB) | `5A992.c` | B (Digi-Key page, human-visible) | digikey.com |  |  |  |
| 13 | microchip-lan8720a-cp-tr | 10/100 Ethernet PHY transceiver (RMII) | `EAR99` | B (Microchip tool, human-visible) | microchipdirect.com |  |  |  |
| 14 | microchip-ksz8794cnxic-tr | Four-port managed 10/100 Ethernet switch | `EAR99` | B (Microchip tool, human-visible) | microchipdirect.com |  |  |  |
| 15 | adi-ad9361bbcz | Wideband 2x2 RF agile transceiver, 47 MHz-6 GHz | `5A991.b.1` | A (ADI, human-visible) | analog.com |  |  |  |
| 16 | adi-adf7021bcpz | Narrow-band sub-1 GHz ISM RF transceiver | `EAR99` | A (ADI, human-visible) | analog.com |  |  |  |
| 17 | lattice-ice40hx4k-tq144 | Low-power FPGA, ~3,520 logic cells | `EAR99` | B (Digi-Key page, human-visible) | digikey.com |  |  |  |
| 18 | adi-ad9081bbpz-4d4ab | Quad RF-DAC / quad RF-ADC mixed-signal front-end | `3A001.a.5.a.3` | A (ADI, human-visible) | analog.com |  |  |  |
| 19 | adi-ad9162bbcz | 6 GSPS RF digital-to-analog converter, to 5 GHz | `3A001.a.5.b.2` | A (ADI, human-visible) | analog.com |  |  |  |
| 20 | adi-adrv9009bbcz | Integrated dual-channel RF transceiver, 75 MHz-6 GHz | `5A991.b.1` | A (ADI, human-visible) | analog.com |  |  |  |
| 21 | adi-adau1452kcpz | 300 MHz 32-bit audio digital signal processor | `3A991.a.2` | A (ADI, human-visible) | analog.com |  |  |  |
| 22 | adi-adsp-sc589bbcz-4b | Dual-SHARC + ARM system-on-chip processor | `5A992.c` | A (ADI, human-visible) | analog.com |  |  |  |
| 23 | adi-maxq1061etp | Cryptographic security controller IC | `5A992.c` | A (ADI, human-visible) | analog.com |  |  |  |
| 24 | adi-ad7768bstz | 8-channel 24-bit sigma-delta ADC, 256 kSPS | `EAR99` | A (ADI, human-visible) | analog.com |  |  |  |
| 25 | microchip-pic32mz2048efm144-i-ph | 32-bit MCU with hardware crypto engine | `5A992.c` | B (Microchip tool, human-visible) | microchipdirect.com |  |  |  |
| 26 | microchip-dspic33ep512mu810-i-pf | 16-bit digital signal controller, 60 MIPS | `3A991.a.2` | B (Microchip tool, human-visible) | microchipdirect.com |  |  |  |
| 27 | microchip-rn4871-v-rm118 | Bluetooth Low Energy 4.2 radio module | `5A992.c` | B (Microchip tool, human-visible) | microchipdirect.com |  |  |  |
| 28 | microchip-atecc608b-mahda-t | Secure element / crypto authentication IC | `5A992.c` | B (Microchip tool, human-visible) | microchipdirect.com |  |  |  |
| 29 | microchip-lan8742a-cz-tr | 10/100 Ethernet PHY transceiver (RMII) | `EAR99` | B (Microchip tool, human-visible) | microchipdirect.com |  |  |  |

## Evidence (per item)

### 1. thorlabs-km100 — `EAR99`  [VERIFIED]
- **Item:** Kinematic mirror mount for 1-inch optics (Thorlabs)
- **Source:** human-review-sources/KM100-EAR99-Invoice.pdf
- **Notes:** VERIFIED by Maxwell against a purchase invoice (human-review-sources/KM100-EAR99-Invoice.pdf) listing ECCN EAR99. Caveat: the Thorlabs product page does NOT show the ECCN to a human (original value was scraped from a backend field), and Thorlabs is not on the BIS public-classification list; the invoice is the authoritative provenance.

### 2. thorlabs-det36a2 — `EAR99`  [C (not human-visible)]
- **Item:** Biased silicon photodetector, 350-1100 nm (Thorlabs)
- **Source:** https://www.thorlabs.com/item/DET36A2
- **Notes:** Source quote: product data field "eccnTL":"EAR99". Published ECCN as raw text: 'EAR99'. PENDING human verification.

### 3. thorlabs-cs165mu — `EAR99`  [C (not human-visible)]
- **Item:** 1.6 MP monochrome CMOS camera (Thorlabs)
- **Source:** https://www.thorlabs.com/item/CS165MU
- **Notes:** Source quote: product data field "eccnTL":"EAR99". Published ECCN as raw text: 'EAR99'. PENDING human verification.

### 4. thorlabs-bb1-e02 — `EAR99`  [VERIFIED]
- **Item:** 1-inch broadband dielectric mirror, 400-750 nm (Thorlabs)
- **Source:** human-review-sources/BB1-E02-EAR99-Invoice.pdf
- **Notes:** VERIFIED by Maxwell against a purchase invoice (human-review-sources/BB1-E02-EAR99-Invoice.pdf) listing ECCN EAR99. Caveat: the Thorlabs product page does NOT show the ECCN to a human (original value was scraped from a backend field), and Thorlabs is not on the BIS public-classification list; the invoice is the authoritative provenance.

### 5. thorlabs-sfl1550p — `6A995.b.1.b`  [C (not human-visible)]
- **Item:** 1550 nm 40 mW external-cavity butterfly laser, PM fiber (Thorlabs)
- **Source:** https://www.thorlabs.com/item/SFL1550P
- **Notes:** Source quote: product data field "eccnTL":"6A995.b.1.b". Published ECCN as raw text: '6A995.b.1.b'. PENDING human verification.

### 6. thorlabs-lp1550-sad2 — `6A995.b.1.b`  [C (not human-visible)]
- **Item:** 1550 nm 2 mW DFB laser with isolator, SM fiber (Thorlabs)
- **Source:** https://www.thorlabs.com/item/LP1550-SAD2
- **Notes:** Source quote: product data field "eccnTL":"6A995.b.1.b". Published ECCN as raw text: '6A995.b.1.b'. PENDING human verification.

### 7. thorlabs-fpl1009s — `6A995.b.2`  [C (not human-visible)]
- **Item:** 1550 nm 100 mW butterfly laser diode, SM fiber (Thorlabs)
- **Source:** https://www.thorlabs.com/item/FPL1009S
- **Notes:** Source quote: product data field "eccnTL":"6A995.b.2". Published ECCN as raw text: '6A995.b.2'. PENDING human verification.

### 8. thorlabs-mx10a — `5B991`  [C (not human-visible)]
- **Item:** Benchtop electro-optic modulator driver, 12.5 Gb/s (Thorlabs)
- **Source:** https://www.thorlabs.com/item/MX10A
- **Notes:** Source quote: product data field "eccnTL":"5B991". Published ECCN as raw text: '5B991'. PENDING human verification.

### 9. st-stm32f407vgt6 — `3A991.a.2`  [B (Digi-Key page, human-visible)]
- **Item:** 32-bit ARM Cortex-M4 microcontroller, 168 MHz (STMicroelectronics)
- **Source:** https://www.digikey.com/en/products/detail/stmicroelectronics/STM32F407VGT6/2747117
- **Notes:** TIER B (human-visible on the Digi-Key product page; distributor self-class). Confirmed 2026-06-24, matches. Quote: "Environmental & Export Classifications -> ECCN 3A991A2". CAVEAT: Digi-Key data was found WRONG on two sibling Microchip parts (corrected against the manufacturer), so where the maker can't be cross-checked, treat this as provisional.

### 10. espressif-esp32-wroom-32e-n4 — `5A992.c`  [B (Digi-Key page, human-visible)]
- **Item:** 2.4 GHz Wi-Fi + Bluetooth module, 4 MB flash (Espressif Systems)
- **Source:** https://www.digikey.com/en/products/detail/espressif-systems/ESP32-WROOM-32E-N4/11613125
- **Notes:** TIER B (human-visible on the Digi-Key product page; distributor self-class). Confirmed 2026-06-24, matches. Quote: "Environmental & Export Classifications -> ECCN 5A992C". CAVEAT: Digi-Key data was found WRONG on two sibling Microchip parts (corrected against the manufacturer), so where the maker can't be cross-checked, treat this as provisional.

### 11. ti-am3358bzcz100 — `5A992.c`  [B (Digi-Key page, human-visible)]
- **Item:** 1 GHz ARM Cortex-A8 applications microprocessor (Texas Instruments)
- **Source:** https://www.digikey.com/en/products/detail/texas-instruments/AM3358BZCZ100/4073874
- **Notes:** TIER B (human-visible on the Digi-Key product page; distributor self-class). Confirmed 2026-06-24, matches. Quote: "Environmental & Export Classifications -> ECCN 5A992C". CAVEAT: Digi-Key data was found WRONG on two sibling Microchip parts (corrected against the manufacturer), so where the maker can't be cross-checked, treat this as provisional.

### 12. rpi-sc0668 — `5A992.c`  [B (Digi-Key page, human-visible)]
- **Item:** Quad-core ARM Cortex-A72 compute module (2 GB / 16 GB) (Raspberry Pi)
- **Source:** https://www.digikey.com/en/products/detail/raspberry-pi/SC0668/13530939
- **Notes:** TIER B (human-visible on the Digi-Key product page; distributor self-class). Confirmed 2026-06-24, matches. Quote: "Environmental & Export Classifications -> ECCN 5A992C SC (trailing 'SC' = license-exception qualifier, not part of the ECCN)". CAVEAT: Digi-Key data was found WRONG on two sibling Microchip parts (corrected against the manufacturer), so where the maker can't be cross-checked, treat this as provisional.

### 13. microchip-lan8720a-cp-tr — `EAR99`  [B (Microchip tool, human-visible)]
- **Item:** 10/100 Ethernet PHY transceiver (RMII) (Microchip Technology)
- **Source:** https://www.microchipdirect.com/exportcontroldata/
- **Notes:** CORRECTED 5A991.b.1 -> EAR99. The 5A991.b.1 value came from Digi-Key, but Microchip's own Export Control Data tool (the manufacturer, authoritative) classifies this part as EAR99. To verify: open the source_url, search 'LAN8720A-CP-TR', read the Classification Number column. Confirmed 2026-06-24. Tool row: "Classification Number EAR99".

### 14. microchip-ksz8794cnxic-tr — `EAR99`  [B (Microchip tool, human-visible)]
- **Item:** Four-port managed 10/100 Ethernet switch (Microchip Technology)
- **Source:** https://www.microchipdirect.com/exportcontroldata/
- **Notes:** CORRECTED 5A991.b.1 -> EAR99. The 5A991.b.1 value came from Digi-Key, but Microchip's own Export Control Data tool (the manufacturer, authoritative) classifies this part as EAR99. To verify: open the source_url, search 'KSZ8794CNXIC-TR', read the Classification Number column. Confirmed 2026-06-24. Tool row: "Classification Number EAR99".

### 15. adi-ad9361bbcz — `5A991.b.1`  [A (ADI, human-visible)]
- **Item:** Wideband 2x2 RF agile transceiver, 47 MHz-6 GHz (Analog Devices)
- **Source:** https://www.analog.com/en/support/view-export-classification.html
- **Notes:** TIER A (Analog Devices is on the BIS public-classification list; ECCN is human-visible). To verify: open the source_url, search 'AD9361BBCZ' in Product Model Search, and read the US ECCN column. Confirmed 2026-06-24 on ADI's export-classification tool, value matches. ADI tool row: "AD9361BBCZ | 2 receive by 2 transmit integrated frequency... | 5A991.b.1 | 8542390090". verified=false pending maintainer sign-off.

### 16. adi-adf7021bcpz — `EAR99`  [A (ADI, human-visible)]
- **Item:** Narrow-band sub-1 GHz ISM RF transceiver (Analog Devices)
- **Source:** https://www.analog.com/en/support/view-export-classification.html
- **Notes:** TIER A (Analog Devices is on the BIS public-classification list; ECCN is human-visible). To verify: open the source_url, search 'ADF7021BCPZ' in Product Model Search, and read the US ECCN column. Confirmed 2026-06-24 on ADI's export-classification tool, value matches. ADI tool row: "ADF7021BCPZ | Narrow Band Transceiver 433/868/900 MHz | EAR99 | 8542390010". verified=false pending maintainer sign-off.

### 17. lattice-ice40hx4k-tq144 — `EAR99`  [B (Digi-Key page, human-visible)]
- **Item:** Low-power FPGA, ~3,520 logic cells (Lattice Semiconductor)
- **Source:** https://www.digikey.com/en/products/detail/lattice-semiconductor-corporation/ICE40HX4K-TQ144/3083582
- **Notes:** TIER B (human-visible on the Digi-Key product page; distributor self-class). Confirmed 2026-06-24, matches. Quote: "Environmental & Export Classifications -> ECCN EAR99". CAVEAT: Digi-Key data was found WRONG on two sibling Microchip parts (corrected against the manufacturer), so where the maker can't be cross-checked, treat this as provisional.

### 18. adi-ad9081bbpz-4d4ab — `3A001.a.5.a.3`  [A (ADI, human-visible)]
- **Item:** Quad RF-DAC / quad RF-ADC mixed-signal front-end (Analog Devices)
- **Source:** https://www.analog.com/en/support/view-export-classification.html
- **Notes:** TIER A (Analog Devices is on the BIS public-classification list; ECCN is human-visible). To verify: open the source_url, search 'AD9081BBPZ-4D4AB' in Product Model Search, and read the US ECCN column. Confirmed 2026-06-24 on ADI's export-classification tool, value matches. ADI tool row: "AD9081BBPZ-4D4AB | MxFE Quad 12G RFDAC Quad 4G RFADC 600MHz | 3A001.a.5.a.3 | 8542390050". verified=false pending maintainer sign-off.

### 19. adi-ad9162bbcz — `3A001.a.5.b.2`  [A (ADI, human-visible)]
- **Item:** 6 GSPS RF digital-to-analog converter, to 5 GHz (Analog Devices)
- **Source:** https://www.analog.com/en/support/view-export-classification.html
- **Notes:** TIER A (Analog Devices is on the BIS public-classification list; ECCN is human-visible). To verify: open the source_url, search 'AD9162BBCZ' in Product Model Search, and read the US ECCN column. Confirmed 2026-06-24 on ADI's export-classification tool, value matches. ADI tool row: "AD9162BBCZ | General Purpose 5 GHz RFDAC | 3A001.a.5.b.2 | 8542390040". verified=false pending maintainer sign-off.

### 20. adi-adrv9009bbcz — `5A991.b.1`  [A (ADI, human-visible)]
- **Item:** Integrated dual-channel RF transceiver, 75 MHz-6 GHz (Analog Devices)
- **Source:** https://www.analog.com/en/support/view-export-classification.html
- **Notes:** TIER A (Analog Devices is on the BIS public-classification list; ECCN is human-visible). To verify: open the source_url, search 'ADRV9009BBCZ' in Product Model Search, and read the US ECCN column. Confirmed 2026-06-24 on ADI's export-classification tool, value matches. ADI tool row: "ADRV9009BBCZ | Integrated Dual RF Rx/Tx/ORx | 5A991.b.1 | 8542390010". verified=false pending maintainer sign-off.

### 21. adi-adau1452kcpz — `3A991.a.2`  [A (ADI, human-visible)]
- **Item:** 300 MHz 32-bit audio digital signal processor (Analog Devices)
- **Source:** https://www.analog.com/en/support/view-export-classification.html
- **Notes:** TIER A (Analog Devices is on the BIS public-classification list; ECCN is human-visible). To verify: open the source_url, search 'ADAU1452KCPZ' in Product Model Search, and read the US ECCN column. Confirmed 2026-06-24 on ADI's export-classification tool, value matches. ADI tool row: "ADAU1452KCPZ | 300 MHz 32bit SigmaDSP Audio Processor | 3A991.a.2 | 8542310035". verified=false pending maintainer sign-off.

### 22. adi-adsp-sc589bbcz-4b — `5A992.c`  [A (ADI, human-visible)]
- **Item:** Dual-SHARC + ARM system-on-chip processor (Analog Devices)
- **Source:** https://www.analog.com/en/support/view-export-classification.html
- **Notes:** TIER A (Analog Devices is on the BIS public-classification list; ECCN is human-visible). To verify: open the source_url, search 'ADSP-SC589BBCZ-4B' in Product Model Search, and read the US ECCN column. Confirmed 2026-06-24 on ADI's export-classification tool, value matches. ADI tool row: "ADSP-SC589BBCZ-4B | ARM, 2xSHARC, dual DDR, PCIe, HPC PKG | 5A992.c | 8542310035". verified=false pending maintainer sign-off.

### 23. adi-maxq1061etp — `5A992.c`  [A (ADI, human-visible)]
- **Item:** Cryptographic security controller IC (Analog Devices)
- **Source:** https://www.analog.com/en/support/view-export-classification.html
- **Notes:** TIER A (Analog Devices is on the BIS public-classification list; ECCN is human-visible). To verify: open the source_url, search 'MAXQ1061ETP+' in Product Model Search, and read the US ECCN column. Confirmed 2026-06-24 on ADI's export-classification tool, value matches. ADI tool row: "MAXQ1061ETP+ | DeepCover Cryptographic Controller | 5A992.c | 8542310030". verified=false pending maintainer sign-off.

### 24. adi-ad7768bstz — `EAR99`  [A (ADI, human-visible)]
- **Item:** 8-channel 24-bit sigma-delta ADC, 256 kSPS (Analog Devices)
- **Source:** https://www.analog.com/en/support/view-export-classification.html
- **Notes:** TIER A (Analog Devices is on the BIS public-classification list; ECCN is human-visible). To verify: open the source_url, search 'AD7768BSTZ' in Product Model Search, and read the US ECCN column. Confirmed 2026-06-24 on ADI's export-classification tool, value matches. ADI tool row: "AD7768BSTZ | 256ksps 8 ch wideband 24B SD-ADC | EAR99 | 8542390030". verified=false pending maintainer sign-off.

### 25. microchip-pic32mz2048efm144-i-ph — `5A992.c`  [B (Microchip tool, human-visible)]
- **Item:** 32-bit MCU with hardware crypto engine (Microchip Technology)
- **Source:** https://www.microchipdirect.com/exportcontroldata/
- **Notes:** TIER B (human-visible; Microchip is not on the BIS list). To verify: open the source_url, search 'PIC32MZ2048EFM144-I/PH', read the Classification Number column. Confirmed 2026-06-24, matches. Tool row: "Classification Number 5A992.c | CCATS G185380 | NLR | 740.17(b)(1)".

### 26. microchip-dspic33ep512mu810-i-pf — `3A991.a.2`  [B (Microchip tool, human-visible)]
- **Item:** 16-bit digital signal controller, 60 MIPS (Microchip Technology)
- **Source:** https://www.microchipdirect.com/exportcontroldata/
- **Notes:** TIER B (human-visible; Microchip is not on the BIS list). To verify: open the source_url, search 'DSPIC33EP512MU810-I/PF', read the Classification Number column. Confirmed 2026-06-24, matches. Tool row: "Classification Number 3A991.a.2 | NLR".

### 27. microchip-rn4871-v-rm118 — `5A992.c`  [B (Microchip tool, human-visible)]
- **Item:** Bluetooth Low Energy 4.2 radio module (Microchip Technology)
- **Source:** https://www.microchipdirect.com/exportcontroldata/
- **Notes:** TIER B (human-visible; Microchip is not on the BIS list). To verify: open the source_url, search 'RN4871-V/RM118', read the Classification Number column. Confirmed 2026-06-24, matches. Tool row: "Classification Number 5A992.c | NLR | 740.17(b)(1)".

### 28. microchip-atecc608b-mahda-t — `5A992.c`  [B (Microchip tool, human-visible)]
- **Item:** Secure element / crypto authentication IC (Microchip Technology)
- **Source:** https://www.microchipdirect.com/exportcontroldata/
- **Notes:** TIER B (human-visible; Microchip is not on the BIS list). To verify: open the source_url, search 'ATECC608B-MAHDA-T', read the Classification Number column. Confirmed 2026-06-24, matches. Tool row: "Classification Number 5A992.c | NLR | 740.17(b)(1)".

### 29. microchip-lan8742a-cz-tr — `EAR99`  [B (Microchip tool, human-visible)]
- **Item:** 10/100 Ethernet PHY transceiver (RMII) (Microchip Technology)
- **Source:** https://www.microchipdirect.com/exportcontroldata/
- **Notes:** TIER B (human-visible; Microchip is not on the BIS list). To verify: open the source_url, search 'LAN8742A-CZ-TR', read the Classification Number column. Confirmed 2026-06-24, matches. Tool row: "Classification Number EAR99 | NLR".
