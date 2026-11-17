# FreeCAD Mechanical Design — Supercar RC Car (Ferrari Enzo)

Current-design macros for the ESP32-CAM FPV Ferrari Enzo RC car.
All older/superseded designs (Jeep Wrangler, F40, F40 Competizione,
single-piece Enzo shell, v1 chassis/gearbox/wheel scripts) have been
removed — this directory now contains only the active build.

## Files

| File | Generates | Purpose |
|------|-----------|---------|
| `Ferrari_Enzo_Modular_Assembly.py` | 20 parts in 6 `App::Part` modules | Full modular Enzo: body shell, separate glass/lenses, chassis + steering, wheels/TPU tires, sealed 36 mm speaker enclosure + gasket, low-profile PCB deck |
| `FPV_RC_Direct_Print_Plate.py` | 15 parts flat at Z=0 | Master print plate: chassis, gearbox cap, decks, knuckles, tie-rod, pushrod, rims, TPU tires |

Generated artifacts live in `output/` (gitignored): 2 `.FCStd` documents
plus per-part `.stl` exports.

## Vehicle Specifications

| Parameter | Value |
|-----------|-------|
| Length × Width × Height | 169 × 74 × 38.5 mm (~1:27 Enzo proportions) |
| Wheelbase | 115 mm |
| Chassis width | 54 mm (54.8 mm snap-fit cavity) |
| Electronics deck height | 22 mm (above 2S 18650 battery) |
| Speaker | 36 mm 3 W 4 Ω in sealed ~15.5 cm³ chamber atop rear gearbox |
| Rear drivetrain | N20 motor + MR63ZZ bearings, 48 mm span gearbox |
| Front steering | SG92R servo, Ackermann C-hub linkage, 66 mm track |

## How to Run

Headless batch (regenerates all `.FCStd` + `.stl`):

```bash
cd <project root>
flatpak run --command=FreeCADCmd org.freecad.FreeCAD -c "exec(open('freecad/run_headless.py').read())"
```

In the FreeCAD GUI: Macro → Macros... → select a script → Execute.

## Print Settings by Part

| Part | Material | Walls | Infill | Notes |
|------|----------|-------|--------|-------|
| Main body shell | Red PETG | 3 | 20% gyroid | Print upside-down on roof |
| Glass / lens inserts | Clear PETG 1.0–1.2 mm sheet or print | 3 | 100% | Cut to fit recessed seats |
| Chassis, gearbox, decks | PETG | 4 | 40% gyroid | Structural |
| Speaker enclosure | PETG | 3 | 25% | Sealed — check layer airtightness |
| TPU gasket / tires | 95A TPU | 3 | 15% gyroid | |
| Rims | PETG | 4 | 40% gyroid | Hub down on bed |

## Modular Assembly Tree

```
Ferrari_Enzo_Modular_Assembly
├── 01_Exterior_Body       Main_Body_Shell_Enzo, Rear_Diffuser_And_Exhaust
├── 02_Glass_And_Lights    Windshield insert, side glass L/R, headlight lenses L/R
├── 03_Chassis_And_Steering Main_Chassis_Base, Rear_Gearbox_Upper_Cap
├── 04_Wheels_And_Tires    4× rims + 4× TPU tires (on-axle positions)
├── 05_Audio_System        Sealed_Speaker_Enclosure_36mm, TPU_Speaker_Gasket
└── 06_Electronics_Deck    Low_Profile_PCB_Deck (Z = 22 mm)
```

Every solid is refined with `removeSplitter()` and validated with
`isValid()` — run Part → Check Geometry (BOPCheck) to confirm before printing.
