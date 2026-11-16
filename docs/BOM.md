# Bill of Materials (BOM)

Source: `super car.pdf` complete BOM section. Standardized on 0805 SMD passives for hand-soldering or JLCPCB/PCBWay turnkey assembly.

## 1. Carrier PCB Electronic Components (per board)

| RefDes | Description | Exact Part Number | Qty | Package | LCSC # | Notes |
|--------|-------------|-------------------|-----|---------|--------|-------|
| U1 | Sync step-down buck 5V/3A | MP1584EN-LF-Z (or Mini-360 module) | 1 | SOIC-8-EP | C13972 | 7.4V → 5V_MAIN |
| L1 | Shielded power inductor | 10 µH / 3A SMD | 1 | CDRH5D28 | C169386 | For MP1584EN |
| U2 | Single-channel H-bridge 3A peak | RZ7889 (or TC1508S / MX1508) | 1 | SOIC-8 | C128955 | N20 rear motor drive |
| Q1,Q2,Q3 | Logic-level N-MOSFET | AO3400A | 3 | SOT-23 | C20917 | Q1 headlights, Q2 taillights, Q3 horn |
| D1 | Reverse-polarity Schottky | SS34 (40V/3A) | 1 | SMA | C8678 | Battery plug-in backward protection |
| D2 | ESP32-CAM rail isolation | 1N5819WS (40V/1A) | 1 | SOD-323 | C191023 | Prevents brownouts |
| D3 | Horn flyback diode | 1N4148W (100V/150mA) | 1 | SOD-123 | C81598 | Clamps inductive spikes |
| C1 | Anti-brownout bulk cap | 470 µF / 16V low-ESR radial | 1 | 8×10 mm | C134738 | At ESP32-CAM 5V/GND |
| C2,C3 | Servo & DFPlayer bulk | 220 µF / 16V radial | 2 | 6.3×7.7 mm | C72503 | SG92R stall + 3 W speaker spikes |
| C4 | Motor rail bulk cap | 100 µF / 16V radial | 1 | 6.3×5.4 mm | C134729 | At RZ7889 VDD |
| C5–C11 | HF bypass & motor EMI | 100 nF / 50V X7R | 7 | SMD 0805 | C49678 | C11 across M1_A/M1_B |
| C12,C13 | Buck in/out ceramic | 22 µF / 25V X5R | 2 | SMD 0805 | C45783 | MP1584EN ripple |
| R1 | Buck feedback top | 100 kΩ ±1% | 1 | SMD 0805 | C17407 | Sets 5.05 V |
| R2 | Buck feedback bottom | 18.7 kΩ ±1% | 1 | SMD 0805 | C17513 | FB to GND |
| R3–R7 | Boot pull-downs & gate bleeds | 10 kΩ ±5% | 5 | SMD 0805 | C17414 | GPIO 12, 14, 15 LOW at boot |
| R8–R11 | DFPlayer RX & MOSFET gate | 1 kΩ ±5% | 4 | SMD 0805 | C17513 | R8 kills DFPlayer RX hum |
| R12 | SG92R signal protection | 330 Ω ±5% | 1 | SMD 0805 | C17630 | GPIO 13 |
| R13,R14 | LED current limiters | 100 Ω ±5% | 2 | SMD 0805 | C17408 | White/red 5 mm LEDs |
| SW1 | Power slide switch | SS-12D00G3 SPDT 3A | 1 | THT 2.54 mm | C128955 | Full system current |

## 2. Plug-In Modules & Connectors

| RefDes | Module | Specification | Qty | Notes |
|--------|--------|---------------|-----|-------|
| MOD1 | ESP32-CAM (OV2640) | AI-Thinker, 2.4 GHz IPEX antenna | 1 | Plugs into top 1×8 headers |
| MOD2 | DFPlayer Mini / JQ6500-16P | Onboard SPI flash sound module | 1 | FAT32 MicroSD ≤32 GB for DFPlayer; USB drag-drop for JQ6500 |
| MH-M18 | Bluetooth A2DP receiver | 23 × 16 mm, ~60 BDT | 1 | Phone streams music as `RC_CAR_AUDIO` |
| J1 | Battery input | JST-XH 2-pin male shrouded 2.50 mm | 1 | 2S 18650 pack with BMS |
| J2 | Rear N20 motor | JST-XH 2-pin male shrouded | 1 | Vibration-proof locking |
| J3 | Front SG92R servo | 1×3 pin male 2.54 mm | 1 | GND-5V-SIG |
| J4,J5 | Headlight/taillight | JST-XH 2-pin male shrouded | 2 | 5 mm white/red LEDs |
| J6 | 3 W speaker | JST-XH 2-pin male shrouded | 1 | 36 mm 4 Ω 3 W speaker |
| J7 | UART programming | 1×4 pin male right-angle 2.54 mm | 1 | TX, RX, GND, GPIO0 |

## 3. Mechanical Drivetrain & Chassis Hardware

| Part | Specification | Qty | Purpose |
|------|---------------|-----|---------|
| Rear drive motor | N20 metal gearmotor 6V–12V, 400–500 RPM, 3 mm D-shaft | 1 | High-speed rear propulsion |
| Front steering servo | TowerPro SG92R 2.5 kg·cm metal-gear micro servo | 1 | Ackermann C-hub steering |
| Rear axle bearings | MR63ZZ miniature ball bearings 3×6×2.5 mm | 2 | Isolate 500 g load from N20 shaft |
| Axles | 3 mm stainless steel round rod, 150 mm | 1 | Cut: 75 mm rear + two 22 mm front |
| Shaft coupler | 3 mm→3 mm brass rigid coupler with M3 grub screws | 1 | N20 output → steel rear axle |
| Speaker | 36 mm diameter 4 Ω 3 W miniature | 1 | Upper deck acoustic ring |
| Battery pack | 2S 18650 holder + 7.4V 2S BMS board | 1 | Runtime + over-discharge cutoff |
| Fasteners | M2 × 8 mm, M2 × 16 mm (kingpins), M2.5 × 6 mm | 1 pack | Gearbox, C-hubs, PCB standoffs |

## 4. PCB Fabrication Settings (JLCPCB / PCBWay)

| Parameter | Value |
|-----------|-------|
| Layers | 2 |
| Dimensions | 46 mm × 32 mm |
| Thickness | 1.6 mm |
| Copper weight | 1 oz (1.2–1.5 mm traces on VBAT/motor lines) |
| Surface finish | HASL or LeadFree HASL |
| Expected cost | ~$2–$5 for 5 boards |

## 5. Audio Files (MicroSD or JQ6500 Flash)

| File | Location | Purpose |
|------|----------|---------|
| `/mp3/0001.mp3` | DFPlayer SD or JQ6500 flash | Car horn blast (0.5–1.5 s) |
| `/mp3/0002.mp3` | DFPlayer SD or JQ6500 flash | Engine idle / turbo rev |
| `/mp3/0003.mp3`+ | DFPlayer SD or JQ6500 flash | Background music tracks 1…N |

## Ordering Checklist

- [ ] PCB: 5× `FPV_RC_Carrier_46x32.kicad_pcb` Gerbers
- [ ] SMD passives: 0805 reels per BOM table
- [ ] Modules: ESP32-CAM, JQ6500-16P or DFPlayer Mini, MH-M18, RZ7889, MP1584EN
- [ ] Mechanical: N20 motor, SG92R servo, MR63ZZ bearings, 3 mm steel rod, brass coupler
- [ ] Power: 2S 18650 cells + BMS + charger
- [ ] Audio: 36 mm 3 W speaker, 5 mm LEDs, MicroSD ≤32 GB