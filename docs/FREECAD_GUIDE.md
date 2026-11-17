# FreeCAD Mechanical Design Guide

Ferrari Enzo FPV v2 RC car — all scripts run inside FreeCAD via
Macro → Macros → Create → Execute (Ctrl+F6), or batch via
`freecad/run_gui.py` (GUI-openable output) / `freecad/run_headless.py`
(console-only). Print in PETG (PLA too brittle). Wheels are bought,
not printed; glass is cut from clear PETG sheet.

## Prerequisites

- FreeCAD 1.0+ with `Part` workbench
- Units: mm
- Materials: PETG for printed parts; 0.5 mm clear PETG sheet (glued with
  B-7000) for glass and headlight lenses; off-the-shelf 34 × 15 mm N20
  rubber wheels (3 mm D-shaft hub)

## Scripts

### `freecad/Enzo_FPV_v2.py` — Ground-Up Rebuild v2 (Current Design)

Generates 34 validated solids in 8 `App::Part` containers. Axes:
X = left/right, Y = rear(0) → nose(210), Z = up (ground = 0).

- **01_Body** — `Body_Shell` (210 × 91 × 51.5 mm lofted BSpline shell,
  2.4 mm walls, round wheel arches for 34 mm wheels, tumblehome cabin,
  lowered center hood, engine-cover louvers, M2 screw bosses),
  `Exhaust_Tips`
- **02_Glass_And_Lights** — planar `Windshield_Glass`, `Side_Glass_L/R`
  (all lying flat in 1 mm rebates, 0.5 mm PETG), `Headlight_Lens_L/R`
  flush with the 32.7° fender slope, `Headlight_Bucket_L/R` black
  reflector housings with +Y 5 mm LED bores
- **03_Chassis** — flat plate (3.5–5.5 mm) with battery pillars, dual N20
  transverse motor tunnels at the rear axle, front fork + kingpin bridge,
  SG92R servo cradle, open nose camera cradle, body-screw holes
- **04_Steering** — `Knuckle_L/R` (kingpin pivots, Ackermann arms aimed at
  the rear axle center), `Tie_Rod`
- **05_Wheels_34mm** — tyre + hub reference solids ×4 (Ø34 × 15 mm market
  wheels: buy "34mm N20 Smart Car Robot Wheel (3mm D-shaft)")
- **06_Drivetrain_Ref** — `N20_Motor_L/R` (one per rear wheel, shaft
  straight into the wheel), `Servo_SG92R_Ref`, `Servo_Horn_Ref`
- **07_Electronics_Ref** — `Battery_2S18650_Ref`, `Electronics_Deck`
  (Z = 25–26.6), `Carrier_PCB_46x32`, `ESP32CAM_Board_Ref`, `MH_M18_Ref`,
  `JQ6500_Ref`, `OV2640_Camera_Ref` (nose camera on a flex cable)
- **08_Audio** — `Speaker_Box_36mm` (sealed, louvered lid hole),
  `Speaker_36mm_Ref`

Key dimensions:
- Scale ~1:22.4 (210 × 91 × 51.5 mm); wheelbase 118 mm
- Wheel inner face |X| = 29.5 mm (outer 44.5 mm); axle height Z = 17 mm
- Battery top Z = 25 mm; electronics deck directly above it

### Built-in interference checker

The macro ends with a boolean intersection report over all critical part
pairs. Baseline: **0.5 mm³ threshold — 3 intentional press-fits** (body
screw bosses, headlight buckets); wheels, knuckles, chassis, electronics
and audio are clean. Re-run after modifying any dimension.

### `freecad/FPV_RC_Direct_Print_Plate.py` — Master Print Plate

Generates 15 mechanical parts laid flat at Z = 0 for direct slicing:
rear gearbox upper cap, main chassis base, upper audio + PCB deck,
steering knuckles L/R, Ackermann tie-rod, servo pushrod link, 4 rims,
4 TPU chevron-tread tires (34 mm Ø × 14 mm).

> Note: the print-plate rims/tires are the earlier printed-wheel set.
> The current build uses off-the-shelf 34 mm N20 rubber wheels instead —
> the rim/tire STLs can be skipped unless you want printed spares.

## Verification Checklist

- [ ] Interference report: only the 3 intentional press-fit pairs
- [ ] Part → Check Geometry (BOPCheck): 0 invalid shapes on all parts
- [ ] 34 mm market wheels press onto the N20 shafts / kingpin pins with
      full steering-lock clearance
- [ ] PCB seats on the deck standoffs; OV2640 nose camera aligns with the
      Ø7.5 mm nose window
- [ ] Cut glass/lens shapes from clear PETG sheet using the exported STL
      outlines; glue into rebates with B-7000
- [ ] Speaker drops into `Speaker_Box_36mm` under the louvered cover
- [ ] Spin rear wheels by hand: motors turn smooth, zero binding
- [ ] Orient body shell upside-down on roof for printing
