# Verification worksheet — CommodityBench dataset

Generated from `data/questions.jsonl` by `scripts/make_worksheet.py`. The **Verify here** column links straight to each source (and gives the part to search for tool-based sources), so you can confirm in-line. Mark the **✅** column as you go, then tell the assistant which sources are confirmed and it flips `verified: true`.

**Tiers:** VERIFIED = you confirmed it. `A · ADI` = on the BIS list, ECCN human-visible in ADI's tool. `B` = human-visible but off the BIS list (Microchip tool / Digi-Key page). `C` = ECCN not human-visible on the source.

## Status: 34 VERIFIED

> **Bulk-confirm tip:** each source renders ECCNs the same way, so spot-check 2 rows per source; if they match, confirm the whole source. Any Tier C row (ECCN not human-visible on the source) needs an invoice or another human-visible source, else drop.

## Decision table

| # | Item | ECCN | Tier | Verify here | ✅ | Your notes |
|---|------|------|------|-------------|:--:|------------|
| 1 | Kinematic mirror mount for 1-inch optics | `EAR99` | VERIFIED | [invoice](human-review-sources/KM100-EAR99-Invoice.pdf) | ✅ |  |
| 2 | 1-inch broadband dielectric mirror, 400-750 nm | `EAR99` | VERIFIED | [invoice](human-review-sources/BB1-E02-EAR99-Invoice.pdf) | ✅ |  |
| 3 | 32-bit ARM Cortex-M4 microcontroller, 168 MHz | `3A991.a.2` | VERIFIED | [Digi-Key page](https://www.digikey.com/en/products/detail/stmicroelectronics/STM32F407VGT6/2747117) | ✅ |  |
| 4 | 2.4 GHz Wi-Fi + Bluetooth module, 4 MB flash | `5A992.c` | VERIFIED | [Digi-Key page](https://www.digikey.com/en/products/detail/espressif-systems/ESP32-WROOM-32E-N4/11613125) | ✅ |  |
| 5 | 1 GHz ARM Cortex-A8 applications microprocessor | `5A992.c` | VERIFIED | [Digi-Key page](https://www.digikey.com/en/products/detail/texas-instruments/AM3358BZCZ100/4073874) | ✅ |  |
| 6 | Quad-core ARM Cortex-A72 compute module (2 GB / 16 GB) | `5A992.c` | VERIFIED | [Digi-Key page](https://www.digikey.com/en/products/detail/raspberry-pi/SC0668/13530939) | ✅ |  |
| 7 | 10/100 Ethernet PHY transceiver (RMII) | `EAR99` | VERIFIED | [Microchip tool](https://www.microchipdirect.com/exportcontroldata/) → search `LAN8720A-CP-TR` | ✅ |  |
| 8 | Four-port managed 10/100 Ethernet switch | `EAR99` | VERIFIED | [Microchip tool](https://www.microchipdirect.com/exportcontroldata/) → search `KSZ8794CNXIC-TR` | ✅ |  |
| 9 | Wideband 2x2 RF agile transceiver, 47 MHz-6 GHz | `5A991.b.1` | VERIFIED | [ADI tool](https://www.analog.com/en/support/view-export-classification.html) → search `AD9361BBCZ` | ✅ |  |
| 10 | Narrow-band sub-1 GHz ISM RF transceiver | `EAR99` | VERIFIED | [ADI tool](https://www.analog.com/en/support/view-export-classification.html) → search `ADF7021BCPZ` | ✅ |  |
| 11 | Low-power FPGA, ~3,520 logic cells | `EAR99` | VERIFIED | [Digi-Key page](https://www.digikey.com/en/products/detail/lattice-semiconductor-corporation/ICE40HX4K-TQ144/3083582) | ✅ |  |
| 12 | Quad RF-DAC / quad RF-ADC mixed-signal front-end | `3A001.a.5.a.3` | VERIFIED | [ADI tool](https://www.analog.com/en/support/view-export-classification.html) → search `AD9081BBPZ-4D4AB` | ✅ |  |
| 13 | 6 GSPS RF digital-to-analog converter, to 5 GHz | `3A001.a.5.b.2` | VERIFIED | [ADI tool](https://www.analog.com/en/support/view-export-classification.html) → search `AD9162BBCZ` | ✅ |  |
| 14 | Integrated dual-channel RF transceiver, 75 MHz-6 GHz | `5A991.b.1` | VERIFIED | [ADI tool](https://www.analog.com/en/support/view-export-classification.html) → search `ADRV9009BBCZ` | ✅ |  |
| 15 | 300 MHz 32-bit audio digital signal processor | `3A991.a.2` | VERIFIED | [ADI tool](https://www.analog.com/en/support/view-export-classification.html) → search `ADAU1452KCPZ` | ✅ |  |
| 16 | Dual-SHARC + ARM system-on-chip processor | `5A992.c` | VERIFIED | [ADI tool](https://www.analog.com/en/support/view-export-classification.html) → search `ADSP-SC589BBCZ-4B` | ✅ |  |
| 17 | Cryptographic security controller IC | `5A992.c` | VERIFIED | [ADI tool](https://www.analog.com/en/support/view-export-classification.html) → search `MAXQ1061ETP+` | ✅ |  |
| 18 | 8-channel 24-bit sigma-delta ADC, 256 kSPS | `EAR99` | VERIFIED | [ADI tool](https://www.analog.com/en/support/view-export-classification.html) → search `AD7768BSTZ` | ✅ |  |
| 19 | 32-bit MCU with hardware crypto engine | `5A992.c` | VERIFIED | [Microchip tool](https://www.microchipdirect.com/exportcontroldata/) → search `PIC32MZ2048EFM144-I/PH` | ✅ |  |
| 20 | 16-bit digital signal controller, 60 MIPS | `3A991.a.2` | VERIFIED | [Microchip tool](https://www.microchipdirect.com/exportcontroldata/) → search `DSPIC33EP512MU810-I/PF` | ✅ |  |
| 21 | Bluetooth Low Energy 4.2 radio module | `5A992.c` | VERIFIED | [Microchip tool](https://www.microchipdirect.com/exportcontroldata/) → search `RN4871-V/RM118` | ✅ |  |
| 22 | Secure element / crypto authentication IC | `5A992.c` | VERIFIED | [Microchip tool](https://www.microchipdirect.com/exportcontroldata/) → search `ATECC608B-MAHDA-T` | ✅ |  |
| 23 | 10/100 Ethernet PHY transceiver (RMII) | `EAR99` | VERIFIED | [Microchip tool](https://www.microchipdirect.com/exportcontroldata/) → search `LAN8742A-CZ-TR` | ✅ |  |
| 24 | 10-DOF MEMS inertial measurement unit with on-board sensor fusion | `7A994` | VERIFIED | [ADI tool](https://www.analog.com/en/support/view-export-classification.html) → search `ADIS16480BMLZ` | ✅ |  |
| 25 | Precision 6-DOF MEMS IMU, ±2000°/s gyro range | `7A003.d.1` | VERIFIED | [ADI tool](https://www.analog.com/en/support/view-export-classification.html) → search `ADIS16545-3BMLZ` | ✅ |  |
| 26 | ±300°/s single-axis MEMS angular rate gyroscope | `7A994` | VERIFIED | [ADI tool](https://www.analog.com/en/support/view-export-classification.html) → search `ADXRS453BRGZ` | ✅ |  |
| 27 | Tactical-grade 6-DOF MEMS inertial measurement unit (~1 cubic inch) | `7A994` | VERIFIED | [page](https://www.honeywellaerospace.com/us/en/products-and-services/products/navigation-and-sensors/inertial-measurement-units/hguide-i300-mems-inertial-measurement-unit) | ✅ |  |
| 28 | Boron-trifluoride thermal neutron proportional counter | `1A999` | VERIFIED | [LND FAQ — ECCN-by-family](https://www.lndinc.com/faq/) | ✅ |  |
| 29 | Boron-10 lined thermal neutron proportional counter | `1A999` | VERIFIED | [LND FAQ — ECCN-by-family](https://www.lndinc.com/faq/) | ✅ |  |
| 30 | Helium-3 thermal neutron detector tube | `1C232` | VERIFIED | [LND FAQ — ECCN-by-family](https://www.lndinc.com/faq/) | ✅ |  |
| 31 | Bronze rotary gear pump, 23 GPM | `2B999.j` | VERIFIED | [page](https://www.motion.com/products/sku/11016143) | ✅ |  |
| 32 | Super-precision angular contact ball bearing, 15 mm bore (P4/ABEC-7) | `EAR99` | VERIFIED | [page](https://www.powelltool.com/products/7002CYDUP4-NAC) | ✅ |  |
| 33 | Aircraft access-panel cam latch (airframe hardware) | `9A991.d` | VERIFIED | [page](https://www.pilotshq.com/products/piper-aircraft-553-876-cam-latch-oem-airframe-hardware-part) | ✅ |  |
| 34 | Aircraft GPS antenna coaxial cable assembly | `9A991.d` | VERIFIED | [page](https://www.pilotshq.com/products/piper-aircraft-coax-gps-2-assembly-101918-003-oem-replacement) | ✅ |  |

## Evidence (per item)

### 1. thorlabs-km100 — `EAR99`  [VERIFIED]
- **Item:** Kinematic mirror mount for 1-inch optics (Thorlabs)
- **Source:** human-review-sources/KM100-EAR99-Invoice.pdf
- **Notes:** VERIFIED by Maxwell against a purchase invoice (human-review-sources/KM100-EAR99-Invoice.pdf) listing ECCN EAR99. Caveat: the Thorlabs product page does NOT show the ECCN to a human (original value was scraped from a backend field), and Thorlabs is not on the BIS public-classification list; the invoice is the authoritative provenance.

### 2. thorlabs-bb1-e02 — `EAR99`  [VERIFIED]
- **Item:** 1-inch broadband dielectric mirror, 400-750 nm (Thorlabs)
- **Source:** human-review-sources/BB1-E02-EAR99-Invoice.pdf
- **Notes:** VERIFIED by Maxwell against a purchase invoice (human-review-sources/BB1-E02-EAR99-Invoice.pdf) listing ECCN EAR99. Caveat: the Thorlabs product page does NOT show the ECCN to a human (original value was scraped from a backend field), and Thorlabs is not on the BIS public-classification list; the invoice is the authoritative provenance.

### 3. st-stm32f407vgt6 — `3A991.a.2`  [VERIFIED]
- **Item:** 32-bit ARM Cortex-M4 microcontroller, 168 MHz (STMicroelectronics)
- **Source:** https://www.digikey.com/en/products/detail/stmicroelectronics/STM32F407VGT6/2747117
- **Notes:** TIER B (human-visible on the Digi-Key product page; distributor self-class). Confirmed 2026-06-24, matches. Quote: "Environmental & Export Classifications -> ECCN 3A991A2". CAVEAT: Digi-Key data was found WRONG on two sibling Microchip parts (corrected against the manufacturer), so where the maker can't be cross-checked, treat this as provisional.

### 4. espressif-esp32-wroom-32e-n4 — `5A992.c`  [VERIFIED]
- **Item:** 2.4 GHz Wi-Fi + Bluetooth module, 4 MB flash (Espressif Systems)
- **Source:** https://www.digikey.com/en/products/detail/espressif-systems/ESP32-WROOM-32E-N4/11613125
- **Notes:** TIER B (human-visible on the Digi-Key product page; distributor self-class). Confirmed 2026-06-24, matches. Quote: "Environmental & Export Classifications -> ECCN 5A992C". CAVEAT: Digi-Key data was found WRONG on two sibling Microchip parts (corrected against the manufacturer), so where the maker can't be cross-checked, treat this as provisional.

### 5. ti-am3358bzcz100 — `5A992.c`  [VERIFIED]
- **Item:** 1 GHz ARM Cortex-A8 applications microprocessor (Texas Instruments)
- **Source:** https://www.digikey.com/en/products/detail/texas-instruments/AM3358BZCZ100/4073874
- **Notes:** TIER B (human-visible on the Digi-Key product page; distributor self-class). Confirmed 2026-06-24, matches. Quote: "Environmental & Export Classifications -> ECCN 5A992C". CAVEAT: Digi-Key data was found WRONG on two sibling Microchip parts (corrected against the manufacturer), so where the maker can't be cross-checked, treat this as provisional.

### 6. rpi-sc0668 — `5A992.c`  [VERIFIED]
- **Item:** Quad-core ARM Cortex-A72 compute module (2 GB / 16 GB) (Raspberry Pi)
- **Source:** https://www.digikey.com/en/products/detail/raspberry-pi/SC0668/13530939
- **Notes:** TIER B (human-visible on the Digi-Key product page; distributor self-class). Confirmed 2026-06-24, matches. Quote: "Environmental & Export Classifications -> ECCN 5A992C SC (trailing 'SC' = license-exception qualifier, not part of the ECCN)". CAVEAT: Digi-Key data was found WRONG on two sibling Microchip parts (corrected against the manufacturer), so where the maker can't be cross-checked, treat this as provisional.

### 7. microchip-lan8720a-cp-tr — `EAR99`  [VERIFIED]
- **Item:** 10/100 Ethernet PHY transceiver (RMII) (Microchip Technology)
- **Source:** https://www.microchipdirect.com/exportcontroldata/
- **Notes:** CORRECTED 5A991.b.1 -> EAR99. The 5A991.b.1 value came from Digi-Key, but Microchip's own Export Control Data tool (the manufacturer, authoritative) classifies this part as EAR99. To verify: open the source_url, search 'LAN8720A-CP-TR', read the Classification Number column. Confirmed 2026-06-24. Tool row: "Classification Number EAR99".

### 8. microchip-ksz8794cnxic-tr — `EAR99`  [VERIFIED]
- **Item:** Four-port managed 10/100 Ethernet switch (Microchip Technology)
- **Source:** https://www.microchipdirect.com/exportcontroldata/
- **Notes:** CORRECTED 5A991.b.1 -> EAR99. The 5A991.b.1 value came from Digi-Key, but Microchip's own Export Control Data tool (the manufacturer, authoritative) classifies this part as EAR99. To verify: open the source_url, search 'KSZ8794CNXIC-TR', read the Classification Number column. Confirmed 2026-06-24. Tool row: "Classification Number EAR99".

### 9. adi-ad9361bbcz — `5A991.b.1`  [VERIFIED]
- **Item:** Wideband 2x2 RF agile transceiver, 47 MHz-6 GHz (Analog Devices)
- **Source:** https://www.analog.com/en/support/view-export-classification.html
- **Notes:** TIER A (Analog Devices is on the BIS public-classification list; ECCN is human-visible). To verify: open the source_url, search 'AD9361BBCZ' in Product Model Search, and read the US ECCN column. Confirmed 2026-06-24 on ADI's export-classification tool, value matches. ADI tool row: "AD9361BBCZ | 2 receive by 2 transmit integrated frequency... | 5A991.b.1 | 8542390090". verified=false pending maintainer sign-off.

### 10. adi-adf7021bcpz — `EAR99`  [VERIFIED]
- **Item:** Narrow-band sub-1 GHz ISM RF transceiver (Analog Devices)
- **Source:** https://www.analog.com/en/support/view-export-classification.html
- **Notes:** TIER A (Analog Devices is on the BIS public-classification list; ECCN is human-visible). To verify: open the source_url, search 'ADF7021BCPZ' in Product Model Search, and read the US ECCN column. Confirmed 2026-06-24 on ADI's export-classification tool, value matches. ADI tool row: "ADF7021BCPZ | Narrow Band Transceiver 433/868/900 MHz | EAR99 | 8542390010". verified=false pending maintainer sign-off.

### 11. lattice-ice40hx4k-tq144 — `EAR99`  [VERIFIED]
- **Item:** Low-power FPGA, ~3,520 logic cells (Lattice Semiconductor)
- **Source:** https://www.digikey.com/en/products/detail/lattice-semiconductor-corporation/ICE40HX4K-TQ144/3083582
- **Notes:** TIER B (human-visible on the Digi-Key product page; distributor self-class). Confirmed 2026-06-24, matches. Quote: "Environmental & Export Classifications -> ECCN EAR99". CAVEAT: Digi-Key data was found WRONG on two sibling Microchip parts (corrected against the manufacturer), so where the maker can't be cross-checked, treat this as provisional.

### 12. adi-ad9081bbpz-4d4ab — `3A001.a.5.a.3`  [VERIFIED]
- **Item:** Quad RF-DAC / quad RF-ADC mixed-signal front-end (Analog Devices)
- **Source:** https://www.analog.com/en/support/view-export-classification.html
- **Notes:** TIER A (Analog Devices is on the BIS public-classification list; ECCN is human-visible). To verify: open the source_url, search 'AD9081BBPZ-4D4AB' in Product Model Search, and read the US ECCN column. Confirmed 2026-06-24 on ADI's export-classification tool, value matches. ADI tool row: "AD9081BBPZ-4D4AB | MxFE Quad 12G RFDAC Quad 4G RFADC 600MHz | 3A001.a.5.a.3 | 8542390050". verified=false pending maintainer sign-off.

### 13. adi-ad9162bbcz — `3A001.a.5.b.2`  [VERIFIED]
- **Item:** 6 GSPS RF digital-to-analog converter, to 5 GHz (Analog Devices)
- **Source:** https://www.analog.com/en/support/view-export-classification.html
- **Notes:** TIER A (Analog Devices is on the BIS public-classification list; ECCN is human-visible). To verify: open the source_url, search 'AD9162BBCZ' in Product Model Search, and read the US ECCN column. Confirmed 2026-06-24 on ADI's export-classification tool, value matches. ADI tool row: "AD9162BBCZ | General Purpose 5 GHz RFDAC | 3A001.a.5.b.2 | 8542390040". verified=false pending maintainer sign-off.

### 14. adi-adrv9009bbcz — `5A991.b.1`  [VERIFIED]
- **Item:** Integrated dual-channel RF transceiver, 75 MHz-6 GHz (Analog Devices)
- **Source:** https://www.analog.com/en/support/view-export-classification.html
- **Notes:** TIER A (Analog Devices is on the BIS public-classification list; ECCN is human-visible). To verify: open the source_url, search 'ADRV9009BBCZ' in Product Model Search, and read the US ECCN column. Confirmed 2026-06-24 on ADI's export-classification tool, value matches. ADI tool row: "ADRV9009BBCZ | Integrated Dual RF Rx/Tx/ORx | 5A991.b.1 | 8542390010". verified=false pending maintainer sign-off.

### 15. adi-adau1452kcpz — `3A991.a.2`  [VERIFIED]
- **Item:** 300 MHz 32-bit audio digital signal processor (Analog Devices)
- **Source:** https://www.analog.com/en/support/view-export-classification.html
- **Notes:** TIER A (Analog Devices is on the BIS public-classification list; ECCN is human-visible). To verify: open the source_url, search 'ADAU1452KCPZ' in Product Model Search, and read the US ECCN column. Confirmed 2026-06-24 on ADI's export-classification tool, value matches. ADI tool row: "ADAU1452KCPZ | 300 MHz 32bit SigmaDSP Audio Processor | 3A991.a.2 | 8542310035". verified=false pending maintainer sign-off.

### 16. adi-adsp-sc589bbcz-4b — `5A992.c`  [VERIFIED]
- **Item:** Dual-SHARC + ARM system-on-chip processor (Analog Devices)
- **Source:** https://www.analog.com/en/support/view-export-classification.html
- **Notes:** TIER A (Analog Devices is on the BIS public-classification list; ECCN is human-visible). To verify: open the source_url, search 'ADSP-SC589BBCZ-4B' in Product Model Search, and read the US ECCN column. Confirmed 2026-06-24 on ADI's export-classification tool, value matches. ADI tool row: "ADSP-SC589BBCZ-4B | ARM, 2xSHARC, dual DDR, PCIe, HPC PKG | 5A992.c | 8542310035". verified=false pending maintainer sign-off.

### 17. adi-maxq1061etp — `5A992.c`  [VERIFIED]
- **Item:** Cryptographic security controller IC (Analog Devices)
- **Source:** https://www.analog.com/en/support/view-export-classification.html
- **Notes:** TIER A (Analog Devices is on the BIS public-classification list; ECCN is human-visible). To verify: open the source_url, search 'MAXQ1061ETP+' in Product Model Search, and read the US ECCN column. Confirmed 2026-06-24 on ADI's export-classification tool, value matches. ADI tool row: "MAXQ1061ETP+ | DeepCover Cryptographic Controller | 5A992.c | 8542310030". verified=false pending maintainer sign-off.

### 18. adi-ad7768bstz — `EAR99`  [VERIFIED]
- **Item:** 8-channel 24-bit sigma-delta ADC, 256 kSPS (Analog Devices)
- **Source:** https://www.analog.com/en/support/view-export-classification.html
- **Notes:** TIER A (Analog Devices is on the BIS public-classification list; ECCN is human-visible). To verify: open the source_url, search 'AD7768BSTZ' in Product Model Search, and read the US ECCN column. Confirmed 2026-06-24 on ADI's export-classification tool, value matches. ADI tool row: "AD7768BSTZ | 256ksps 8 ch wideband 24B SD-ADC | EAR99 | 8542390030". verified=false pending maintainer sign-off.

### 19. microchip-pic32mz2048efm144-i-ph — `5A992.c`  [VERIFIED]
- **Item:** 32-bit MCU with hardware crypto engine (Microchip Technology)
- **Source:** https://www.microchipdirect.com/exportcontroldata/
- **Notes:** TIER B (human-visible; Microchip is not on the BIS list). To verify: open the source_url, search 'PIC32MZ2048EFM144-I/PH', read the Classification Number column. Confirmed 2026-06-24, matches. Tool row: "Classification Number 5A992.c | CCATS G185380 | NLR | 740.17(b)(1)".

### 20. microchip-dspic33ep512mu810-i-pf — `3A991.a.2`  [VERIFIED]
- **Item:** 16-bit digital signal controller, 60 MIPS (Microchip Technology)
- **Source:** https://www.microchipdirect.com/exportcontroldata/
- **Notes:** TIER B (human-visible; Microchip is not on the BIS list). To verify: open the source_url, search 'DSPIC33EP512MU810-I/PF', read the Classification Number column. Confirmed 2026-06-24, matches. Tool row: "Classification Number 3A991.a.2 | NLR".

### 21. microchip-rn4871-v-rm118 — `5A992.c`  [VERIFIED]
- **Item:** Bluetooth Low Energy 4.2 radio module (Microchip Technology)
- **Source:** https://www.microchipdirect.com/exportcontroldata/
- **Notes:** TIER B (human-visible; Microchip is not on the BIS list). To verify: open the source_url, search 'RN4871-V/RM118', read the Classification Number column. Confirmed 2026-06-24, matches. Tool row: "Classification Number 5A992.c | NLR | 740.17(b)(1)".

### 22. microchip-atecc608b-mahda-t — `5A992.c`  [VERIFIED]
- **Item:** Secure element / crypto authentication IC (Microchip Technology)
- **Source:** https://www.microchipdirect.com/exportcontroldata/
- **Notes:** TIER B (human-visible; Microchip is not on the BIS list). To verify: open the source_url, search 'ATECC608B-MAHDA-T', read the Classification Number column. Confirmed 2026-06-24, matches. Tool row: "Classification Number 5A992.c | NLR | 740.17(b)(1)".

### 23. microchip-lan8742a-cz-tr — `EAR99`  [VERIFIED]
- **Item:** 10/100 Ethernet PHY transceiver (RMII) (Microchip Technology)
- **Source:** https://www.microchipdirect.com/exportcontroldata/
- **Notes:** TIER B (human-visible; Microchip is not on the BIS list). To verify: open the source_url, search 'LAN8742A-CZ-TR', read the Classification Number column. Confirmed 2026-06-24, matches. Tool row: "Classification Number EAR99 | NLR".

### 24. adi-adis16480bmlz — `7A994`  [VERIFIED]
- **Item:** 10-DOF MEMS inertial measurement unit with on-board sensor fusion (Analog Devices)
- **Source:** https://www.analog.com/en/support/view-export-classification.html
- **Notes:** TIER A (Analog Devices on BIS public list; ECCN human-visible in ADI export tool). Search 'ADIS16480BMLZ' in Product Model Search; read US ECCN column. Confirmed 2026-06-24 via rendered DOM + ADI FetchExportClassificationData JSON. Tool row: "ADIS16480BMLZ | 10 DoF IMU, with Attitude & Heading | 7A994 | 8542390090". verified=false pending maintainer sign-off.

### 25. adi-adis16545-3bmlz — `7A003.d.1`  [VERIFIED]
- **Item:** Precision 6-DOF MEMS IMU, ±2000°/s gyro range (Analog Devices)
- **Source:** https://www.analog.com/en/support/view-export-classification.html
- **Notes:** TIER A (ADI export tool, human-visible). Search 'ADIS16545-3BMLZ'. Tool row: "ADIS16545-3BMLZ | 6 DOF Prec IMU, 8g (2000 DPS DNR) | 7A003.d.1 | 8542390090". HARD CASE: only the -3 (2000 DPS) variant steps up to 7A003.d.1; lower-range siblings are 7A994 - dynamic range drives the subparagraph. Confirmed 2026-06-24 (DOM + JSON). verified=false.

### 26. adi-adxrs453brgz — `7A994`  [VERIFIED]
- **Item:** ±300°/s single-axis MEMS angular rate gyroscope (Analog Devices)
- **Source:** https://www.analog.com/en/support/view-export-classification.html
- **Notes:** TIER A (ADI export tool, human-visible). Search 'ADXRS453BRGZ'. Tool row: "ADXRS453BRGZ | SOIC Digital Output Gyro +/-300 | 7A994 | 8542390090". Standalone single-axis gyro (sensor-type variety vs the IMUs). Confirmed 2026-06-24 (DOM + JSON). verified=false.

### 27. honeywell-hguide-i300 — `7A994`  [VERIFIED]
- **Item:** Tactical-grade 6-DOF MEMS inertial measurement unit (~1 cubic inch) (Honeywell Aerospace)
- **Source:** https://www.honeywellaerospace.com/us/en/products-and-services/products/navigation-and-sensors/inertial-measurement-units/hguide-i300-mems-inertial-measurement-unit
- **Notes:** TIER B (Honeywell Aerospace, not on BIS list; ECCN human-visible on the manufacturer product page). Quote: "It has an ECCN of 7A994 and is generally available without an export license." Confirmed 2026-06-24. verified=false.

### 28. lnd-202-bf3 — `1A999`  [VERIFIED]
- **Item:** Boron-trifluoride thermal neutron proportional counter (LND, Inc.)
- **Source:** https://www.lndinc.com/faq/
- **Notes:** TIER B (LND not on BIS list; ECCN human-visible on LND FAQ, which assigns ECCN by product family). Quote: "Our BF3 detectors and B10 lined detectors have been assigned ECCN 1A999 by BIS." Specs from product page https://www.lndinc.com/products/neutron-detectors/202/. verified=false.

### 29. lnd-2311-b10 — `1A999`  [VERIFIED]
- **Item:** Boron-10 lined thermal neutron proportional counter (LND, Inc.)
- **Source:** https://www.lndinc.com/faq/
- **Notes:** TIER B (LND FAQ, human-visible; family-level assignment). Quote: "Our BF3 detectors and B10 lined detectors have been assigned ECCN 1A999 by BIS." Specs from https://www.lndinc.com/products/neutron-detectors/2311/. verified=false.

### 30. lnd-2517-he3 — `1C232`  [VERIFIED]
- **Item:** Helium-3 thermal neutron detector tube (LND, Inc.)
- **Source:** https://www.lndinc.com/faq/
- **Notes:** TIER B (LND FAQ, human-visible). Quote: "Certain models of our 3He tubes are covered by the ECCN 1C232." 1C232 controls Helium-3 (nuclear nonproliferation). CAVEAT: FAQ hedges 'certain models' - per-model 1C232 vs EAR99/1A999 not individually published; the He-3 detector is the canonical 1C232 fit. Specs from https://www.lndinc.com/products/neutron-detectors/2517/. verified=false.

### 31. oberdorfer-obn9000rs3 — `2B999.j`  [VERIFIED]
- **Item:** Bronze rotary gear pump, 23 GPM (Oberdorfer (Ingersoll Rand))
- **Source:** https://www.motion.com/products/sku/11016143
- **Notes:** TIER B (distributor Motion Industries; ECCN human-visible in product title). Quote: "OBN9000RS3 ECCN 2B999.J GEAR PUMP". 2B999.j = positive-displacement pumps for corrosive service. CAVEAT: ECCN sits in the distributor product-name string (not a dedicated field) and the manufacturer page omits it; value appears consistently across distributors. verified=false.

### 32. nachi-7002cydup4 — `EAR99`  [VERIFIED]
- **Item:** Super-precision angular contact ball bearing, 15 mm bore (P4/ABEC-7) (NACHI)
- **Source:** https://www.powelltool.com/products/7002CYDUP4-NAC
- **Notes:** TIER B (distributor Powell Tool Supply; ECCN human-visible). Quote: "Standards and Approvals: ECCN: EAR99". TRAP CASE: a genuine P4/ABEC-7 super-precision spindle bearing - the tolerance class 2A001 names - yet correctly EAR99 because its small dimensions fall outside the 2A001 size envelope. Tests over-classification. verified=false.

### 33. piper-553-876-camlatch — `9A991.d`  [VERIFIED]
- **Item:** Aircraft access-panel cam latch (airframe hardware) (Piper Aircraft)
- **Source:** https://www.pilotshq.com/products/piper-aircraft-553-876-cam-latch-oem-airframe-hardware-part
- **Notes:** TIER C (distributor PilotsHQ; ECCN human-visible). Quote: "ECCN: 9A991.d". 9A991.d is the catch-all for commercial aircraft parts/components. CAVEAT: PilotsHQ ECCNs appear templated to the BIS aircraft-parts default - cross-check vs the OEM before relying. verified=false.

### 34. piper-101918-coax-gps — `9A991.d`  [VERIFIED]
- **Item:** Aircraft GPS antenna coaxial cable assembly (Piper Aircraft)
- **Source:** https://www.pilotshq.com/products/piper-aircraft-coax-gps-2-assembly-101918-003-oem-replacement
- **Notes:** TIER C (PilotsHQ; human-visible). Quote: "9A991.d". HARD CASE: a GPS/avionics RF part classified as an aircraft component (9A991.d) rather than nav equipment (7A994). CAVEAT: distributor-templated default; cross-check vs OEM. verified=false.
