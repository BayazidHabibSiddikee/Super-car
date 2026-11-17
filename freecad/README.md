# FreeCAD Mechanical Design — Supercar RC Car (Ferrari Enzo FPV v2)

Current-design macros for the ESP32-CAM FPV Ferrari Enzo RC car.
All superseded designs (Jeep, F40, single-piece shells, low-profile and
fixed assemblies) have been removed — this directory contains only the
active build.

## Files

| File | Generates | Purpose |
|------|-----------|---------|
| `Enzo_FPV_v2.py` | 34 parts in 8 `App::Part` modules | Ground-up rebuild v2: body shell, flush glass + angled headlights, chassis, Ackermann steering, 34 mm market wheels, dual N20 drivetrain, electronics + audio references — with a built-in interference checker |
| `FPV_RC_Direct_Print_Plate.py` | 15 parts flat at Z=0 | Master print plate: chassis, gearbox cap, decks, knuckles, tie-rod, pushrod, rims, TPU tires (earlier printed-wheel set; market wheels are now the default) |
| `run_gui.py` | — | GUI-mode batch runner (xvfb): produces GUI-openable `.FCStd` + STLs in one pass |
| `run_headless.py` | — | Console-only batch runner (FreeCADCmd); faster, but its `.FCStd` can show an empty tree in the GUI |

Generated artifacts live in `output/` (gitignored).

## Vehicle Specifications (v2)

| Parameter | Value |
|-----------|-------|
| Scale | ~1:22.4 (210 × 91 × 51.5 mm) — 34 mm market wheels are scale-correct |
| Wheelbase | 118 mm (rear axle Y=49, front axle Y=167) |
| Wheels | Off-the-shelf 34 mm × 15 mm N20 rubber wheels, 3 mm D-shaft hub |
| Rear drivetrain | 2× N20 motors (one per rear wheel), transverse, shaft straight into wheel |
| Front steering | SG92R servo + kingpin knuckles, Ackermann arms aimed at the rear axle |
| Chassis | Flat plate 3.5–5.5 mm + battery pillars, servo cradle, nose camera cradle |
| Electronics deck | Z = 25–26.6 mm above the 2S 18650 holder (battery top Z = 25) |
| Carrier PCB | 46 × 32 mm on-deck standoffs; ESP32-CAM nose camera on flex cable |
| Audio | 36 mm speaker in sealed box over rear axle, louvered engine cover |
| Glass | 0.5 mm clear PETG sheet glued into 1 mm rebates (windshield, side windows, headlight lenses) |

## Interference Check (built into the macro)

`Enzo_FPV_v2.py` runs a boolean intersection report over all critical
part pairs at the end of the build. Baseline result: **3 intentional
press-fits only** (body screw bosses into the shell, headlight buckets
into their pockets) — no real collisions. Wheels/knuckles/chassis are clean.

## How to Run

GUI-compatible batch (regenerates `.FCStd` + colors + view data + STLs):

```bash
cd <project root>
xvfb-run -a flatpak run org.freecad.FreeCAD freecad/run_gui.py
```

Console-only batch (faster, but GUI may show an empty tree):

```bash
flatpak run --command=FreeCADCmd org.freecad.FreeCAD -c "exec(open('freecad/run_headless.py').read())"
```

In the FreeCAD GUI: Macro → Macros... → select a script → Execute.

## Assembly Tree

```
Enzo_FPV_v2
├── 01_Body              Body_Shell, Exhaust_Tips
├── 02_Glass_And_Lights  Windshield_Glass, Side_Glass_L/R, Headlight_Lens_L/R,
│                        Headlight_Bucket_L/R (black reflector + 5mm LED bores)
├── 03_Chassis           Chassis (flat plate, pillars, motor tunnels, cradles)
├── 04_Steering          Knuckle_L/R, Tie_Rod (Ackermann)
├── 05_Wheels_34mm       Tyre + Hub ×4 (reference; buy the real wheels)
├── 06_Drivetrain_Ref    N20_Motor_L/R, Servo_SG92R_Ref, Servo_Horn_Ref
├── 07_Electronics_Ref   Battery_2S18650_Ref, Electronics_Deck, Carrier_PCB_46x32,
│                        ESP32CAM_Board_Ref, MH_M18_Ref, JQ6500_Ref, OV2640_Camera_Ref
└── 08_Audio             Speaker_Box_36mm, Speaker_36mm_Ref
```

## Print Settings by Part

| Part | Material | Walls | Infill | Notes |
|------|----------|-------|--------|-------|
| Body shell | Red PETG | 3 | 20% gyroid | Print upside-down on roof |
| Chassis | PETG | 4 | 40% gyroid | Structural |
| Steering knuckles | PETG | 4 | 40% gyroid | M2 kingpins |
| Speaker box | PETG | 3 | 25% | Sealed — check layer airtightness |
| Glass / lenses | 0.5 mm clear PETG sheet | — | — | Cut to STL outlines, glue with B-7000; do NOT print |
| Wheels | Buy: "34mm N20 Smart Car Robot Wheel (3mm D-shaft)" | — | — | No rubber printing |
