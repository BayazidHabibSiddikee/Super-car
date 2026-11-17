# FreeCAD Mechanical Design — Supercar RC Car

Production-quality v2 FreeCAD Python macros for the Supercar ESP32-CAM FPV RC car.

## Files

| File | Generates | Purpose |
|------|-----------|---------|
| `rc_gearboxes.py` | 5 parts | Rear N20 + MR63ZZ gearbox, front SG92R + C-hub steering, Ackermann knuckles |
| `complete_chassis_v2.py` | 5 parts | Full 500 g chassis, upper deck, battery cradle, nose bumper |
| `body_shell.py` | 1 part | Snap-on aerodynamic body shell with wheel arches, camera viewport, spoiler |
| `wheels_tires.py` | 8 parts | PETG rims + TPU chevron treaded tires |

## Prerequisites

- FreeCAD 0.21+ with `Part` workbench
- Units: mm
- Materials: PETG or ABS for structural parts; 95A TPU for tires

## How to Run

1. Open FreeCAD
2. Macro → Macros... → Create
3. Paste the entire script, click Execute (Ctrl+F6)
4. Part Workbench → Check Geometry on each object (expect 0 invalid shapes)
5. File → Export → STL Mesh (*.stl) for each part
6. Slice: PETG, 0.2 mm layer, 4 walls/perimeters, 40% gyroid infill

## Quality Features (v2)

| Feature | Implementation |
|---------|---------------|
| Parameter validation | All scripts validate dimensions before building (raises on bad values) |
| Geometry check | Each script runs `checkGeometry()` on all outputs and reports pass/fail |
| Parametric | All dimensions in a `P` dict at the top — change one value, rebuild |
| Documented | Every build section has a comment block explaining purpose |

## Print Settings by Part

| Part | Material | Walls | Infill | Notes |
|------|----------|-------|--------|-------|
| Chassis belly pan + gearboxes | PETG/ABS | 4 | 40% gyroid | Structural, 500 g load |
| Upper deck + speaker deck | PETG | 3 | 20% gyroid | Electronics mounting |
| Body shell | PETG | 3 | 20% gyroid | Print upside-down on roof |
| Rims | PETG/ABS | 4 | 40% gyroid | Hub down on bed |
| Tires | 95A TPU | 3 | 15% gyroid | Stretch over rims |

## Assembly Order

1. Print all parts
2. Press MR63ZZ bearings into rear gearbox bearing seats
3. Insert 3 mm steel rear axle through bearings
4. Couple N20 motor to axle with 3 mm brass coupler
5. Bolt rear gearbox upper cap with 4× M2 screws
6. Mount SG92R servo in front bridge
7. Assemble steering knuckles with M2 kingpins
8. Install tie-rods between knuckles and servo horn
9. Snap body shell onto chassis rails
10. Mount TPU tires on PETG rims

## Key Dimensions

| Parameter | Value | Where |
|-----------|-------|-------|
| Wheelbase | 115 mm | `complete_chassis_v2.py` |
| Chassis width | 54 mm | `complete_chassis_v2.py` |
| Front track | 64-66 mm | `rc_gearboxes.py` / `complete_chassis_v2.py` |
| Rear span | 46-48 mm | `rc_gearboxes.py` / `complete_chassis_v2.py` |
| Tray Z height | 37 mm | `complete_chassis_v2.py` |
| Tire OD | 34 mm | `wheels_tires.py` |
| N20 motor pocket | 12.15 × 10.15 mm | `rc_gearboxes.py` |
| MR63ZZ bearing seat | 6.08 mm Ø | `rc_gearboxes.py` |