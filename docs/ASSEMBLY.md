# Assembly Guide — Supercar ESP32-CAM FPV RC Car

> Step-by-step build order. Follow in sequence — each step builds on the previous.
> Estimated build time: 2–3 hours (excluding 3D print time).

## Prerequisites

- All 3D-printed parts (PETG/ABS for structural, 95A TPU for tires)
- Populated PCB (`FPV_RC_Carrier_46x32_v2.kicad_pcb` generated and assembled)
- ESP32-CAM flashed with `FPV_Car_DFPlayer_AutoResume.ino`
- All BOM components from `docs/BOM.md`

---

## Phase 1: Mechanical Assembly

### Step 1.1 — Rear Gearbox

1. Press two MR63ZZ bearings into the rear gearbox lower housing bearing seats
2. Insert 3 mm stainless steel rear axle (75 mm cut) through both bearings
3. Mount N20 metal gearmotor into the N20 pocket
4. Couple N20 output shaft to rear axle using 3 mm brass shaft coupler (tighten M3 grub screws)
5. Bolt rear gearbox upper cap with 4× M2 × 8 mm screws
6. **Test:** Spin rear wheels by hand — N20 gearbox should turn smoothly with zero binding

### Step 1.2 — Front Steering

1. Mount SG92R servo into the front steering bridge pocket
2. Assemble left and right steering knuckles onto M2 kingpin screws
3. Install knuckles into C-hub arms (kingpins through upper/lower arms)
4. Connect tie-rod from servo horn to both steering knuckles (adjustable M2 threaded rod)
5. **Test:** Move servo horn — both wheels should turn together symmetrically
6. Check: wheels turn ±40° without binding on C-hub arms

### Step 1.3 — Chassis Assembly

1. Mount rear gearbox assembly onto chassis belly pan (rear mount points)
2. Mount front steering bridge onto chassis (front mount points)
3. Install 2S 18650 battery into lower cradle (Y = 42–111 mm)
4. Install upper deck pillars (4× M2.5, Z = 37 mm)
5. Mount upper PCB/speaker deck onto pillars
6. **Test:** Place 500 g weight on center deck — zero axle flex

### Step 1.4 — Wheels & Tires

1. Mount PETG rims onto rear axle (3 mm D-shaft for rear, 3.18 mm bore for front)
2. Secure rear rims with M2.5 set-screw onto axle
3. Secure front rims with E-clips or washers on knuckle stub axles
4. Stretch TPU tires over rims until bead rib clicks into rim groove
5. **Test:** Roll car — wheels spin freely, tires don't slip on rims

### Step 1.5 — Body Shell

1. Snap body shell onto chassis rocker retention clips
2. Verify ESP32-CAM lens aligns with camera viewport
3. Verify headlight LEDs visible through bumper ports
4. **Test:** Body removes in 2 seconds for battery/SD card access

---

## Phase 2: Electronics Assembly

### Step 2.1 — PCB Population

1. Solder SMD 0805 passives (resistors, capacitors) per BOM
2. Solder RZ7889 SOIC-8 (bottom layer), MP1584EN, AO3400 MOSFETs
3. Solder through-hole JST-XH connectors (J1–J7), M2 mounting holes
4. Solder 470 µF capacitor C1 adjacent to ESP32-CAM 5V/GND
5. **Test:** Continuity check — no VCC→GND shorts on any rail

### Step 2.2 — Module Installation

1. Plug ESP32-CAM into top 1×8 female headers (align 5V/GND pins)
2. Plug JQ6500-16P or DFPlayer Mini into bottom headers
3. Plug MH-M18 Bluetooth module
4. Connect N20 motor to J2, servo to J3, speaker to J6
5. Connect battery to J1 via SS-12D00G3 switch

### Step 2.3 — Firmware Flash

1. Connect USB-TTL to J7 header (TX→GPIO3, RX→GPIO1, GND→GND)
2. Jumper GPIO 0 → GND (flash mode)
3. Upload `FPV_Car_DFPlayer_AutoResume.ino` (AI Thinker ESP32-CAM, 115200 baud)
4. Remove GPIO 0 jumper, reset
5. **Test:** Serial monitor shows "Setup complete. Ready." and AP `RC_FPV_CAR` broadcasts

### Step 2.4 — Audio Setup

1. Format MicroSD as FAT32 (≤32 GB)
2. Create `/mp3/` folder, copy: `0001.mp3` (horn), `0002.mp3` (engine), `0003.mp3+` (music)
3. Insert into DFPlayer Mini (or drag onto JQ6500-16P USB flash)
4. Pair phone to `RC_CAR_AUDIO` via MH-M18 Bluetooth

---

## Phase 3: Bring-Up & Test

### Step 3.1 — Power-On Smoke Test

```
[ ] Battery connected, switch ON
[ ] ESP32-CAM boots, Wi-Fi AP "RC_FPV_CAR" visible
[ ] 5V rail: 4.90–5.15 V (multimeter at ESP32-CAM header)
[ ] No components hot after 30 seconds
[ ] Serial: "Setup complete. Ready."
```

### Step 3.2 — Function Tests

```
[ ] GPIO 14 tap → motor forward, GPIO 15 tap → motor reverse
[ ] GPIO 13 tap → servo moves, GPIO 12 tap → horn sounds
[ ] WS connect → send {"T":100} → motor spins forward
[ ] WS connect → send {"S":-45} → steering full left
[ ] WS connect → send {"H":1} → horn over music
[ ] Telemetry → send {"C":"get"} → returns battery V, RSSI, uptime
```

### Step 3.3 — Full-Load Test (wheels off ground)

```
[ ] Full throttle forward → immediate reverse → steering L/R + horn
[ ] 5V rail never drops below 4.75 V
[ ] RZ7889 stays under 60 °C
[ ] Video stream stays connected (no brownout resets)
[ ] Failsafe: disconnect WS → motors stop within 250 ms
```

---

## Phase 4: Calibration

### Servo Center Calibration

1. Send `{"S":0}` — wheels should point straight
2. If not centered, adjust `servo_center` in firmware (default 4915)
3. Re-flash and retest

### Motor Deadzone Calibration

1. Send `{"T":5}` — motor should not move (deadzone default 12)
2. Adjust `motor_deadzone` until motor just starts at desired threshold
3. Volume changes auto-save to Preferences

---

## Safety Checklist (Before Every Session)

```
[ ] Battery voltage > 6.5 V (telemetry V reading)
[ ] No loose wires near moving parts
[ ] Wheels secured (set-screws tight, E-clips in place)
[ ] Body shell snapped on securely
[ ] Clear operating area (no people, pets, obstacles)
[ ] Fail-safe tested (disconnect WS → car stops)
```

---

## Estimated Build Time

| Phase | Time |
|-------|------|
| 3D printing (all parts) | 4–6 hours (printer time) |
| Mechanical assembly | 60–90 min |
| PCB population | 45–60 min |
| Firmware flash & config | 15 min |
| Bring-up & testing | 30 min |
| **Total** | **2.5–3.5 hours** |