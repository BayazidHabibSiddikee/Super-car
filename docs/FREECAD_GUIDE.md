# FreeCAD Mechanical Design Guide

Ferrari Enzo low-profile RC body — all scripts run inside FreeCAD via
Macro → Macros → Create → Execute (Ctrl+F6), or headlessly via
`freecad/run_headless.py`. Print in PETG (PLA too brittle); 95A TPU for
tires and speaker gasket.

## Prerequisites

- FreeCAD 1.0+ with `Part` workbench
- Units: mm
- Materials: PETG for structural/cosmetic parts; 95A TPU for tires + gasket; clear 1.0–1.2 mm PETG/acrylic for glass inserts

## Scripts

### `freecad/Ferrari_Enzo_Modular_Assembly.py` — Full Modular Enzo Assembly

Generates 20 validated solids organized into 6 `App::Part` containers:

- **01_Exterior_Body** — `Main_Body_Shell_Enzo` (38.5 mm tall × 74 mm wide,
  2 mm walls, outer-only wheel arches preserving the F1 nose, recessed
  1.3 mm window seats, rocker snap clips), `Rear_Diffuser_And_Exhaust`
  (5 strakes + quad exhaust)
- **02_Glass_And_Lights** — `Front_Windshield_Clear_Insert` (Ø11 mm camera
  aperture), `Side_Glass_L/R`, `Headlight_Lens_L/R` (separate clear inserts)
- **03_Chassis_And_Steering** — `Main_Chassis_Base` (2.5 mm belly pan, side
  rails, integrated rear N20 gearbox lower half with MR63ZZ bearing seats,
  SG92R servo pocket, front C-hub bridge), `Rear_Gearbox_Upper_Cap`
- **04_Wheels_And_Tires** — 4 rims + 4 TPU tires positioned on the axles
- **05_Audio_System** — `Sealed_Speaker_Enclosure_36mm` (~15.5 cm³ sealed
  chamber atop the rear gearbox, 36.2 mm bore, 4× M2 bosses),
  `TPU_Speaker_Gasket`
- **06_Electronics_Deck** — `Low_Profile_PCB_Deck` at Z = 22 mm with 4×
  PCB standoff bosses

Key dimensions:
- Vehicle: 169 × 74 × 38.5 mm (~1:27 Enzo proportions)
- Wheelbase: 115 mm; chassis width: 54 mm (54.8 mm snap-fit cavity)
- Front track: 66 mm; rear gearbox span: 48 mm
- Every solid is `removeSplitter()`-refined and `isValid()`-checked

### `freecad/FPV_RC_Direct_Print_Plate.py` — Master Print Plate

Generates 15 mechanical parts laid flat at Z = 0 for direct slicing:
rear gearbox upper cap, main chassis base, upper audio + PCB deck,
steering knuckles L/R, Ackermann tie-rod, servo pushrod link, 4 rims,
4 TPU chevron-tread tires (34 mm Ø × 14 mm).

## Verification Checklist

- [ ] Part → Check Geometry (BOPCheck): 0 invalid shapes on all parts
- [ ] Dry-fit MR63ZZ bearings and N20 motor in rear gearbox
- [ ] Speaker drops into `Sealed_Speaker_Enclosure_36mm` with gasket seated
- [ ] Glass inserts fit the 1.3 mm recessed window seats
- [ ] Spin rear wheels by hand: N20 gearbox turns smooth, zero binding
- [ ] Export per-module STLs; orient shell upside-down on roof for printing