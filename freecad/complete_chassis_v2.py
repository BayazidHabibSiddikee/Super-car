#!/usr/bin/env python3
"""
complete_chassis_v2.py — FreeCAD Python Macro
Supercar: Complete 500 g Rolling Chassis + Upper Deck
Integrated rear N20 + dual MR63ZZ gearbox, front SG92R + C-hub steering,
2S 18650 battery bay, 3 W speaker acoustic deck, carrier PCB standoffs,
15 deg forward-tilted ESP32-CAM nose mount.
Run: FreeCAD -> Macro -> Macros... -> Create -> paste -> Execute (Ctrl+F6)
"""

import FreeCAD as App
import Part
import math

doc = App.newDocument("Complete_FPV_RC_Chassis_500g_v2")

# ==========================================
# MASTER CHASSIS & HARDWARE PARAMETERS (mm)
# ==========================================
TOL        = 0.15
FLOOR_T    = 3.0               # Heavy-duty 3 mm structural belly pan for 500 g load
WHEELBASE  = 115.0             # Front axle to Rear axle distance
CHASSIS_W  = 54.0              # Main center deck width

# Updated Upper Deck Height for 2S 18650 + Bottom DFPlayer Mini Clearance
TRAY_Z     = 37.0              # Raised from 23.0 mm -> 37.0 mm (13.5 mm clear above 2S battery)
PILLAR_R   = 3.5               # Thickened 7 mm diameter pillars for 500 g torsional stiffness

# Rear N20 + Dual MR63ZZ Bearing Gearbox
N20_W       = 12.0 + TOL
N20_H       = 10.0 + TOL
N20_L       = 16.0
COUPLER_BAY_L = 14.0
BEARING_OD  = 6.08             # MR63ZZ press-fit (6.0 mm + 0.08 mm)
BEARING_W   = 2.6
AXLE_D      = 3.3              # 3 mm steel rod clearance
REAR_SPAN   = 48.0

# Front SG92R + C-Hub Steering Bridge
SERVO_L   = 23.1 + TOL
SERVO_W   = 12.5 + TOL
SERVO_H   = 15.5
FRONT_TRACK = 66.0
CHUB_GAP  = 14.0
CHUB_ARM_T = 3.5
KINGPIN_D = 2.1                # M2 kingpin screw hole

# Payload Bays (2S 18650 Battery, Speaker, Carrier PCB, ESP32-CAM)
BAT_L   = 69.0                 # 2S 18650 holder length
BAT_W   = 38.0                 # 2S 18650 holder width
SPK_D   = 36.5                 # 36 mm round 3 W speaker diameter
PCB_L   = 46.0                 # Carrier PCB length
PCB_W   = 32.0                 # Carrier PCB width

# ==========================================
# 1. INTEGRATED BASE CHASSIS + GEARBOX HOUSINGS
# ==========================================
def build_complete_base():
    rear_y0   = 0.0
    gb_len    = N20_L + COUPLER_BAY_L + 6.0
    axle_y    = rear_y0 + 3.0 + N20_L + (COUPLER_BAY_L / 2.0)   # Y = 27.0 mm
    front_y0  = axle_y + WHEELBASE - 9.0                        # Y = 133.0 mm
    total_len = front_y0 + 24.0                                 # ~157 mm total length

    # --- A. Main Center Belly Pan + Side Stiffener Rails ---
    deck   = Part.makeBox(CHASSIS_W, total_len - 10.0, FLOOR_T,
                          App.Vector(-CHASSIS_W / 2.0, 5.0, 0))
    rail_l = Part.makeBox(3.5, total_len - 25.0, 10.0,
                          App.Vector(-CHASSIS_W / 2.0, 15.0, 0))
    rail_r = Part.makeBox(3.5, total_len - 25.0, 10.0,
                          App.Vector(CHASSIS_W / 2.0 - 3.5, 15.0, 0))
    chassis = deck.fuse(rail_l).fuse(rail_r)

    # --- B. Integrated Rear N20 + Bearing Gearbox Lower Housing ---
    gb_h = N20_H + 6.0
    z_axle = gb_h / 2.0
    rear_block = Part.makeBox(REAR_SPAN, gb_len, gb_h,
                              App.Vector(-REAR_SPAN / 2.0, rear_y0, 0))

    n20_pocket = Part.makeBox(
        N20_W, N20_L, N20_H,
        App.Vector(-N20_W / 2.0, rear_y0 + 3.0, z_axle - N20_H / 2.0)
    )
    wire_slot = Part.makeBox(
        6.0, 4.0, 4.0,
        App.Vector(-3.0, -0.5, z_axle - 2.0)
    )
    coupler_bay = Part.makeBox(
        16.0, COUPLER_BAY_L, 12.0,
        App.Vector(-8.0, rear_y0 + 3.0 + N20_L, z_axle - 6.0)
    )
    axle_hole = Part.makeCylinder(
        AXLE_D / 2.0, REAR_SPAN + 2.0,
        App.Vector(-REAR_SPAN / 2.0 - 1.0, axle_y, z_axle),
        App.Vector(1, 0, 0)
    )
    brg_l = Part.makeCylinder(
        BEARING_OD / 2.0, BEARING_W + 0.5,
        App.Vector(-REAR_SPAN / 2.0 - 0.5, axle_y, z_axle),
        App.Vector(1, 0, 0)
    )
    brg_r = Part.makeCylinder(
        BEARING_OD / 2.0, BEARING_W + 0.5,
        App.Vector(REAR_SPAN / 2.0 - BEARING_W, axle_y, z_axle),
        App.Vector(1, 0, 0)
    )

    full_rear = (rear_block.cut(n20_pocket).cut(wire_slot)
                 .cut(coupler_bay).cut(axle_hole).cut(brg_l).cut(brg_r))
    for sx in [-REAR_SPAN / 2.0 + 4.0, REAR_SPAN / 2.0 - 4.0]:
        for sy in [5.0, gb_len - 5.0]:
            full_rear = full_rear.cut(
                Part.makeCylinder(1.05, gb_h + 2.0,
                                  App.Vector(sx, sy, -1.0)))

    # Split Rear Gearbox at Z = z_axle (Lower fuses to chassis; Upper is separate cap)
    rear_lower = full_rear.cut(
        Part.makeBox(REAR_SPAN + 10, gb_len + 10, gb_h,
                     App.Vector(-REAR_SPAN / 2 - 5, -5, z_axle)))
    rear_upper = full_rear.cut(
        Part.makeBox(REAR_SPAN + 10, gb_len + 10, gb_h,
                     App.Vector(-REAR_SPAN / 2 - 5, -5, z_axle - gb_h)))

    chassis = chassis.fuse(rear_lower)

    # --- C. 2S 18650 Battery Retention Cradle (Y = 42 to 111 mm) ---
    bat_y0 = 42.0
    bat_wall_l = Part.makeBox(2.5, BAT_L, 12.0,
                              App.Vector(-BAT_W / 2.0 - 2.5, bat_y0, FLOOR_T))
    bat_wall_r = Part.makeBox(2.5, BAT_L, 12.0,
                              App.Vector(BAT_W / 2.0, bat_y0, FLOOR_T))
    bat_stop = Part.makeBox(BAT_W + 5.0, 2.5, 10.0,
                            App.Vector(-BAT_W / 2.0 - 2.5,
                                       bat_y0 + BAT_L, FLOOR_T))
    chassis = chassis.fuse(bat_wall_l).fuse(bat_wall_r).fuse(bat_stop)

    # --- D. Reinforced Upper Deck Pillars (Z = 3.0 to 37.0 mm) ---
    tray_y0  = 38.0
    tray_len = 90.0
    for px in [-CHASSIS_W / 2.0 + 3.5, CHASSIS_W / 2.0 - 3.5]:
        for py in [tray_y0 + 4.0, tray_y0 + tray_len - 4.0]:
            pillar = Part.makeCylinder(
                PILLAR_R, TRAY_Z - FLOOR_T,
                App.Vector(px, py, FLOOR_T))
            # Wide base reinforcement collar for high-speed crash durability
            collar = Part.makeCylinder(
                PILLAR_R + 1.5, 6.0,
                App.Vector(px, py, FLOOR_T))
            # M2.5 screw pilot hole at top of pillar
            top_hole = Part.makeCylinder(
                1.05, 8.0,
                App.Vector(px, py, TRAY_Z - 7.5))
            chassis = chassis.fuse(pillar).fuse(collar).cut(top_hole)

    # --- E. Integrated Front SG92R Servo + C-Hub Steering Crossmember ---
    bridge_w  = FRONT_TRACK + 8.0
    bridge_d  = 18.0
    total_chub_h = CHUB_GAP + (CHUB_ARM_T * 2)
    front_plate = Part.makeBox(bridge_w, bridge_d, CHUB_ARM_T,
                               App.Vector(-bridge_w / 2.0, front_y0, 0))

    servo_blk_w = SERVO_L + 10.0
    servo_blk_d = SERVO_W + 6.0
    servo_blk = Part.makeBox(
        servo_blk_w, servo_blk_d, SERVO_H,
        App.Vector(-servo_blk_w / 2.0, front_y0, 0))
    servo_pkt = Part.makeBox(
        SERVO_L, SERVO_W, SERVO_H + 1.0,
        App.Vector(-SERVO_L / 2.0, front_y0 + 3.0, 2.0))
    ear_l = Part.makeCylinder(
        0.9, 10.0,
        App.Vector(-SERVO_L / 2.0 - 2.5, front_y0 + 3.0 + SERVO_W / 2.0, SERVO_H / 2.0))
    ear_r = Part.makeCylinder(
        0.9, 10.0,
        App.Vector(SERVO_L / 2.0 + 2.5, front_y0 + 3.0 + SERVO_W / 2.0, SERVO_H / 2.0))
    servo_mnt = servo_blk.cut(servo_pkt).cut(ear_l).cut(ear_r)

    chassis = chassis.fuse(front_plate).fuse(servo_mnt)

    for side in [-1, 1]:
        x_piv = side * (FRONT_TRACK / 2.0)
        col_x = x_piv - (side * 6.5) - 2.0
        col = Part.makeBox(4.0, 12.0, total_chub_h,
                           App.Vector(col_x, front_y0 + 3.0, 0))
        arm_x = min(col_x, x_piv - 4.0)
        arm_w = abs(x_piv - col_x) + 4.5
        top_arm = Part.makeBox(arm_w, 12.0, CHUB_ARM_T,
                               App.Vector(arm_x, front_y0 + 3.0,
                                          total_chub_h - CHUB_ARM_T))
        chassis = chassis.fuse(col).fuse(top_arm)
        kp_hole = Part.makeCylinder(KINGPIN_D / 2.0, total_chub_h + 2.0,
                                    App.Vector(x_piv, front_y0 + 9.0, -1.0))
        chassis = chassis.cut(kp_hole)

    # --- F. Forward Angled ESP32-CAM Nose Bumper & Headlight Pods ---
    nose_y = front_y0 + bridge_d
    bumper = Part.makeBox(46.0, 10.0, 16.0,
                          App.Vector(-23.0, nose_y - 2.0, 0))
    # 15-degree upward-tilted camera lens cutout
    cam_hole = Part.makeCylinder(
        5.2, 16.0,
        App.Vector(0, nose_y - 3.0, 9.0),
        App.Vector(0, 1, 0.27))
    # Dual 5.2 mm LED Headlight sockets
    led_l = Part.makeCylinder(
        2.6, 14.0,
        App.Vector(-16.0, nose_y - 3.0, 8.0),
        App.Vector(0, 1, 0))
    led_r = Part.makeCylinder(
        2.6, 14.0,
        App.Vector(16.0, nose_y - 3.0, 8.0),
        App.Vector(0, 1, 0))
    bumper = bumper.cut(cam_hole).cut(led_l).cut(led_r)
    chassis = chassis.fuse(bumper)

    obj_base = doc.addObject("Part::Feature", "Main_Chassis_With_Gearboxes")
    obj_base.Shape = chassis

    obj_cap = doc.addObject("Part::Feature", "Rear_Gearbox_Upper_Cap")
    obj_cap.Shape = rear_upper
    obj_cap.Placement.Base = App.Vector(0, 0, 18.0)

    # --- G. Upper Electronics & 3 W Speaker Acoustic Deck (At Z = TRAY_Z) ---
    upper_deck = Part.makeBox(CHASSIS_W, tray_len, 2.5,
                              App.Vector(-CHASSIS_W / 2.0, tray_y0, TRAY_Z))

    # 4x Pillar Mounting Holes on Upper Deck Corners
    for px in [-CHASSIS_W / 2.0 + 3.5, CHASSIS_W / 2.0 - 3.5]:
        for py in [tray_y0 + 4.0, tray_y0 + tray_len - 4.0]:
            mnt_hole = Part.makeCylinder(
                1.3, 4.0,
                App.Vector(px, py, TRAY_Z - 0.5))
            upper_deck = upper_deck.cut(mnt_hole)

    # Speaker Ring Enclosure (36 mm 3 W speaker) at rear of upper deck
    spk_ring = Part.makeCylinder(
        SPK_D / 2.0 + 2.5, 10.0,
        App.Vector(0, tray_y0 + 21.0, TRAY_Z + 2.5))
    spk_bore = Part.makeCylinder(
        SPK_D / 2.0, 11.0,
        App.Vector(0, tray_y0 + 21.0, TRAY_Z + 2.5))
    spk_sound_hole = Part.makeCylinder(
        12.0, 5.0,
        App.Vector(0, tray_y0 + 21.0, TRAY_Z - 1.0))
    upper_deck = upper_deck.fuse(spk_ring).cut(spk_bore).cut(spk_sound_hole)

    # 4x M2 Standoffs for Carrier PCB at front of upper deck
    pcb_y0 = tray_y0 + 42.0
    for mx in [-PCB_W / 2.0 + 2.5, PCB_W / 2.0 - 2.5]:
        for my in [pcb_y0 + 2.5, pcb_y0 + PCB_L - 2.5]:
            boss = Part.makeCylinder(2.5, 5.0,
                                     App.Vector(mx, my, TRAY_Z + 2.5))
            hole = Part.makeCylinder(0.85, 6.0,
                                     App.Vector(mx, my, TRAY_Z + 2.0))
            upper_deck = upper_deck.fuse(boss).cut(hole)

    # Clearance Window in Upper Deck for Bottom-Mounted DFPlayer Mini & MicroSD Access
    df_cutout = Part.makeBox(22.0, 23.0, 5.0,
                             App.Vector(-11.0, pcb_y0 + 1.0, TRAY_Z - 1.0))
    upper_deck = upper_deck.cut(df_cutout)

    obj_tray = doc.addObject("Part::Feature", "Upper_PCB_And_Speaker_Deck")
    obj_tray.Shape = upper_deck
    obj_tray.Placement.Base = App.Vector(0, 0, 15.0)   # Exploded upward for easy export

# ==========================================
# 2. FRONT ACKERMANN STEERING KNUCKLES
# ==========================================
def build_knuckle(name, side, x_pos, y_pos):
    knuckle_h = CHUB_GAP - 0.6
    z_base    = CHUB_ARM_T + 0.3
    barrel = Part.makeCylinder(4.2, knuckle_h,
                               App.Vector(x_pos, y_pos, z_base))
    kp_bore = Part.makeCylinder(KINGPIN_D / 2.0, knuckle_h + 2.0,
                                App.Vector(x_pos, y_pos, z_base - 1.0))
    stub = Part.makeCylinder(
        4.5, 10.0,
        App.Vector(x_pos, y_pos, z_base + knuckle_h / 2.0),
        App.Vector(side, 0, 0))
    stub_bore = Part.makeCylinder(
        1.55, 11.0,
        App.Vector(x_pos, y_pos, z_base + knuckle_h / 2.0),
        App.Vector(side, 0, 0))

    arm_len = 13.0
    arm = Part.makeBox(3.2, arm_len, 3.5, App.Vector(-1.6, -arm_len, 0))
    arm.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), side * 12.0)
    arm.translate(App.Vector(x_pos, y_pos, z_base + 1.5))

    tip_x = x_pos + side * (arm_len - 2.2) * math.sin(math.radians(12.0))
    tip_y = y_pos - (arm_len - 2.2) * math.cos(math.radians(12.0))
    tie_hole = Part.makeCylinder(0.85, 6.0, App.Vector(tip_x, tip_y, z_base))

    knuckle = barrel.fuse(stub).fuse(arm).cut(kp_bore).cut(stub_bore).cut(tie_hole)
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = knuckle

# ==========================================
# BUILD ALL
# ==========================================
build_complete_base()
build_knuckle("Steering_Knuckle_Left",  -1, -FRONT_TRACK / 2.0 - 15.0, 142.0)
build_knuckle("Steering_Knuckle_Right",  1,  FRONT_TRACK / 2.0 + 15.0, 142.0)

doc.recompute()
if App.GuiUp:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewAxonometric()
    Gui.SendMsgToActiveView("ViewFit")

print("complete_chassis_v2.py: generated ->")
print("  Main_Chassis_With_Gearboxes, Rear_Gearbox_Upper_Cap,")
print("  Upper_PCB_And_Speaker_Deck, Steering_Knuckle_Left/Right")