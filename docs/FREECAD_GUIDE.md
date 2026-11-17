# FreeCAD Mechanical Design Guide

Ferrari Enzo low-profile RC body — all scripts run inside FreeCAD via
Macro → Macros → Create → Execute (Ctrl+F6), or batch via
`freecad/run_gui.py` (GUI-openable output) / `freecad/run_headless.py`
(console-only). Print in PETG (PLA too brittle). Wheels are bought,
not printed.

## Prerequisites

- FreeCAD 1.0+ with `Part` workbench
- Units: mm
- Materials: PETG for structural/cosmetic parts; 0.5–1.0 mm clear PETG
  sheet (cut to shape, glued with B-7000) for glass and headlight lenses;
  off-the-shelf 34 × 15 mm N20 rubber wheels (3 mm D-shaft hub)

## Scripts

### `freecad/Ferrari_Enzo_Fixed_Assembly.py` — Full Enzo Assembly (Current Design)

Generates 22 validated solids organized into 6 `App::Part` containers:

- **01_Exterior_Body** — `Main_Body_Shell_Enzo` (38.5 mm tall × 74 mm wide,
  2 mm walls, outer-only wheel arches preserving the F1 nose, flush sloped
  window cutouts, rocker snap clips), `Rear_Diffuser_And_Exhaust`
  (5 strakes + quad exhaust)
- **02_Glass_And_Lights** — `Front_Windshield_Flush_Glass` (lofted along the
  22° canopy rake, Ø10.4 mm camera aperture), `Side_Glass_L/R` (26°
  tumblehome), `Headlight_Bucket_L/R` (black reflector housings with
  straight-ahead 5 mm LED bores), `Headlight_Clear_Lens_L/R` (flush covers
  following the 19.8° fender slope)
- **03_Chassis_And_Steering** — `Main_Chassis_Base` (2.5 mm belly pan, side
  rails, integrated rear N20 gearbox lower half with MR63ZZ bearing seats,
  SG92R servo pocket, front C-hub bridge), `Rear_Gearbox_Upper_Cap`
- **04_Market_Wheels_34mm** — hub + rubber tire reference solids (Ø34 ×
  15 mm) for fitment checking; buy the real wheels: "34mm N20 Smart Car
  Robot Wheel (3mm D-shaft)"
- **05_Audio_System** — `Sealed_Speaker_Enclosure_36mm` (~15.5 cm³ sealed
  chamber atop the rear gearbox, 36.2 mm bore, gasket seat)
- **06_Electronics_Deck** — `Low_Profile_PCB_Deck` at Z = 22 mm with 4× M2
  standoffs ON TOP, plus `Carrier_PCB_Top_Mounted_Ref` (46 × 32 mm board
  reference; ESP32-CAM lens lands at Z ≈ 33 mm through the windshield)

Key dimensions:
- Vehicle: 169 × 74 × 38.5 mm (~1:27 Enzo proportions)
- Wheelbase: 115 mm; chassis width: 54 mm (54.8 mm snap-fit cavity)
- Front track: 64 mm; rear gearbox span: 48 mm
- Every solid is `removeSplitter()`-refined and `isValid()`-checked

### `freecad/FPV_RC_Direct_Print_Plate.py` — Master Print Plate

Generates 15 mechanical parts laid flat at Z = 0 for direct slicing:
rear gearbox upper cap, main chassis base, upper audio + PCB deck,
steering knuckles L/R, Ackermann tie-rod, servo pushrod link, 4 rims,
4 TPU chevron-tread tires (34 mm Ø × 14 mm).

> Note: the print-plate rims/tires are the earlier printed-wheel set.
> The current build uses off-the-shelf 34 mm N20 rubber wheels instead —
> the rim/tire STLs can be skipped unless you want printed spares.

## Verification Checklist

- [ ] Part → Check Geometry (BOPCheck): 0 invalid shapes on all parts
- [ ] Dry-fit MR63ZZ bearings and N20 motor in rear gearbox
- [ ] Speaker drops into `Sealed_Speaker_Enclosure_36mm`
- [ ] 34 mm market wheels press onto 3 mm D-shaft axle and knuckle pins
      with full steering-lock clearance
- [ ] PCB seats on the 4 top-of-deck standoffs; camera aligned to the
      windshield aperture
- [ ] Cut glass/lens shapes from clear PETG sheet using the exported STL
      outlines; glue behind window openings with B-7000
- [ ] Spin rear wheels by hand: N20 gearbox turns smooth, zero binding
- [ ] Orient shell upside-down on roof for printing