# FreeCAD Mechanical Design Guide

Source: `super car.pdf` FreeCAD Python macro sections. All scripts run inside FreeCAD via Macro → Macros → Create → paste → Execute (Ctrl+F6). Print in PETG/ABS (PLA too brittle for 500 g gearboxes).

## Prerequisites

- FreeCAD with `Part` workbench
- Units: mm
- Materials: PETG or ABS for structural parts; 95A TPU for tires

## Scripts

### `freecad/rc_gearboxes.py` — Rear N20 + Front SG92R Gearboxes

Generates 5 parts:
- `Rear_Gearbox_Lower` / `Rear_Gearbox_Upper` — split clamshell housing, N20 pocket 12.15 × 10.15 mm (+0.15 tolerance), dual MR63ZZ bearing seats (6.08 mm bore × 2.6 mm deep), 3 mm steel axle pass-through, M2 clamping holes
- `Front_Steering_Bridge` — 3 mm crossmember with SG92R pocket (23.1 × 12.5 mm), C-hub arms with M2 kingpin bores
- `Steering_Knuckle_Left` / `Steering_Knuckle_Right` — pivot knuckles with 3.2 mm axle bores, M2 kingpin pivots, 12° Ackermann tie-rod arms

Key dimensions:
- N20 motor pocket: 12.20 × 10.20 mm, depth 12–14 mm
- MR63ZZ seat: 6.05–6.10 mm Ø, 2.60 mm deep
- Rear span: 46 mm; front track: 64 mm
- Wall thickness: 3 mm

### `freecad/complete_chassis_v2.py` — Full 500 g Chassis + Upper Deck

Generates:
- `Main_Chassis_With_Gearboxes` — belly pan (3 mm), side rails (10 mm high), rear N20 + bearing gearbox integrated, front SG92R bridge, 2S 18650 cradle (Y=42→111 mm), front bumper with 15° camera cowl
- `Upper_PCB_And_Speaker_Deck` — at TRAY_Z = 37 mm, speaker ring (36 mm Ø), 4× M2 PCB standoffs, DFPlayer cutout window
- `Rear_Gearbox_Upper_Cap` — separate clamshell cap

Key dimensions:
- Wheelbase: 115 mm; chassis width: 54 mm; total length: ~157 mm
- Battery bay: 69 × 38 mm at Y=42→111
- Speaker: 36.5 mm Ø ring at rear of upper deck
- Tray Z raised to 37 mm for bottom-mounted DFPlayer clearance above 2S battery
- Pillars thickened to 3.5 mm radius for 500 g torsional stiffness

### `freecad/body_shell.py` — Snap-On Aerodynamic Body Shell

Generates `Aerodynamic_Car_Body_Shell`:
- Lofted outer profile, 2 mm walls, hollow interior
- Wheel arch cutouts: rear 20 mm Ø, front 22.5 mm Ø (±40° steering lock)
- FPV camera viewport (22 × 18 mm at Y=125, Z=46), dual headlight ports
- 5× roof louver vents above speaker (Y=51→69)
- Rear DFPlayer MicroSD access cutout
- Snap-on rocker retention clips under belly pan rails (Y=63→98)
- Rear spoiler wing (8° downforce)
- Roof Z = 65 mm (clears ESP32-CAM stack at 59.5 mm + 3.5 mm gap)

Print upside-down on roof; PETG, 0.2 mm layer, 3 walls, 20% infill; tree supports under spoiler only.

### `freecad/wheels_tires.py` — PETG Rims + TPU Tires

Generates 8 parts:
- `Rear_Drive_Rim_Left/Right` — 5-spoke PETG rim, 3 mm D-shaft bore with flat chord, M2.5 set-screw boss
- `Front_Steer_Rim_Left/Right` — 3.18 mm free-spin bore, retaining lip
- `TPU_Tire_1…4` — 34 mm Ø × 14 mm wide chevron-tread TPU tire with interlocking bead rib

Key dimensions:
- Tire OD: 34 mm (17 mm radius); clears body arches with 3 mm rear / 5.5 mm front clearance
- Rim OD: 24 mm; bead depth 1.2 mm
- Print rims: PETG, 4 walls, 40% gyroid, hub down
- Print tires: 95A TPU, 3 walls, 15% gyroid

## Verification Checklist

- [ ] Part → Check Geometry: 0 invalid shapes on all exported parts
- [ ] Dry-fit MR63ZZ bearings and N20 motor in rear lower shell
- [ ] 500 g weight on center deck: zero axle flex
- [ ] Spin rear wheels by hand: N20 gearbox turns smooth, zero binding
- [ ] Export each part as separate STL; orient for printing per script notes