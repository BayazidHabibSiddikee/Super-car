#!/usr/bin/env python3
"""
rc_gearboxes.py — FreeCAD Python Macro
Supercar: Rear N20 + MR63ZZ Bearing Gearbox + Front SG92R Steering Gearbox
Sized for a 500 g chassis payload.
Run: FreeCAD -> Macro -> Macros... -> Create -> paste -> Execute (Ctrl+F6)
"""

import FreeCAD as App
import Part
import math

doc = App.newDocument("RC_Car_Gearboxes_500g")

# ==========================================
# PARAMETRIC DIMENSIONS (in mm)
# ==========================================
TOL = 0.15                  # 3D printing clearance tolerance
WALL = 3.0                  # Heavy-duty wall thickness for 500 g load

# Rear N20 + MR63ZZ Bearing Gearbox
N20_W  = 12.0 + TOL         # 12.15 mm
N20_H  = 10.0 + TOL         # 10.15 mm
N20_L  = 16.0               # Gearbox + rear motor support length
COUPLER_BAY_L = 14.0        # Space for 3 mm-to-3 mm shaft coupler or spur gear
BEARING_OD  = 6.0 + 0.08    # MR63ZZ outer diameter (6.08 mm snug press-fit)
BEARING_W   = 2.6           # MR63ZZ width (2.5 mm + 0.1 mm clearance)
AXLE_CLEARANCE = 3.3        # 3 mm steel rod pass-through
REAR_SPAN   = 46.0          # Total width across rear bearing bosses

# Front SG92R + C-Hub Steering Gearbox
SERVO_L  = 23.1 + TOL       # SG92R body length (23.25 mm)
SERVO_W  = 12.5 + TOL       # SG92R body width (12.65 mm)
SERVO_H  = 16.0             # Pocket depth
FRONT_TRACK = 64.0          # Distance between left & right kingpin pivots
CHUB_GAP  = 14.0            # Vertical opening inside C-hub
CHUB_ARM_T = 3.5            # Thickness of upper/lower C-hub arms
KINGPIN_D = 2.1             # M2 screw pivot hole

# ==========================================
# 1. REAR GEARBOX (N20 + DUAL MR63ZZ)
# ==========================================
def build_rear_gearbox():
    gb_len = N20_L + COUPLER_BAY_L + (WALL * 2)
    gb_w   = REAR_SPAN
    gb_h   = N20_H + (WALL * 2)          # 16.15 mm total height
    z_center = gb_h / 2.0

    # Main solid block centered on X, starting at Y=0
    body = Part.makeBox(gb_w, gb_len, gb_h,
                        App.Vector(-gb_w / 2.0, 0, 0))

    # Cut N20 Motor Pocket (from Y = WALL to Y = WALL + N20_L)
    n20_pocket = Part.makeBox(
        N20_W, N20_L, N20_H,
        App.Vector(-N20_W / 2.0, WALL, z_center - N20_H / 2.0)
    )

    # Cut Wire Slot at Rear Wall
    wire_slot = Part.makeBox(
        6.0, WALL + 1.0, 4.0,
        App.Vector(-3.0, -0.5, z_center - 2.0)
    )

    # Cut Center Coupler / Gear Cavity
    coupler_y = WALL + N20_L
    coupler_pocket = Part.makeBox(
        16.0, COUPLER_BAY_L, 12.0,
        App.Vector(-8.0, coupler_y, z_center - 6.0)
    )

    # Axle Axis Position (Y-center of coupler bay)
    axle_y = coupler_y + (COUPLER_BAY_L / 2.0)

    # Cut 3 mm Axle Pass-Through Hole across entire width
    axle_hole = Part.makeCylinder(
        AXLE_CLEARANCE / 2.0, gb_w + 2.0,
        App.Vector(-gb_w / 2.0 - 1.0, axle_y, z_center),
        App.Vector(1, 0, 0)
    )

    # Cut Left & Right MR63ZZ Bearing Pockets on outer walls
    left_bearing = Part.makeCylinder(
        BEARING_OD / 2.0, BEARING_W + 0.5,
        App.Vector(-gb_w / 2.0 - 0.5, axle_y, z_center),
        App.Vector(1, 0, 0)
    )
    right_bearing = Part.makeCylinder(
        BEARING_OD / 2.0, BEARING_W + 0.5,
        App.Vector(gb_w / 2.0 - BEARING_W, axle_y, z_center),
        App.Vector(1, 0, 0)
    )

    # Cut 4x M2 Clamping Screw Holes through Z-axis
    screw_holes = []
    for sx in [-gb_w / 2.0 + 4.0, gb_w / 2.0 - 4.0]:
        for sy in [5.0, gb_len - 5.0]:
            sh = Part.makeCylinder(1.05, gb_h + 2.0, App.Vector(sx, sy, -1.0))
            screw_holes.append(sh)

    # Subtract all cavities
    full_rear = body.cut(n20_pocket).cut(wire_slot).cut(coupler_pocket)
    full_rear = full_rear.cut(axle_hole).cut(left_bearing).cut(right_bearing)
    for sh in screw_holes:
        full_rear = full_rear.cut(sh)

    # Split into Lower Half and Upper Clamshell Cap along Z = z_center
    lower_cutter = Part.makeBox(gb_w + 10, gb_len + 10, gb_h,
                                App.Vector(-gb_w / 2.0 - 5, -5, z_center))
    upper_cutter = Part.makeBox(gb_w + 10, gb_len + 10, gb_h,
                                App.Vector(-gb_w / 2.0 - 5, -5, z_center - gb_h))

    rear_lower = full_rear.cut(lower_cutter)
    rear_upper = full_rear.cut(upper_cutter)

    obj_low = doc.addObject("Part::Feature", "Rear_Gearbox_Lower")
    obj_low.Shape = rear_lower

    obj_up = doc.addObject("Part::Feature", "Rear_Gearbox_Upper")
    obj_up.Shape = rear_upper
    obj_up.Placement.Base = App.Vector(0, 0, 12.0)   # Offset upward for clear view

# ==========================================
# 2. FRONT STEERING BRIDGE (SG92R + C-HUBS)
# ==========================================
def build_front_steering():
    y_offset = 65.0           # Place in front of rear gearbox in document view
    bridge_w = FRONT_TRACK + 8.0
    bridge_d = 18.0
    total_h  = CHUB_GAP + (CHUB_ARM_T * 2)   # 21.0 mm total height

    # Base Crossmember Plate
    base_plate = Part.makeBox(bridge_w, bridge_d, CHUB_ARM_T,
                              App.Vector(-bridge_w / 2.0, y_offset, 0))

    # Central SG92R Servo Mount Block
    servo_block_w = SERVO_L + 10.0
    servo_block_d = SERVO_W + (WALL * 2)
    servo_block = Part.makeBox(
        servo_block_w, servo_block_d, SERVO_H,
        App.Vector(-servo_block_w / 2.0, y_offset, 0)
    )
    servo_pocket = Part.makeBox(
        SERVO_L, SERVO_W, SERVO_H + 1.0,
        App.Vector(-SERVO_L / 2.0, y_offset + WALL, 2.0)
    )

    # Servo mounting ear screw holes (M2)
    ear_hole_l = Part.makeCylinder(0.9, 10.0,
        App.Vector(-SERVO_L / 2.0 - 2.5, y_offset + WALL + SERVO_W / 2.0, SERVO_H / 2.0))
    ear_hole_r = Part.makeCylinder(0.9, 10.0,
        App.Vector(SERVO_L / 2.0 + 2.5, y_offset + WALL + SERVO_W / 2.0, SERVO_H / 2.0))

    servo_mount = servo_block.cut(servo_pocket).cut(ear_hole_l).cut(ear_hole_r)

    # Outer Left & Right C-Hub Uprights + Top Arms
    chubs = []
    for side in [-1, 1]:
        x_pivot = side * (FRONT_TRACK / 2.0)
        # Vertical C-hub backing column (set inward by 5 mm so knuckle swings freely)
        col_x = x_pivot - (side * 6.5) - 2.0
        col = Part.makeBox(4.0, 12.0, total_h,
                           App.Vector(col_x, y_offset + 3.0, 0))

        # Top C-Hub Arm extending over kingpin
        arm_x = min(col_x, x_pivot - 4.0)
        arm_w = abs(x_pivot - col_x) + 4.5
        top_arm = Part.makeBox(arm_w, 12.0, CHUB_ARM_T,
                               App.Vector(arm_x, y_offset + 3.0, total_h - CHUB_ARM_T))

        # Vertical M2 Kingpin Hole through top and bottom C-hub arms
        kp_hole = Part.makeCylinder(KINGPIN_D / 2.0, total_h + 2.0,
                                    App.Vector(x_pivot, y_offset + 9.0, -1.0))
        chubs.append(col.fuse(top_arm).cut(kp_hole))

    front_bridge = base_plate.fuse(servo_mount).fuse(chubs[0]).fuse(chubs[1])

    # Re-cut kingpin holes cleanly through base plate
    for side in [-1, 1]:
        kp_hole = Part.makeCylinder(KINGPIN_D / 2.0, total_h + 2.0,
                                    App.Vector(side * (FRONT_TRACK / 2.0), y_offset + 9.0, -1.0))
        front_bridge = front_bridge.cut(kp_hole)

    obj_front = doc.addObject("Part::Feature", "Front_Steering_Bridge")
    obj_front.Shape = front_bridge

# ==========================================
# 3. FRONT STEERING KNUCKLES (LEFT & RIGHT)
# ==========================================
def build_knuckle(name, side, x_pos, y_pos):
    knuckle_h = CHUB_GAP - 0.6     # 0.3 mm top/bottom clearance inside C-hub
    z_base    = CHUB_ARM_T + 0.3

    # Main Kingpin Barrel
    barrel = Part.makeCylinder(4.2, knuckle_h,
                               App.Vector(x_pos, y_pos, z_base))
    kp_bore = Part.makeCylinder(KINGPIN_D / 2.0, knuckle_h + 2.0,
                                App.Vector(x_pos, y_pos, z_base - 1.0))

    # Outward Front Wheel Stub Axle Boss (for 3 mm steel wheel pin or MR63ZZ bearing)
    stub = Part.makeCylinder(
        4.5, 10.0,
        App.Vector(x_pos, y_pos, z_base + knuckle_h / 2.0),
        App.Vector(side, 0, 0)
    )
    stub_bore = Part.makeCylinder(
        1.55, 11.0,             # 3.1 mm bore for 3 mm steel front wheel axle pin
        App.Vector(x_pos, y_pos, z_base + knuckle_h / 2.0),
        App.Vector(side, 0, 0)
    )

    # Rearward Ackermann Steering Arm (angled 12 deg inward)
    arm_len = 13.0
    arm = Part.makeBox(3.2, arm_len, 3.5, App.Vector(-1.6, -arm_len, 0))
    arm.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), side * 12.0)
    arm.translate(App.Vector(x_pos, y_pos, z_base + 1.5))

    # Tie-rod ball/screw hole at tip of Ackermann arm
    tip_x = x_pos + side * (arm_len - 2.2) * math.sin(math.radians(12.0))
    tip_y = y_pos - (arm_len - 2.2) * math.cos(math.radians(12.0))
    tie_hole = Part.makeCylinder(0.85, 6.0, App.Vector(tip_x, tip_y, z_base))

    knuckle = barrel.fuse(stub).fuse(arm).cut(kp_bore).cut(stub_bore).cut(tie_hole)
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = knuckle

# ==========================================
# BUILD ALL
# ==========================================
build_rear_gearbox()
build_front_steering()
build_knuckle("Steering_Knuckle_Left",  -1, -FRONT_TRACK / 2.0 - 14.0, 74.0)
build_knuckle("Steering_Knuckle_Right",  1,  FRONT_TRACK / 2.0 + 14.0, 74.0)

doc.recompute()
if App.GuiUp:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewAxonometric()
    Gui.SendMsgToActiveView("ViewFit")

print("rc_gearboxes.py: 5 parts generated ->")
print("  Rear_Gearbox_Lower, Rear_Gearbox_Upper,")
print("  Front_Steering_Bridge, Steering_Knuckle_Left, Steering_Knuckle_Right")