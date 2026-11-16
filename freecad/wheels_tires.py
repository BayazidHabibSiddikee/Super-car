#!/usr/bin/env python3
"""
wheels_tires.py — FreeCAD Python Macro
Supercar: PETG Wheel Rims + 95A TPU Treaded Tires
Rear: 3 mm D-shaft drive rims; Front: 3.18 mm free-spin rims; 4x matching tires.
Run: FreeCAD -> Macro -> Macros... -> Create -> paste -> Execute (Ctrl+F6)
"""

import FreeCAD as App
import Part
import math

doc = App.newDocument("RC_Car_Wheels_And_Tires_500g")

# ==========================================
# PARAMETRIC WHEEL & TIRE DIMENSIONS (mm)
# ==========================================
TIRE_OD     = 34.0              # 34.0 mm outer diameter (17.0 mm radius -> clears body arch)
TIRE_W      = 14.0              # 14.0 mm wide footprint for 500 g traction
RIM_OD      = 24.0              # 24.0 mm rigid PETG rim outer diameter
BEAD_DEPTH  = 1.2               # Interlocking tire-to-rim bead channel depth
BEAD_W      = 3.2               # Bead channel width

AXLE_D      = 3.05              # 3 mm steel axle snug fit
D_FLAT_OFFSET = 1.05            # D-shaft flat distance from center (2.57 mm flat chord)
SPOKE_COUNT = 5                 # 5-spoke reinforced structural rim

# ==========================================
# 1. RIGID PETG WHEEL RIM BUILDER
# ==========================================
def build_rim(name, is_rear_drive, x_pos, y_pos):
    rim_r = RIM_OD / 2.0

    # Outer Barrel Ring
    outer_cyl   = Part.makeCylinder(rim_r, TIRE_W)
    inner_barrel = Part.makeCylinder(rim_r - 2.4, TIRE_W + 2.0, App.Vector(0, 0, -1.0))
    barrel = outer_cyl.cut(inner_barrel)

    # Center Bead-Lock Groove around outer perimeter (prevents TPU tire rolling off)
    groove_outer = Part.makeCylinder(rim_r + 1.0, BEAD_W, App.Vector(0, 0, (TIRE_W - BEAD_W) / 2.0))
    groove_inner = Part.makeCylinder(rim_r - BEAD_DEPTH, BEAD_W, App.Vector(0, 0, (TIRE_W - BEAD_W) / 2.0))
    bead_groove = groove_outer.cut(groove_inner)
    barrel = barrel.cut(bead_groove)

    # Center Axle Hub Boss (Reinforced for 500 g radial load)
    hub_r  = 5.5 if is_rear_drive else 4.8
    hub_len = 13.0 if is_rear_drive else 10.5
    hub = Part.makeCylinder(hub_r, hub_len, App.Vector(0, 0, 0))

    # 5x Structural Spokes connecting Hub to Outer Barrel
    spokes = hub
    for i in range(SPOKE_COUNT):
        angle = i * (360.0 / SPOKE_COUNT)
        spoke = Part.makeBox(2.6, rim_r - 1.5, 4.0, App.Vector(-1.3, 0, 2.0))
        spoke.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), angle)
        spokes = spokes.fuse(spoke)

    rim = barrel.fuse(spokes)

    # Cut Center Axle Bore
    if is_rear_drive:
        # 3 mm D-Shaft Bore: cylinder intersected with a flat chord block
        cyl_bore = Part.makeCylinder(AXLE_D / 2.0, hub_len + 2.0, App.Vector(0, 0, -1.0))
        flat_cutter = Part.makeBox(6.0, 6.0, hub_len + 2.0,
                                   App.Vector(-3.0, D_FLAT_OFFSET, -1.0))
        d_bore = cyl_bore.cut(flat_cutter)
        rim = rim.cut(d_bore)

        # Radial M2.5 Set-Screw Hole into hub collar (locks onto round 3 mm steel axle)
        set_screw = Part.makeCylinder(
            1.05, hub_r + 2.0,
            App.Vector(0, 0, hub_len - 2.8),
            App.Vector(0, -1, 0))
        rim = rim.cut(set_screw)
    else:
        # Smooth 3.18 mm Free-Spinning Bore for Front Steering Knuckle Stub Axle
        free_bore = Part.makeCylinder(3.18 / 2.0, hub_len + 2.0, App.Vector(0, 0, -1.0))
        rim = rim.cut(free_bore)

    rim.translate(App.Vector(x_pos, y_pos, 0))
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = rim

# ==========================================
# 2. FLEXIBLE 95A TPU TREADED TIRE BUILDER
# ==========================================
def build_treaded_tire(name, x_pos, y_pos):
    tire_r = TIRE_OD / 2.0
    rim_r  = (RIM_OD / 2.0) - 0.1   # -0.1 mm interference fit so TPU grips rim tightly

    # Base Tire Carcass (Smooth crown prior to cutting tread grooves)
    carcass  = Part.makeCylinder(tire_r, TIRE_W)
    inner_bore = Part.makeCylinder(rim_r, TIRE_W + 2.0, App.Vector(0, 0, -1.0))
    tire = carcass.cut(inner_bore)

    # Inner Locking Bead Rib (snaps into rim perimeter channel)
    rib_outer = Part.makeCylinder(rim_r + 0.5, BEAD_W - 0.2,
                                  App.Vector(0, 0, (TIRE_W - (BEAD_W - 0.2)) / 2.0))
    rib_inner = Part.makeCylinder(rim_r - BEAD_DEPTH + 0.15, BEAD_W - 0.2,
                                  App.Vector(0, 0, (TIRE_W - (BEAD_W - 0.2)) / 2.0))
    bead_rib = rib_outer.cut(rib_inner)
    tire = tire.fuse(bead_rib)

    # Subtle Sidewall Chamfers for Realistic Scale Profile
    chamfer_bot  = Part.makeCone(tire_r + 1.0, tire_r - 1.2, 1.5, App.Vector(0, 0, -0.1))
    chamfer_bot_in = Part.makeCylinder(tire_r - 1.2, 2.0, App.Vector(0, 0, -0.2))
    tire = tire.cut(chamfer_bot.cut(chamfer_bot_in))

    chamfer_top  = Part.makeCone(tire_r - 1.2, tire_r + 1.0, 1.5, App.Vector(0, 0, TIRE_W - 1.4))
    chamfer_top_in = Part.makeCylinder(tire_r - 1.2, 2.0, App.Vector(0, 0, TIRE_W - 1.5))
    tire = tire.cut(chamfer_top.cut(chamfer_top_in))

    # Cut 16x Directional Chevron / Off-Road Tread Grooves around circumference
    tread_count   = 16
    groove_depth  = 1.1
    for i in range(tread_count):
        angle = i * (360.0 / tread_count)

        # Left angled tread groove
        g_left = Part.makeBox(groove_depth + 1.0, 1.8, TIRE_W * 0.55,
                              App.Vector(tire_r - groove_depth, -0.9, 0))
        g_left.rotate(App.Vector(tire_r, 0, TIRE_W * 0.25), App.Vector(1, 0, 0), 25.0)
        g_left.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), angle)

        # Right angled tread groove (staggered chevron)
        g_right = Part.makeBox(groove_depth + 1.0, 1.8, TIRE_W * 0.55,
                               App.Vector(tire_r - groove_depth, -0.9, 0))
        g_right.rotate(App.Vector(tire_r, 0, TIRE_W * 0.75), App.Vector(1, 0, 0), -25.0)
        g_right.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), angle + (180.0 / tread_count))

        tire = tire.cut(g_left).cut(g_right)

    tire.translate(App.Vector(x_pos, y_pos, 0))
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = tire

# ==========================================
# GENERATE 8 PARTS: 4 RIMS + 4 TIRES
# ==========================================
build_rim("Rear_Drive_Rim_Left",  True,  -45.0,  25.0)
build_rim("Rear_Drive_Rim_Right", True,   45.0,  25.0)
build_rim("Front_Steer_Rim_Left", False, -45.0, -25.0)
build_rim("Front_Steer_Rim_Right",False,  45.0, -25.0)

build_treaded_tire("TPU_Tire_1", -90.0,  25.0)
build_treaded_tire("TPU_Tire_2",  90.0,  25.0)
build_treaded_tire("TPU_Tire_3", -90.0, -25.0)
build_treaded_tire("TPU_Tire_4",  90.0, -25.0)

doc.recompute()
if App.GuiUp:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewAxonometric()
    Gui.SendMsgToActiveView("ViewFit")

print("wheels_tires.py: 8 parts generated ->")
print("  Rear_Drive_Rim_Left/Right, Front_Steer_Rim_Left/Right")
print("  TPU_Tire_1..4")
print("  Rims: PETG, 4 walls, 40% gyroid, hub down")
print("  Tires: 95A TPU, 3 walls, 15% gyroid")