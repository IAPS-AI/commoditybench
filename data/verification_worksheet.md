# Verification worksheet — CommodityBench candidate dataset

29 candidate questions sourced from manufacturer self-classifications. **None is verified yet.** For each item: open the `source_url`, confirm the published ECCN matches that exact part, and record your decision. A reviewer then flips `verified: true` (or corrects `gold_eccn`) in `data/questions.jsonl`.

> ⚠️ These ECCNs are manufacturer self-classifications. Per BIS, they are not validated by BIS and are for informational purposes only. Treat them as candidate labels to confirm, not authoritative truth.

**Plausibility** is *my* read from the controlling CCL logic, to prioritize your attention — not a verification. 🟢 = expected/strong, 🟡 = check the specifics.

## Items needing extra scrutiny (resolve these first)

- **thorlabs-mx10a** (Benchtop electro-optic modulator driver, 12.5 Gb/s, `5B991`): FLAG: classified 5B991 (telecom *test/production* equipment, group B). A modulator driver reads more like a component (group A). Verify the group letter, not just the number.
- **microchip-lan8720a-cp-tr** (10/100 Ethernet PHY transceiver (RMII), `5A991.b.1`): FLAG: published 5A991.b.1, but the near-identical LAN8742A (this set) is published EAR99. One of the two is the interesting case; resolve both against Microchip's current data.
- **adi-adrv9009bbcz** (Integrated dual-channel RF transceiver, 75 MHz-6 GHz, `5A991.b.1`): FLAG: RF transceiver to 6 GHz with 200 MHz bandwidth as 5A991.b.1. The wider 200 MHz BW pushes closer to 5A001 thresholds than the AD9361 — worth a careful look.
- **microchip-lan8742a-cz-tr** (10/100 Ethernet PHY transceiver (RMII), `EAR99`): FLAG: published EAR99, vs LAN8720A (5A991.b.1) in this set. Resolve the pair together.

## Decision table

| # | ID | Item | Mfr | Published ECCN | Plaus | ✅ Confirm? | Corrected ECCN | Reviewer notes |
|---|----|------|-----|----------------|:-----:|:-----------:|----------------|----------------|
| 1 | thorlabs-km100 | Kinematic mirror mount for 1-inch optics | Thorlabs | `EAR99` | 🟢 |  |  |  |
| 2 | thorlabs-det36a2 | Biased silicon photodetector, 350-1100 nm | Thorlabs | `EAR99` | 🟢 |  |  |  |
| 3 | thorlabs-cs165mu | 1.6 MP monochrome CMOS camera | Thorlabs | `EAR99` | 🟡 |  |  |  |
| 4 | thorlabs-bb1-e02 | 1-inch broadband dielectric mirror, 400-750 nm | Thorlabs | `EAR99` | 🟢 |  |  |  |
| 5 | thorlabs-sfl1550p | 1550 nm 40 mW external-cavity butterfly laser, PM fiber | Thorlabs | `6A995.b.1.b` | 🟡 |  |  |  |
| 6 | thorlabs-lp1550-sad2 | 1550 nm 2 mW DFB laser with isolator, SM fiber | Thorlabs | `6A995.b.1.b` | 🟡 |  |  |  |
| 7 | thorlabs-fpl1009s | 1550 nm 100 mW butterfly laser diode, SM fiber | Thorlabs | `6A995.b.2` | 🟡 |  |  |  |
| 8 | thorlabs-mx10a | Benchtop electro-optic modulator driver, 12.5 Gb/s | Thorlabs | `5B991` | 🟡 |  |  |  |
| 9 | st-stm32f407vgt6 | 32-bit ARM Cortex-M4 microcontroller, 168 MHz | STMicroelectronics | `3A991.a.2` | 🟡 |  |  |  |
| 10 | espressif-esp32-wroom-32e-n4 | 2.4 GHz Wi-Fi + Bluetooth module, 4 MB flash | Espressif Systems | `5A992.c` | 🟡 |  |  |  |
| 11 | ti-am3358bzcz100 | 1 GHz ARM Cortex-A8 applications microprocessor | Texas Instruments | `5A992.c` | 🟡 |  |  |  |
| 12 | rpi-sc0668 | Quad-core ARM Cortex-A72 compute module (2 GB / 16 GB) | Raspberry Pi | `5A992.c` | 🟡 |  |  |  |
| 13 | microchip-lan8720a-cp-tr | 10/100 Ethernet PHY transceiver (RMII) | Microchip Technology | `5A991.b.1` | 🟡 |  |  |  |
| 14 | microchip-ksz8794cnxic-tr | Four-port managed 10/100 Ethernet switch | Microchip Technology | `5A991.b.1` | 🟡 |  |  |  |
| 15 | adi-ad9361bbcz | Wideband 2x2 RF agile transceiver, 47 MHz-6 GHz | Analog Devices | `5A991.b.1` | 🟡 |  |  |  |
| 16 | adi-adf7021bcpz | Narrow-band sub-1 GHz ISM RF transceiver | Analog Devices | `EAR99` | 🟡 |  |  |  |
| 17 | lattice-ice40hx4k-tq144 | Low-power FPGA, ~3,520 logic cells | Lattice Semiconductor | `EAR99` | 🟡 |  |  |  |
| 18 | adi-ad9081bbpz-4d4ab | Quad RF-DAC / quad RF-ADC mixed-signal front-end | Analog Devices | `3A001.a.5.a.3` | 🟢 |  |  |  |
| 19 | adi-ad9162bbcz | 6 GSPS RF digital-to-analog converter, to 5 GHz | Analog Devices | `3A001.a.5.b.2` | 🟢 |  |  |  |
| 20 | adi-adrv9009bbcz | Integrated dual-channel RF transceiver, 75 MHz-6 GHz | Analog Devices | `5A991.b.1` | 🟡 |  |  |  |
| 21 | adi-adau1452kcpz | 300 MHz 32-bit audio digital signal processor | Analog Devices | `3A991.a.2` | 🟡 |  |  |  |
| 22 | adi-adsp-sc589bbcz-4b | Dual-SHARC + ARM system-on-chip processor | Analog Devices | `5A992.c` | 🟡 |  |  |  |
| 23 | adi-maxq1061etp | Cryptographic security controller IC | Analog Devices | `5A992.c` | 🟡 |  |  |  |
| 24 | adi-ad7768bstz | 8-channel 24-bit sigma-delta ADC, 256 kSPS | Analog Devices | `EAR99` | 🟢 |  |  |  |
| 25 | microchip-pic32mz2048efm144-i-ph | 32-bit MCU with hardware crypto engine | Microchip Technology | `5A992.c` | 🟡 |  |  |  |
| 26 | microchip-dspic33ep512mu810-i-pf | 16-bit digital signal controller, 60 MIPS | Microchip Technology | `3A991.a.2` | 🟡 |  |  |  |
| 27 | microchip-rn4871-v-rm118 | Bluetooth Low Energy 4.2 radio module | Microchip Technology | `5A992.c` | 🟡 |  |  |  |
| 28 | microchip-atecc608b-mahda-t | Secure element / crypto authentication IC | Microchip Technology | `5A992.c` | 🟢 |  |  |  |
| 29 | microchip-lan8742a-cz-tr | 10/100 Ethernet PHY transceiver (RMII) | Microchip Technology | `EAR99` | 🟡 |  |  |  |

## Evidence & plausibility (per item)

### 1. thorlabs-km100 — `EAR99` 🟢
- **Item:** Kinematic mirror mount for 1-inch optics (Thorlabs, EAR99)
- **Description:** Two-adjuster kinematic mount that holds a one-inch (25.4 mm) round optic and allows fine tip/tilt angular adjustment about two orthogonal axes via micrometer-style screws. Used to align mirrors and other flat optics in free-space optical setups; provides stable, repeatable pointing with spring-loaded retention.
- **Source:** <https://www.thorlabs.com/item/KM100>
- **Provenance:** Source quote: product data field "eccnTL":"EAR99". Published ECCN as raw text: 'EAR99'. PENDING human verification.
- **My read:** Passive optomechanical mount; no controlled parameters. EAR99 is the expected answer.

### 2. thorlabs-det36a2 — `EAR99` 🟢
- **Item:** Biased silicon photodetector, 350-1100 nm (Thorlabs, EAR99)
- **Description:** Reverse-biased silicon PIN photodiode detector with a 13 mm^2 active area, sensitive over the 350-1100 nm spectral range with a 14 ns rise time for measuring optical pulses and intensity. Includes universal mounting holes for post mounting in an optical setup.
- **Source:** <https://www.thorlabs.com/item/DET36A2>
- **Provenance:** Source quote: product data field "eccnTL":"EAR99". Published ECCN as raw text: 'EAR99'. PENDING human verification.
- **My read:** Silicon PIN detector in the visible/NIR; not the specialized IR/avalanche detectors of 6A002. EAR99 expected.

### 3. thorlabs-cs165mu — `EAR99` 🟡
- **Item:** 1.6 MP monochrome CMOS camera (Thorlabs, EAR99)
- **Description:** Compact 1.6 megapixel monochrome scientific CMOS camera with a global electronic shutter, 3.45 um pixels, 1/2.9-inch optical format, 10-bit digital output, read noise below 4 e- RMS, and up to ~35 fps full-frame rate. Passively cooled, used for microscopy, machine vision, and general scientific imaging.
- **Source:** <https://www.thorlabs.com/item/CS165MU>
- **Provenance:** Source quote: product data field "eccnTL":"EAR99". Published ECCN as raw text: 'EAR99'. PENDING human verification.
- **My read:** Visible-band CMOS camera. Cameras turn on 6A003 thresholds (frame rate, features); a ~35 fps 1.6 MP visible camera should sit below them, but confirm the frame-rate/ROI specs against 6A003.b.

### 4. thorlabs-bb1-e02 — `EAR99` 🟢
- **Item:** 1-inch broadband dielectric mirror, 400-750 nm (Thorlabs, EAR99)
- **Description:** One-inch (25.4 mm) broadband dielectric mirror with a multilayer dielectric coating optimized for high reflectance across the 400-750 nm visible band on a fused-silica substrate. Used as a turning/folding mirror for visible-wavelength free-space beam steering.
- **Source:** <https://www.thorlabs.com/item/BB1-E02>
- **Provenance:** Source quote: product data field "eccnTL":"EAR99". Published ECCN as raw text: 'EAR99'. PENDING human verification.
- **My read:** Standard dielectric mirror; not the special mirrors of 6A004 (deformable, high damage threshold, etc.). EAR99 expected.

### 5. thorlabs-sfl1550p — `6A995.b.1.b` 🟡
- **Item:** 1550 nm 40 mW external-cavity butterfly laser, PM fiber (Thorlabs, 6)
- **Description:** Narrow-linewidth single-frequency external-cavity diode laser emitting at a 1550 nm center wavelength with 40 mW output power, in a butterfly package with an integrated thermoelectric cooler and polarization-maintaining fiber pigtail terminated with an FC/APC connector. Used as a coherent source for telecom, interferometry, and sensing.
- **Source:** <https://www.thorlabs.com/item/SFL1550P>
- **Provenance:** Source quote: product data field "eccnTL":"6A995.b.1.b". Published ECCN as raw text: '6A995.b.1.b'. PENDING human verification.
- **My read:** 1550 nm telecom-band laser. 6A995 is the AT-controlled laser subset; confirm 6A995.b.1.b vs the main laser entry 6A005 (turns on power/wavelength/pulse specs).

### 6. thorlabs-lp1550-sad2 — `6A995.b.1.b` 🟡
- **Item:** 1550 nm 2 mW DFB laser with isolator, SM fiber (Thorlabs, 6)
- **Description:** TO-can packaged distributed-feedback (DFB) semiconductor laser emitting at 1550 nm with 2 mW output, incorporating an internal optical isolator and a single-mode fiber pigtail terminated with an FC/APC connector. Provides a stable single-frequency source for fiber-optic communications and test applications.
- **Source:** <https://www.thorlabs.com/item/LP1550-SAD2>
- **Provenance:** Source quote: product data field "eccnTL":"6A995.b.1.b". Published ECCN as raw text: '6A995.b.1.b'. PENDING human verification.
- **My read:** Low-power (2 mW) 1550 nm DFB laser as 6A995.b.1.b. Same 6A995-vs-6A005 check as above; low power supports the AT-only 6A995 read.

### 7. thorlabs-fpl1009s — `6A995.b.2` 🟡
- **Item:** 1550 nm 100 mW butterfly laser diode, SM fiber (Thorlabs, 6)
- **Description:** Fabry-Perot semiconductor laser diode emitting at a 1550 nm center wavelength with 100 mW output power, in a butterfly package with a single-mode fiber pigtail terminated with an FC/APC connector. Used as a higher-power near-infrared source for fiber-coupled applications and pumping.
- **Source:** <https://www.thorlabs.com/item/FPL1009S>
- **Provenance:** Source quote: product data field "eccnTL":"6A995.b.2". Published ECCN as raw text: '6A995.b.2'. PENDING human verification.
- **My read:** 100 mW 1550 nm laser diode as 6A995.b.2. Confirm the .b.2 subparagraph and the 6A995-vs-6A005 boundary at this power.

### 8. thorlabs-mx10a — `5B991` 🟡
- **Item:** Benchtop electro-optic modulator driver, 12.5 Gb/s (Thorlabs, 5)
- **Description:** Benchtop RF amplifier/driver designed to drive electro-optic modulators at data rates up to 12.5 Gb/s, providing the high-bandwidth electrical drive signal needed for high-speed optical communication links and modulation experiments.
- **Source:** <https://www.thorlabs.com/item/MX10A>
- **Provenance:** Source quote: product data field "eccnTL":"5B991". Published ECCN as raw text: '5B991'. PENDING human verification.
- **My read:** FLAG: classified 5B991 (telecom *test/production* equipment, group B). A modulator driver reads more like a component (group A). Verify the group letter, not just the number.

### 9. st-stm32f407vgt6 — `3A991.a.2` 🟡
- **Item:** 32-bit ARM Cortex-M4 microcontroller, 168 MHz (STMicroelectronics, 3)
- **Description:** 32-bit ARM Cortex-M4 microcontroller with floating-point unit running at up to 168 MHz, 1 MB flash, 192 KB SRAM, in a 100-pin LQFP package. General-purpose microcontroller for embedded control, motor control, and connectivity applications.
- **Source:** <https://www.digikey.com/en/products/detail/stmicroelectronics/STM32F407VGT6/2747117>
- **Provenance:** Source quote: ECCN 3A991A2. Published ECCN as raw text: '3A991A2'. PENDING human verification.
- **My read:** General-purpose Cortex-M4 MCU as 3A991.a.2 (microprocessor microcircuits). Common and plausible; confirm against ST's current export data.

### 10. espressif-esp32-wroom-32e-n4 — `5A992.c` 🟡
- **Item:** 2.4 GHz Wi-Fi + Bluetooth module, 4 MB flash (Espressif Systems, 5)
- **Description:** Integrated 2.4 GHz Wi-Fi (802.11 b/g/n) and Bluetooth/BLE module built around a dual-core processor with 4 MB embedded flash. Surface-mount radio-frequency transceiver module for wireless connectivity designs.
- **Source:** <https://www.digikey.com/en/products/detail/espressif-systems/ESP32-WROOM-32E-N4/11613125>
- **Provenance:** Source quote: ECCN 5A992C. Published ECCN as raw text: '5A992C'. PENDING human verification.
- **My read:** Wi-Fi/BLE module implementing standard crypto -> 5A992.c (mass-market encryption). Plausible; the classification rests on the encryption + mass-market self-classification.

### 11. ti-am3358bzcz100 — `5A992.c` 🟡
- **Item:** 1 GHz ARM Cortex-A8 applications microprocessor (Texas Instruments, 5)
- **Description:** Single-core 32-bit ARM Cortex-A8 applications microprocessor running at 1.0 GHz with integrated graphics and industrial communications support, in a 324-ball BGA package. Targets embedded computing and human-machine-interface applications.
- **Source:** <https://www.digikey.com/en/products/detail/texas-instruments/AM3358BZCZ100/4073874>
- **Provenance:** Source quote: ECCN 5A992C. Published ECCN as raw text: '5A992C'. PENDING human verification.
- **My read:** Cortex-A8 applications processor with crypto -> 5A992.c. Plausible for a processor with standard cryptographic functions.

### 12. rpi-sc0668 — `5A992.c` 🟡
- **Item:** Quad-core ARM Cortex-A72 compute module (2 GB / 16 GB) (Raspberry Pi, 5)
- **Description:** System-on-module computer based on a quad-core ARM Cortex-A72 processor at 1.5 GHz with 2 GB RAM and 16 GB eMMC storage, Gigabit Ethernet, USB 2.0, HDMI, and wireless connectivity, on a 55x40 mm module.
- **Source:** <https://www.digikey.com/en/products/detail/raspberry-pi/SC0668/13530939>
- **Provenance:** Source quote: ECCN 5A992C SC. Published ECCN as raw text: '5A992C SC'. PENDING human verification.
- **My read:** Compute module with wireless + crypto -> 5A992.c. The published value carried a trailing 'SC' annotation (dropped during canonicalization); confirm it didn't change the ECCN.

### 13. microchip-lan8720a-cp-tr — `5A991.b.1` 🟡
- **Item:** 10/100 Ethernet PHY transceiver (RMII) (Microchip Technology, 5)
- **Description:** Low-power 10BASE-T/100BASE-TX Ethernet physical-layer (PHY) transceiver compliant with IEEE 802.3, supporting an RMII interface to an Ethernet MAC, with Auto-Negotiation and Auto-MDIX, in a 24-QFN package.
- **Source:** <https://www.digikey.com/en/products/detail/microchip-technology/LAN8720A-CP-TR/3872109>
- **Provenance:** DISCREPANCY TO RESOLVE: a near-identical Microchip Ethernet PHY (LAN8742A, in this set) is published as EAR99 while this one is published as 5A991.b.1. Confirm both against the maker's current export data. Source quote: ECCN 5A991B1. Published ECCN as raw text: '5A991B1'. PENDING human verification.
- **My read:** FLAG: published 5A991.b.1, but the near-identical LAN8742A (this set) is published EAR99. One of the two is the interesting case; resolve both against Microchip's current data.

### 14. microchip-ksz8794cnxic-tr — `5A991.b.1` 🟡
- **Item:** Four-port managed 10/100 Ethernet switch (Microchip Technology, 5)
- **Description:** Layer-2 managed four-port 10/100 Ethernet switch with integrated PHYs and an MII/RMII/RGMII interface to a host processor, in a 64-QFN package. Used in industrial networking and embedded switching applications.
- **Source:** <https://www.digikey.com/en/products/detail/microchip-technology/KSZ8794CNXIC-TR/5319443>
- **Provenance:** Source quote: ECCN 5A991B1. Published ECCN as raw text: '5A991B1'. PENDING human verification.
- **My read:** Managed Ethernet switch as 5A991.b.1 (telecom switching equipment). Plausible; switches with management commonly land in 5A991.b.

### 15. adi-ad9361bbcz — `5A991.b.1` 🟡
- **Item:** Wideband 2x2 RF agile transceiver, 47 MHz-6 GHz (Analog Devices, 5)
- **Description:** Wideband 2x2 RF agile transceiver integrating an RF front end, mixed-signal baseband with data converters, and frequency synthesizers; local oscillator tunable from 47 MHz to 6.0 GHz with channel bandwidths up to 56 MHz, in a 144-ball CSP BGA. Used in software-defined radio and wireless infrastructure.
- **Source:** <https://www.digikey.com/en/products/detail/analog-devices-inc/AD9361BBCZ/4439647>
- **Provenance:** Source quote: ECCN 5A991B1. Published ECCN as raw text: '5A991B1'. PENDING human verification.
- **My read:** Wideband 2x2 RF transceiver (47 MHz-6 GHz, 56 MHz BW) as 5A991.b.1. SDR transceivers can cross into 5A001 on bandwidth/frequency; 56 MHz BW supports the 5A991 read but confirm.

### 16. adi-adf7021bcpz — `EAR99` 🟡
- **Item:** Narrow-band sub-1 GHz ISM RF transceiver (Analog Devices, EAR99)
- **Description:** High-performance narrow-band sub-1 GHz ISM-band RF transceiver supporting 80-650 MHz and 862-950 MHz with FSK/GFSK modulation, in a 48-lead exposed-pad package. Used in low-power wireless data links and metering.
- **Source:** <https://www.digikey.com/en/products/detail/analog-devices-inc/ADF7021BCPZ/1523018>
- **Provenance:** Source quote: ECCN EAR99. Published ECCN as raw text: 'EAR99'. PENDING human verification.
- **My read:** Narrowband sub-1 GHz ISM transceiver as EAR99. No strong crypto and modest RF performance support EAR99; confirm it's below 5A001 telecom thresholds.

### 17. lattice-ice40hx4k-tq144 — `EAR99` 🟡
- **Item:** Low-power FPGA, ~3,520 logic cells (Lattice Semiconductor, EAR99)
- **Description:** High-performance field-programmable gate array with roughly 3,520 logic cells, 107 I/O, and embedded block RAM, in a 144-pin LQFP package. Low-cost FPGA for hardware acceleration, glue logic, and interface bridging.
- **Source:** <https://www.digikey.com/en/products/detail/lattice-semiconductor-corporation/ICE40HX4K-TQ144/3083582>
- **Provenance:** Source quote: ECCN EAR99. Published ECCN as raw text: 'EAR99'. PENDING human verification.
- **My read:** Small low-density FPGA as EAR99. Plausible (well below any high-end IC controls); confirm there's no crypto/programmable-logic trigger.

### 18. adi-ad9081bbpz-4d4ab — `3A001.a.5.a.3` 🟢
- **Item:** Quad RF-DAC / quad RF-ADC mixed-signal front-end (Analog Devices, 3)
- **Description:** Mixed-signal front-end integrating four 12 GSPS radio-frequency digital-to-analog converter channels and four 4 GSPS radio-frequency analog-to-digital converter channels, with on-chip digital up/down conversion and a JESD204B/C serial interface (~600 MHz channel bandwidth), for wideband direct-RF transmit and receive signal chains.
- **Source:** <https://www.analog.com/exportclassification/search?searchBy=AD9081BBPZ-4D4AB>
- **Provenance:** Source quote: {"ModelNumber":"AD9081BBPZ-4D4AB","ECCN":"3A001.a.5.a.3","US_Commodity_Code":"8542390050"}. Published ECCN as raw text: '3A001.a.5.a.3'. PENDING human verification.
- **My read:** Quad 12 GSPS DAC / 4 GSPS ADC -> 3A001.a.5 (high-speed data converters). 12 GSPS clearly exceeds the control thresholds; textbook controlled item. Confirm the exact .a.3 subparagraph.

### 19. adi-ad9162bbcz — `3A001.a.5.b.2` 🟢
- **Item:** 6 GSPS RF digital-to-analog converter, to 5 GHz (Analog Devices, 3)
- **Description:** High-speed 16-bit radio-frequency digital-to-analog converter with up to 6 GSPS update rate supporting direct signal synthesis to 5 GHz, a JESD204B serial data interface, and integrated interpolation and numerically controlled oscillator for wideband transmit applications.
- **Source:** <https://www.analog.com/exportclassification/search?searchBy=AD9162BBCZ>
- **Provenance:** Source quote: {"ModelNumber":"AD9162BBCZ","ECCN":"3A001.a.5.b.2","US_Commodity_Code":"8542390040"}. Published ECCN as raw text: '3A001.a.5.b.2'. PENDING human verification.
- **My read:** 6 GSPS RF DAC to 5 GHz -> 3A001.a.5.b. Update rate is well into controlled territory. Confirm the .b.2 subparagraph.

### 20. adi-adrv9009bbcz — `5A991.b.1` 🟡
- **Item:** Integrated dual-channel RF transceiver, 75 MHz-6 GHz (Analog Devices, 5)
- **Description:** Highly integrated radio-frequency agile transceiver providing two transmit, two receive, and an observation-receive channel covering roughly 75 MHz to 6 GHz, with up to 200 MHz bandwidth, on-chip synthesizers and digital filtering for software-defined radio and wireless infrastructure.
- **Source:** <https://www.analog.com/exportclassification/search?searchBy=ADRV9009BBCZ>
- **Provenance:** Source quote: {"ModelNumber":"ADRV9009BBCZ","ECCN":"5A991.b.1","US_Commodity_Code":"8542390010"}. Published ECCN as raw text: '5A991.b.1'. PENDING human verification.
- **My read:** FLAG: RF transceiver to 6 GHz with 200 MHz bandwidth as 5A991.b.1. The wider 200 MHz BW pushes closer to 5A001 thresholds than the AD9361 — worth a careful look.

### 21. adi-adau1452kcpz — `3A991.a.2` 🟡
- **Item:** 300 MHz 32-bit audio digital signal processor (Analog Devices, 3)
- **Description:** Single-core 32-bit audio digital signal processor running at 300 MHz with multichannel digital audio I/O, an integrated PLL and a signal-processing engine for low-latency audio mixing, filtering and equalization.
- **Source:** <https://www.analog.com/exportclassification/search?searchBy=ADAU1452KCPZ>
- **Provenance:** Source quote: {"ModelNumber":"ADAU1452KCPZ","ECCN":"3A991.a.2","US_Commodity_Code":"8542310035"}. Published ECCN as raw text: '3A991.a.2'. PENDING human verification.
- **My read:** 300 MHz audio DSP as 3A991.a.2. Plausible classification for a signal-processing microcircuit; confirm.

### 22. adi-adsp-sc589bbcz-4b — `5A992.c` 🟡
- **Item:** Dual-SHARC + ARM system-on-chip processor (Analog Devices, 5)
- **Description:** Heterogeneous processor combining an ARM Cortex-A5 core with two floating-point SHARC DSP cores, dual DDR memory controllers, PCIe and extensive connectivity for high-performance audio, industrial and signal-processing systems.
- **Source:** <https://www.analog.com/exportclassification/search?searchBy=ADSP-SC589BBCZ-4B>
- **Provenance:** Source quote: {"ModelNumber":"ADSP-SC589BBCZ-4B","ECCN":"5A992.c","US_Commodity_Code":"8542310035"}. Published ECCN as raw text: '5A992.c'. PENDING human verification.
- **My read:** ARM+dual-SHARC SoC with crypto -> 5A992.c. Plausible for a processor with standard cryptographic functions.

### 23. adi-maxq1061etp — `5A992.c` 🟡
- **Item:** Cryptographic security controller IC (Analog Devices, 5)
- **Description:** Dedicated hardware cryptographic controller providing TLS/secure-boot acceleration, public-key (ECDSA/ECDH) and symmetric (AES) engines, secure key storage and a true random number generator for embedded and smart-metering security.
- **Source:** <https://www.analog.com/exportclassification/search?searchBy=MAXQ1061ETP%2B>
- **Provenance:** Source quote: {"ModelNumber":"MAXQ1061ETP+","ECCN":"5A992.c","US_Commodity_Code":"8542310030"}. Published ECCN as raw text: '5A992.c'. PENDING human verification.
- **My read:** Dedicated cryptographic controller -> 5A992.c with License Exception ENC (740.17(b)(1)) noted in the source, which is consistent for mass-market crypto. Plausible.

### 24. adi-ad7768bstz — `EAR99` 🟢
- **Item:** 8-channel 24-bit sigma-delta ADC, 256 kSPS (Analog Devices, EAR99)
- **Description:** Eight-channel simultaneous-sampling 24-bit sigma-delta analog-to-digital converter with wideband performance up to 256 kSPS per channel, integrated digital filtering and a low-noise front end for precision data acquisition and condition monitoring.
- **Source:** <https://www.analog.com/exportclassification/search?searchBy=AD7768BSTZ>
- **Provenance:** Source quote: {"ModelNumber":"AD7768BSTZ","ECCN":"EAR99","US_Commodity_Code":"8542390030"}. Published ECCN as raw text: 'EAR99'. PENDING human verification.
- **My read:** 256 kSPS 24-bit ADC -> EAR99. Sample rate is far below the 3A001.a.5 converter thresholds, so EAR99 is internally consistent with the controlled GSPS converters above. Strong read.

### 25. microchip-pic32mz2048efm144-i-ph — `5A992.c` 🟡
- **Item:** 32-bit MCU with hardware crypto engine (Microchip Technology, 5)
- **Description:** High-performance 32-bit MIPS-based microcontroller with 2048 KB flash, 512 KB RAM, an integrated hardware cryptographic engine (AES/3DES/SHA with random number generator), CAN, USB and Ethernet interfaces, in a 144-pin package.
- **Source:** <https://www.microchipdirect.com/exportcontroldata/?CPN=PIC32MZ2048EFM144-I/PH>
- **Provenance:** Source quote: {"PartNumber":"PIC32MZ2048EFM144-I/PH","ECCNNum":"5A992.c","CCATSVal":"G185380","ENCLVal":"740.17(b)(1)"}. Published ECCN as raw text: '5A992.c'. PENDING human verification.
- **My read:** MCU with hardware crypto engine -> 5A992.c (ENC 740.17(b)(1) noted). Plausible for a part with AES/3DES/SHA.

### 26. microchip-dspic33ep512mu810-i-pf — `3A991.a.2` 🟡
- **Item:** 16-bit digital signal controller, 60 MIPS (Microchip Technology, 3)
- **Description:** 16-bit digital signal controller running at 60 MIPS with 512 KB flash and 52 KB RAM, an integrated DSP engine, USB OTG, two CAN modules and 15-channel DMA, in a 100-pin package, for motor control and embedded signal processing.
- **Source:** <https://www.microchipdirect.com/exportcontroldata/?CPN=DSPIC33EP512MU810-I/PF>
- **Provenance:** Source quote: {"PartNumber":"DSPIC33EP512MU810-I/PF","ECCNNum":"3A991.a.2","USELSVal":"NLR"}. Published ECCN as raw text: '3A991.a.2'. PENDING human verification.
- **My read:** 16-bit DSC as 3A991.a.2. Plausible; confirm against Microchip's current data.

### 27. microchip-rn4871-v-rm118 — `5A992.c` 🟡
- **Item:** Bluetooth Low Energy 4.2 radio module (Microchip Technology, 5)
- **Description:** Certified Bluetooth 4.2 Low Energy radio module in a shielded 9 x 11.5 mm package with integrated antenna and an ASCII command interface, providing a complete 2.4 GHz wireless transceiver subsystem for connectivity.
- **Source:** <https://www.microchipdirect.com/exportcontroldata/?CPN=RN4871-V/RM118>
- **Provenance:** Source quote: {"PartNumber":"RN4871-V/RM118","ECCNNum":"5A992.c","ENCLVal":"740.17(b)(1)"}. Published ECCN as raw text: '5A992.c'. PENDING human verification.
- **My read:** BLE radio module -> 5A992.c (ENC 740.17(b)(1) noted). Plausible for a wireless module with standard crypto.

### 28. microchip-atecc608b-mahda-t — `5A992.c` 🟢
- **Item:** Secure element / crypto authentication IC (Microchip Technology, 5)
- **Description:** Hardware secure element providing ECDSA/ECDH elliptic-curve cryptography, AES-128, SHA-256, protected key storage and a true random number generator over an I2C interface, used for device authentication and secure boot.
- **Source:** <https://www.microchipdirect.com/exportcontroldata/?CPN=ATECC608B-MAHDA-T>
- **Provenance:** Cross-corroborated: Digi-Key independently lists the ATECC608 family as 5A992.c. Source quote: {"PartNumber":"ATECC608B-MAHDA-T","ECCNNum":"5A992.c","ENCLVal":"740.17(b)(1)"}. Published ECCN as raw text: '5A992.c'. PENDING human verification.
- **My read:** Secure element -> 5A992.c, and Digi-Key independently lists the ATECC608 family as 5A992.c. Cross-corroborated; strong read.

### 29. microchip-lan8742a-cz-tr — `EAR99` 🟡
- **Item:** 10/100 Ethernet PHY transceiver (RMII) (Microchip Technology, EAR99)
- **Description:** Single-port 10BASE-T/100BASE-TX Ethernet physical-layer transceiver with an RMII interface, integrated cable diagnostics and low-power modes, for embedded networking.
- **Source:** <https://www.microchipdirect.com/exportcontroldata/?CPN=LAN8742A-CZ-TR>
- **Provenance:** DISCREPANCY TO RESOLVE: published EAR99 here, while the similar LAN8720A (in this set) is published 5A991.b.1. Source quote: {"PartNumber":"LAN8742A-CZ-TR","ECCNNum":"EAR99"}. Published ECCN as raw text: 'EAR99'. PENDING human verification.
- **My read:** FLAG: published EAR99, vs LAN8720A (5A991.b.1) in this set. Resolve the pair together.
