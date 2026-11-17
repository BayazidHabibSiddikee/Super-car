import FreeCAD as App
import Part
import math

doc = App.newDocument("FPV_RC_Direct_Print_Plate")

# ==========================================
# MASTER PARAMETRIC DIMENSIONS (mm)
# ==========================================
TOL = 0.15
FLOOR_T = 3.0
WHEELBASE = 115.0
CHASSIS_W = 54.0
TRAY_Z = 37.0
PILLAR_R = 3.5

# Rear N20 + Dual MR63ZZ Bearing Gearbox
N20_W = 12.0 + TOL
N20_H = 10.0 + TOL
N20_L = 16.0
COUPLER_BAY_L = 14.0
BEARING_OD = 6.08
BEARING_W = 2.6
AXLE_D = 3.3
REAR_SPAN = 48.0

# Front SG92R + C-Hub Steering Bridge
SERVO_L = 23.1 + TOL
SERVO_W = 12.5 + TOL
SERVO_H = 15.5
FRONT_TRACK = 66.0
CHUB_GAP = 14.0
CHUB_ARM_T = 3.5
KINGPIN_D = 2.1

# Payload & Audio Modules (2S 18650, 3W Speaker, JQ6500-16P, MH-M18, PCB)
BAT_L = 69.0
BAT_W = 38.0
SPK_D = 36.5
PCB_L = 46.0
PCB_W = 32.0
JQ_L = 21.0 + TOL
JQ_W = 20.5 + TOL
MHM18_L = 23.2 + TOL
MHM18_W = 16.2 + TOL

# ==========================================
# 1. MAIN CHASSIS + PRINT-READY GEARBOX CAP
# ==========================================
def build_chassis_and_deck():
    gb_len = N20_L + COUPLER_BAY_L + 6.0
    axle_y = 3.0 + N20_L + (COUPLER_BAY_L / 2.0)       # Y = 26.0 mm
    front_y0 = axle_y + WHEELBASE - 9.0                # Y = 132.0 mm
    total_len = front_y0 + 24.0

    # Center Belly Pan & Side Stiffener Rails
    deck = Part.makeBox(CHASSIS_W, total_len - 10.0, FLOOR_T, App.Vector(-CHASSIS_W / 2.0, 5.0, 0))
    rail_l = Part.makeBox(3.5, total_len - 25.0, 10.0, App.Vector(-CHASSIS_W / 2.0, 15.0, 0))
    rail_r = Part.makeBox(3.5, total_len - 25.0, 10.0, App.Vector(CHASSIS_W / 2.0 - 3.5, 15.0, 0))
    chassis = deck.fuse(rail_l).fuse(rail_r)

    # Rear N20 + Bearing Gearbox
    gb_h = N20_H + 6.0
    z_axle = gb_h / 2.0
    rear_block = Part.makeBox(REAR_SPAN, gb_len, gb_h, App.Vector(-REAR_SPAN / 2.0, 0, 0))
    n20_pkt = Part.makeBox(N20_W, N20_L, N20_H, App.Vector(-N20_W / 2.0, 3.0, z_axle - N20_H / 2.0))
    wire_slot = Part.makeBox(6.0, 4.0, 4.0, App.Vector(-3.0, -0.5, z_axle - 2.0))
    coupler_bay = Part.makeBox(16.0, COUPLER_BAY_L, 12.0, App.Vector(-8.0, 3.0 + N20_L, z_axle - 6.0))
    axle_hole = Part.makeCylinder(AXLE_D / 2.0, REAR_SPAN + 2.0, App.Vector(-REAR_SPAN / 2.0 - 1.0, axle_y, z_axle), App.Vector(1, 0, 0))
    brg_l = Part.makeCylinder(BEARING_OD / 2.0, BEARING_W + 0.5, App.Vector(-REAR_SPAN / 2.0 - 0.5, axle_y, z_axle), App.Vector(1, 0, 0))
    brg_r = Part.makeCylinder(BEARING_OD / 2.0, BEARING_W + 0.5, App.Vector(REAR_SPAN / 2.0 - BEARING_W, axle_y, z_axle), App.Vector(1, 0, 0))

    full_rear = rear_block.cut(n20_pkt).cut(wire_slot).cut(coupler_bay).cut(axle_hole).cut(brg_l).cut(brg_r)
    for sx in [-REAR_SPAN / 2.0 + 4.0, REAR_SPAN / 2.0 - 4.0]:
        for sy in [5.0, gb_len - 5.0]:
            full_rear = full_rear.cut(Part.makeCylinder(1.05, gb_h + 2.0, App.Vector(sx, sy, -1.0)))

    rear_lower = full_rear.cut(Part.makeBox(REAR_SPAN + 10, gb_len + 10, gb_h, App.Vector(-REAR_SPAN/2 - 5, -5, z_axle)))
    rear_upper = full_rear.cut(Part.makeBox(REAR_SPAN + 10, gb_len + 10, gb_h, App.Vector(-REAR_SPAN/2 - 5, -5, z_axle - gb_h)))
    chassis = chassis.fuse(rear_lower)

    # Flip Rear Gearbox Cap flat onto Z=0 at X=-65 for direct printing
    rear_upper.rotate(App.Vector(0, gb_len / 2.0, z_axle + gb_h / 4.0), App.Vector(0, 1, 0), 180.0)
    rear_upper.translate(App.Vector(-65.0, 0, -rear_upper.BoundBox.ZMin))
    obj_cap = doc.addObject("Part::Feature", "Rear_Gearbox_Upper_Cap")
    obj_cap.Shape = rear_upper

    # 2S 18650 Battery Cradle
    bat_y0 = 42.0
    bat_wall_l = Part.makeBox(2.5, BAT_L, 12.0, App.Vector(-BAT_W / 2.0 - 2.5, bat_y0, FLOOR_T))
    bat_wall_r = Part.makeBox(2.5, BAT_L, 12.0, App.Vector(BAT_W / 2.0, bat_y0, FLOOR_T))
    bat_stop = Part.makeBox(BAT_W + 5.0, 2.5, 10.0, App.Vector(-BAT_W / 2.0 - 2.5, bat_y0 + BAT_L, FLOOR_T))
    chassis = chassis.fuse(bat_wall_l).fuse(bat_wall_r).fuse(bat_stop)

    # 4x Reinforced Upper Deck Pillars (Z = 3.0 to 37.0 mm)
    tray_y0 = 38.0
    tray_len = 90.0
    for px in [-CHASSIS_W / 2.0 + 3.5, CHASSIS_W / 2.0 - 3.5]:
        for py in [tray_y0 + 4.0, tray_y0 + tray_len - 4.0]:
            pillar = Part.makeCylinder(PILLAR_R, TRAY_Z - FLOOR_T, App.Vector(px, py, FLOOR_T))
            collar = Part.makeCylinder(PILLAR_R + 1.5, 6.0, App.Vector(px, py, FLOOR_T))
            top_hole = Part.makeCylinder(1.05, 8.0, App.Vector(px, py, TRAY_Z - 7.5))
            chassis = chassis.fuse(pillar).fuse(collar).cut(top_hole)

    # Front SG92R Servo + C-Hub Crossmember
    bridge_w = FRONT_TRACK + 8.0
    bridge_d = 18.0
    total_chub_h = CHUB_GAP + (CHUB_ARM_T * 2)
    front_plate = Part.makeBox(bridge_w, bridge_d, CHUB_ARM_T, App.Vector(-bridge_w / 2.0, front_y0, 0))

    servo_blk_w = SERVO_L + 10.0
    servo_blk_d = SERVO_W + 6.0
    servo_blk = Part.makeBox(servo_blk_w, servo_blk_d, SERVO_H, App.Vector(-servo_blk_w / 2.0, front_y0, 0))
    servo_pkt = Part.makeBox(SERVO_L, SERVO_W, SERVO_H + 1.0, App.Vector(-SERVO_L / 2.0, front_y0 + 3.0, 2.0))
    ear_l = Part.makeCylinder(0.9, 10.0, App.Vector(-SERVO_L / 2.0 - 2.5, front_y0 + 3.0 + SERVO_W / 2.0, SERVO_H - 9.0))
    ear_r = Part.makeCylinder(0.9, 10.0, App.Vector(SERVO_L / 2.0 + 2.5, front_y0 + 3.0 + SERVO_W / 2.0, SERVO_H - 9.0))
    chassis = chassis.fuse(front_plate).fuse(servo_blk.cut(servo_pkt).cut(ear_l).cut(ear_r))

    for side in [-1, 1]:
        x_piv = side * (FRONT_TRACK / 2.0)
        col_x = x_piv - (side * 6.5) - 2.0
        col = Part.makeBox(4.0, 12.0, total_chub_h, App.Vector(col_x, front_y0 + 3.0, 0))
        arm_x = min(col_x, x_piv - 4.0)
        arm_w = abs(x_piv - col_x) + 4.5
        top_arm = Part.makeBox(arm_w, 12.0, CHUB_ARM_T, App.Vector(arm_x, front_y0 + 3.0, total_chub_h - CHUB_ARM_T))
        chassis = chassis.fuse(col).fuse(top_arm)
        kp_hole = Part.makeCylinder(KINGPIN_D / 2.0, total_chub_h + 2.0, App.Vector(x_piv, front_y0 + 9.0, -1.0))
        chassis = chassis.cut(kp_hole)

    # Front Angled Camera Bumper & Headlight Pods
    nose_y = front_y0 + bridge_d
    bumper = Part.makeBox(46.0, 10.0, 16.0, App.Vector(-23.0, nose_y - 2.0, 0))
    cam_hole = Part.makeCylinder(5.2, 16.0, App.Vector(0, nose_y - 3.0, 9.0), App.Vector(0, 1, 0.27))
    led_l = Part.makeCylinder(2.6, 14.0, App.Vector(-16.0, nose_y - 3.0, 8.0), App.Vector(0, 1, 0))
    led_r = Part.makeCylinder(2.6, 14.0, App.Vector(16.0, nose_y - 3.0, 8.0), App.Vector(0, 1, 0))
    chassis = chassis.fuse(bumper.cut(cam_hole).cut(led_l).cut(led_r))

    obj_base = doc.addObject("Part::Feature", "Main_Chassis_Base")
    obj_base.Shape = chassis

    # ==========================================
    # 2. UPPER DECK (SPEAKER + JQ6500 + MH-M18 + PCB) FLAT AT Z=0
    # ==========================================
    upper_deck = Part.makeBox(CHASSIS_W, tray_len, 2.5, App.Vector(-CHASSIS_W / 2.0, 0, 0))

    # 4x Corner Pillar Screw Holes
    for px in [-CHASSIS_W / 2.0 + 3.5, CHASSIS_W / 2.0 - 3.5]:
        for py in [4.0, tray_len - 4.0]:
            upper_deck = upper_deck.cut(Part.makeCylinder(1.3, 4.0, App.Vector(px, py, -0.5)))

    # 36mm 3W Speaker Acoustic Ring (Centered at Y = 22.0)
    spk_ring = Part.makeCylinder(SPK_D / 2.0 + 2.5, 9.0, App.Vector(0, 22.0, 2.5))
    spk_bore = Part.makeCylinder(SPK_D / 2.0, 10.0, App.Vector(0, 22.0, 2.5))
    spk_vent = Part.makeCylinder(12.0, 5.0, App.Vector(0, 22.0, -1.0))
    upper_deck = upper_deck.fuse(spk_ring).cut(spk_bore).cut(spk_vent)

    # JQ6500-16P Onboard Flash Retention Cradle + Pass-Through Slot (Y = 43 to 64)
    jq_wall = Part.makeBox(JQ_W + 3.0, JQ_L + 3.0, 5.0, App.Vector(-(JQ_W + 3.0) / 2.0, 43.0, 2.5))
    jq_pkt = Part.makeBox(JQ_W, JQ_L, 6.0, App.Vector(-JQ_W / 2.0, 44.5, 2.5))
    jq_slot = Part.makeBox(JQ_W - 2.0, JQ_L - 2.0, 5.0, App.Vector(-(JQ_W - 2.0) / 2.0, 45.5, -1.0))
    upper_deck = upper_deck.fuse(jq_wall.cut(jq_pkt)).cut(jq_slot)

    # MH-M18 Bluetooth Audio Receiver Side Pocket (Left side at X = -25 to -13, Y = 44 to 68)
    bt_wall = Part.makeBox(MHM18_W + 2.4, MHM18_L + 2.4, 4.0, App.Vector(-CHASSIS_W / 2.0 + 1.0, 44.0, 2.5))
    bt_pkt = Part.makeBox(MHM18_W, MHM18_L, 5.0, App.Vector(-CHASSIS_W / 2.0 + 2.2, 45.2, 2.5))
    upper_deck = upper_deck.fuse(bt_wall.cut(bt_pkt))

    # 4x M2 Standoffs for 46x32mm Carrier PCB (Y = 42.0 to 88.0)
    pcb_y0 = 42.0
    for mx in [-PCB_W / 2.0 + 2.5, PCB_W / 2.0 - 2.5]:
        for my in [pcb_y0 + 2.5, pcb_y0 + PCB_L - 2.5]:
            boss = Part.makeCylinder(2.5, 5.5, App.Vector(mx, my, 2.5))
            hole = Part.makeCylinder(0.85, 6.5, App.Vector(mx, my, 2.0))
            upper_deck = upper_deck.fuse(boss).cut(hole)

    upper_deck.translate(App.Vector(72.0, 20.0, 0))  # Placed flat at Z=0 beside chassis
    obj_tray = doc.addObject("Part::Feature", "Upper_Audio_And_PCB_Deck")
    obj_tray.Shape = upper_deck

# ==========================================
# 3. STEERING KNUCKLES + TIE-ROD + SERVO LINK (FLAT AT Z=0)
# ==========================================
def build_steering_hardware():
    knuckle_h = CHUB_GAP - 0.6
    for idx, (name, side, y_off) in enumerate([("Steering_Knuckle_Left", -1, 45.0), ("Steering_Knuckle_Right", 1, 70.0)]):
        barrel = Part.makeCylinder(4.2, knuckle_h, App.Vector(0, 0, 0))
        kp_bore = Part.makeCylinder(KINGPIN_D / 2.0, knuckle_h + 2.0, App.Vector(0, 0, -1.0))
        stub = Part.makeCylinder(4.5, 10.0, App.Vector(0, 0, knuckle_h / 2.0), App.Vector(side, 0, 0))
        stub_bore = Part.makeCylinder(1.55, 11.0, App.Vector(0, 0, knuckle_h / 2.0), App.Vector(side, 0, 0))

        arm_len = 13.0
        arm = Part.makeBox(3.2, arm_len, 3.5, App.Vector(-1.6, -arm_len, 0))
        arm.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), side * 12.0)

        tip_x = side * (arm_len - 2.2) * math.sin(math.radians(12.0))
        tip_y = -(arm_len - 2.2) * math.cos(math.radians(12.0))
        tie_hole = Part.makeCylinder(0.95, 6.0, App.Vector(tip_x, tip_y, -1.0))

        knuckle = barrel.fuse(stub).fuse(arm).cut(kp_bore).cut(stub_bore).cut(tie_hole)
        knuckle.translate(App.Vector(-65.0, y_off, 0))
        obj = doc.addObject("Part::Feature", name)
        obj.Shape = knuckle

    # Ackermann Tie-Rod Bar connecting Left and Right Knuckle Arms (61.5mm eye-to-eye)
    tie_span = FRONT_TRACK - (2.0 * 10.8 * math.sin(math.radians(12.0)))
    bar = Part.makeBox(tie_span, 3.6, 3.0, App.Vector(-tie_span / 2.0, -1.8, 0))
    end_l = Part.makeCylinder(3.2, 3.0, App.Vector(-tie_span / 2.0, 0, 0))
    end_r = Part.makeCylinder(3.2, 3.0, App.Vector(tie_span / 2.0, 0, 0))
    srv_boss = Part.makeCylinder(3.2, 3.0, App.Vector(6.0, 2.0, 0))
    hole_l = Part.makeCylinder(0.95, 5.0, App.Vector(-tie_span / 2.0, 0, -1.0))
    hole_r = Part.makeCylinder(0.95, 5.0, App.Vector(tie_span / 2.0, 0, -1.0))
    hole_s = Part.makeCylinder(0.95, 5.0, App.Vector(6.0, 2.0, -1.0))

    tie_rod = bar.fuse(end_l).fuse(end_r).fuse(srv_boss).cut(hole_l).cut(hole_r).cut(hole_s)
    tie_rod.translate(App.Vector(-65.0, 95.0, 0))
    obj_tr = doc.addObject("Part::Feature", "Ackermann_Tie_Rod")
    obj_tr.Shape = tie_rod

    # SG92R Servo Pushrod Link (22mm eye-to-eye)
    p_bar = Part.makeBox(22.0, 3.2, 2.5, App.Vector(-11.0, -1.6, 0))
    p_l = Part.makeCylinder(2.8, 2.5, App.Vector(-11.0, 0, 0))
    p_r = Part.makeCylinder(2.8, 2.5, App.Vector(11.0, 0, 0))
    ph_l = Part.makeCylinder(0.85, 4.0, App.Vector(-11.0, 0, -0.5))
    ph_r = Part.makeCylinder(0.85, 4.0, App.Vector(11.0, 0, -0.5))
    pushrod = p_bar.fuse(p_l).fuse(p_r).cut(ph_l).cut(ph_r)
    pushrod.translate(App.Vector(-65.0, 110.0, 0))
    obj_pr = doc.addObject("Part::Feature", "Servo_Pushrod_Link")
    obj_pr.Shape = pushrod

# ==========================================
# 4. 4x RIMS & 4x TIRES (FLAT AT Z=0)
# ==========================================
def build_wheels_and_tires():
    tire_od, tire_w, rim_od = 34.0, 14.0, 24.0
    rim_r = rim_od / 2.0
    for idx, (name, is_rear, px, py) in enumerate([
        ("Rear_Rim_L", True, -55.0, 135.0), ("Rear_Rim_R", True, -85.0, 135.0),
        ("Front_Rim_L", False, -55.0, 165.0), ("Front_Rim_R", False, -85.0, 165.0)
    ]):
        outer = Part.makeCylinder(rim_r, tire_w)
        inner = Part.makeCylinder(rim_r - 2.4, tire_w + 2.0, App.Vector(0, 0, -1.0))
        groove = Part.makeCylinder(rim_r + 1.0, 3.2, App.Vector(0, 0, (tire_w - 3.2) / 2.0)).cut(
                 Part.makeCylinder(rim_r - 1.2, 3.2, App.Vector(0, 0, (tire_w - 3.2) / 2.0)))
        barrel = outer.cut(inner).cut(groove)
        hub_len = 13.0 if is_rear else 10.5
        hub = Part.makeCylinder(5.2, hub_len)
        for s in range(5):
            sp = Part.makeBox(2.5, rim_r - 1.5, 4.0, App.Vector(-1.25, 0, 0))
            sp.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), s * 72.0)
            hub = hub.fuse(sp)
        rim = barrel.fuse(hub)
        if is_rear:
            dbore = Part.makeCylinder(1.53, hub_len + 2.0, App.Vector(0, 0, -1.0)).cut(
                    Part.makeBox(6.0, 6.0, hub_len + 2.0, App.Vector(-3.0, 1.05, -1.0)))
            rim = rim.cut(dbore)
        else:
            rim = rim.cut(Part.makeCylinder(1.59, hub_len + 2.0, App.Vector(0, 0, -1.0)))
        rim.translate(App.Vector(px, py, 0))
        obj = doc.addObject("Part::Feature", name)
        obj.Shape = rim

    for idx, (px, py) in enumerate([(55.0, 135.0), (95.0, 135.0), (55.0, 175.0), (95.0, 175.0)]):
        tr = tire_od / 2.0
        rr = rim_r - 0.1
        t_body = Part.makeCylinder(tr, tire_w).cut(Part.makeCylinder(rr, tire_w + 2.0, App.Vector(0, 0, -1.0)))
        rib = Part.makeCylinder(rr + 0.5, 3.0, App.Vector(0, 0, (tire_w - 3.0) / 2.0)).cut(
              Part.makeCylinder(rr - 1.0, 3.0, App.Vector(0, 0, (tire_w - 3.0) / 2.0)))
        t_body = t_body.fuse(rib)
        t_body.translate(App.Vector(px, py, 0))
        obj_t = doc.addObject("Part::Feature", f"TPU_Tire_{idx+1}")
        obj_t.Shape = t_body

build_chassis_and_deck()
build_steering_hardware()
build_wheels_and_tires()

doc.recompute()
if App.GuiUp:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewAxonometric()
    Gui.SendMsgToActiveView("ViewFit")