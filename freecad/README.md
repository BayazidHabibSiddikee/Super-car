# FreeCAD Mechanical Design — Supercar RC Car (Ferrari Enzo)

Current-design macros for the ESP32-CAM FPV Ferrari Enzo RC car.
All older/superseded designs (Jeep Wrangler, F40, F40 Competizione,
single-piece Enzo shell, v1 chassis/gearbox/wheel scripts) have been
removed — this directory now contains only the active build.

## Files

| File | Generates | Purpose |
|------|-----------|---------|
| `Ferrari_Enzo_Fixed_Assembly.py` | 20 parts in 6 `App::Part` modules | Full modular Enzo: body shell, separate glass/lenses, chassis + steering, wheels/TPU tires, sealed 36 mm speaker enclosure + gasket, low-profile PCB deck |
| `FPV_RC_Direct_Print_Plate.py` | 15 parts flat at Z=0 | Master print plate: chassis, gearbox cap, decks, knuckles, tie-rod, pushrod, rims, TPU tires |

Generated artifacts live in `output/` (gitignored): 2 `.FCStd` documents
plus per-part `.stl` exports.

> **Important:** `output/*.FCStd` files are saved in **GUI mode** (via
> `run_gui.py`) so they embed `GuiDocument.xml` and open with full tree +
> colors in the FreeCAD GUI. `run_headless.py` (FreeCADCmd) is faster but
> produces console-saved files that can show an empty tree in the GUI —
> use it only when you will re-save or post-process headlessly.

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

GUI-compatible batch (regenerates `.FCStd` + colors + view data that open
correctly in the FreeCAD GUI):

```bash
cd <project root>
xvfb-run -a flatpak run org.freecad.FreeCAD freecad/run_gui.py
```

Console-only batch (faster, but GUI may show an empty tree):

```bash
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

## Assembly Tree

```
Ferrari_Enzo_Fixed_Assembly
├── 01_Exterior_Body        Main_Body_Shell_Enzo, Rear_Diffuser_And_Exhaust
├── 02_Glass_And_Lights     Flush windshield glass (camera aperture), tumbled side
│                           glass L/R, angled headlight buckets + clear lenses L/R
├── 03_Chassis_And_Steering Main_Chassis_Base, Rear_Gearbox_Upper_Cap
├── 04_Market_Wheels_34mm   4× hub + 4× rubber tire reference parts (buy
│                           "34mm N20 Smart Car Robot Wheel, 3mm D-shaft")
├── 05_Audio_System         Sealed_Speaker_Enclosure_36mm
└── 06_Electronics_Deck     Low_Profile_PCB_Deck (Z = 22 mm), Carrier_PCB_Top_Mounted_Ref
```

Key corrections over previous iterations:

- **PCB mounts ON TOP of the deck** (Z = 25.5 mm via 3.5 mm standoffs) —
  the space underneath is fully occupied by the 2S 18650 battery; the
  ESP32-CAM lens lands at Z ≈ 33 mm aimed through the windshield aperture
- **Flush sloped glass** — windshield lofted along the 22° canopy rake,
  side windows follow the 26° tumblehome, no flat boxes poking out
- **Angled headlight buckets** — black reflector housings recessed into the
  19.8° sloped front fenders with straight-ahead 5 mm LED bores and flush
  clear lenses; don't 3D-print glass — cut 0.5 mm clear PETG sheet to the
  exported STL outlines
- **Off-the-shelf 34 × 15 mm N20 rubber wheels** (3 mm D-shaft hub) — no
  TPU tire printing; wheel arches sized for full steering-lock clearance

Every solid is refined with `removeSplitter()` and validated with
`isValid()` — run Part → Check Geometry (BOPCheck) to confirm before printing.
