import FreeCAD as App
import Part
import math

doc = App.newDocument("Ferrari_Enzo_Fixed_Assembly")

# ==========================================
# MASTER VEHICLE PARAMETERS (mm)
# ==========================================
TOL = 0.15
WHEELBASE = 115.0
REAR_AXLE_Y = 26.0
FRONT_AXLE_Y = REAR_AXLE_Y + WHEELBASE    # 141.0 mm

CHASSIS_W = 54.0
FENDER_W = 74.0
TRAY_Z = 22.0                             # Electronics deck sits above 2S 18650 battery
ROOF_Z = 38.5                             # Low-slung Ferrari Enzo roof height

WALL = 2.0
CLEARANCE = 0.4
INNER_W = CHASSIS_W + (CLEARANCE * 2.0)   # 54.8 mm chassis snap-fit cavity

# Hardware & Off-the-Shelf Market Wheel Dimensions
SPK_D = 36.2                              # 36mm 3W speaker
MARKET_WHEEL_OD = 34.0                    # Standard 34mm x 15mm N20 market rubber wheel
MARKET_WHEEL_W = 15.0
N20_W, N20_H, N20_L = 12.15, 10.15, 16.0
SERVO_L, SERVO_W, SERVO_H = 23.25, 12.65, 15.5
FRONT_TRACK = 64.0
CHUB_GAP, CHUB_ARM_T = 14.0, 3.5

def add_solid(group, name, shape, color=(0.8, 0.8, 0.8), transparency=0):
    clean_shape = shape.removeSplitter()
    if not clean_shape.isValid():
        clean_shape.fix(1e-3, 1e-3, 1e-3)
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = clean_shape
    group.addObject(obj)
    if App.GuiUp:
        obj.ViewObject.ShapeColor = color
        obj.ViewObject.Transparency = transparency
    return obj

def make_wire(y_pos, half_w, z_bot, z_side, z_top, top_half_w):
    pts = [
        App.Vector(-half_w, y_pos, z_bot),
        App.Vector(-half_w, y_pos, z_side),
        App.Vector(-top_half_w, y_pos, z_top),
        App.Vector(top_half_w, y_pos, z_top),
        App.Vector(half_w, y_pos, z_side),
        App.Vector(half_w, y_pos, z_bot),
        App.Vector(-half_w, y_pos, z_bot)
    ]
    return Part.Wire(Part.makePolygon(pts).Edges)

# ==========================================
# MODULAR ASSEMBLY CONTAINERS (App::Part)
# ==========================================
grp_ext   = doc.addObject("App::Part", "01_Exterior_Body")
grp_glass = doc.addObject("App::Part", "02_Glass_And_Lights")
grp_chas  = doc.addObject("App::Part", "03_Chassis_And_Steering")
grp_wheel = doc.addObject("App::Part", "04_Market_Wheels_34mm")
grp_audio = doc.addObject("App::Part", "05_Audio_System")
grp_elec  = doc.addObject("App::Part", "06_Electronics_Deck")

# ==========================================
# MODULE 01 & 02: EXTERIOR BODY, FLUSH GLASS & ANGLED HEADLIGHTS
# ==========================================
def build_exterior_glass_lights():
    hw_f = FENDER_W / 2.0
    hw_in = INNER_W / 2.0

    # 1. Wide Fender Body Loft
    w_rear   = make_wire(-2.0,  hw_f - 2.0, 2.5, 22.0, 27.5, 28.0)
    w_haunch = make_wire(32.0,  hw_f,       1.0, 23.0, 28.5, 31.0)
    w_waist  = make_wire(82.0,  hw_f - 2.5, 1.0, 21.0, 25.5, 29.0)
    w_ffend  = make_wire(138.0, hw_f - 0.5, 1.5, 21.5, 26.5, 29.5)
    w_front  = make_wire(163.0, hw_f - 5.0, 2.0, 13.0, 17.5, 25.0)
    fender_body = Part.makeLoft([w_rear, w_haunch, w_waist, w_ffend, w_front], True)

    # 2. Central Teardrop Canopy + F1 Protruding Nose Cone
    c_rear   = make_wire(0.0,   16.0, 10.0, 25.0, 28.5, 11.0)
    c_spk    = make_wire(30.0,  21.5, 10.0, 29.5, 34.5, 15.5)
    c_cock1  = make_wire(72.0,  22.5, 10.0, 32.0, ROOF_Z, 15.5)
    c_cock2  = make_wire(105.0, 21.0, 10.0, 30.0, 36.5, 14.5)
    c_hood   = make_wire(136.0, 14.0,  6.0, 21.0, 24.5,  9.5)
    c_f1nose = make_wire(169.0,  7.5,  3.5, 11.5, 14.5,  5.0)
    canopy = Part.makeLoft([c_rear, c_spk, c_cock1, c_cock2, c_hood, c_f1nose], True)

    outer = fender_body.fuse(canopy)

    # 3. Hollow Interior Cavity (2.0mm shell wall)
    wi_rear   = make_wire(0.0,   hw_in,       -2.0, 21.0, 26.0, 25.0)
    wi_haunch = make_wire(32.0,  hw_in,       -2.0, 22.0, 32.5, 19.5)
    wi_waist  = make_wire(82.0,  hw_in,       -2.0, 28.0, ROOF_Z - WALL, 15.0)
    wi_ffend  = make_wire(136.0, hw_in,       -2.0, 19.5, 24.5, 16.0)
    wi_front  = make_wire(160.5, hw_in - 3.0, -2.0, 11.0, 15.5, 14.0)
    cavity = Part.makeLoft([wi_rear, wi_haunch, wi_waist, wi_ffend, wi_front], True)

    shell = outer.cut(cavity)

    # 4. Outer-Only Wheel Arches (Sized for 34mm Market Rubber Wheels)
    for side in [-1, 1]:
        x_start = 18.0 if side == 1 else -(hw_f + 5.0)
        span = (hw_f + 5.0) - 18.0
        shell = shell.cut(Part.makeCylinder(19.5, span, App.Vector(x_start, REAR_AXLE_Y, 8.1), App.Vector(1, 0, 0)))
        shell = shell.cut(Part.makeCylinder(20.5, span, App.Vector(x_start, FRONT_AXLE_Y, 8.1), App.Vector(1, 0, 0)))

    # 5. Front Twin Grille Intakes & Side NACA Scoops
    for side in [-1, 1]:
        ix = 8.5 if side == 1 else -28.5
        shell = shell.cut(Part.makeBox(20.0, 10.0, 8.5, App.Vector(ix, 156.0, 4.0)))
        sx = (hw_f - 4.5) if side == 1 else -(hw_f + 1.0)
        shell = shell.cut(Part.makeBox(5.5, 30.0, 12.0, App.Vector(sx, 50.0, 8.0)))

    # 6. FLUSH SLOPED WINDSHIELD CUTOUT & CONTOURED CLEAR INSERT
    # Lofted along exact canopy rake from Y=105 (Z=36.5) down to Y=131 (Z=25.5)
    ws_cut_top = make_wire(105.0, 14.2, 31.0, 34.0, 37.5, 13.0)
    ws_cut_bot = make_wire(131.0, 11.0, 22.0, 24.5, 27.0, 10.0)
    ws_cutter = Part.makeLoft([ws_cut_top, ws_cut_bot], True)
    shell = shell.cut(ws_cutter)

    # Flush Clear Windshield Glass (1.0mm thick, sits inside window frame without poking out)
    ws_gl_top = make_wire(105.5, 13.8, 34.6, 35.4, 36.1, 12.6)
    ws_gl_bot = make_wire(130.5, 10.6, 24.2, 25.0, 25.7,  9.6)
    ws_glass = Part.makeLoft([ws_gl_top, ws_gl_bot], True)
    # Clean camera lens viewport hole through windshield so ESP32-CAM has zero glare
    cam_hole = Part.makeCylinder(5.2, 35.0, App.Vector(0, 102.0, 32.0), App.Vector(0, 1, -0.15))
    ws_glass = ws_glass.cut(cam_hole)
    add_solid(grp_glass, "Front_Windshield_Flush_Glass", ws_glass, (0.65, 0.88, 0.98), 65)

    # 7. FLUSH TUMBLED SIDE WINDOWS (Follows 26-deg inward cabin slope)
    for side, sname in [(-1, "Side_Glass_L"), (1, "Side_Glass_R")]:
        # Side window cutout on canopy wall
        sw_cut = Part.makeBox(10.0, 28.0, 6.2, App.Vector(side * 16.5 - (5.0 if side == -1 else 0), 73.0, 30.2))
        sw_cut.rotate(App.Vector(side * 16.5, 87.0, 33.0), App.Vector(0, 1, 0), -side * 25.0)
        shell = shell.cut(sw_cut)

        # Flush Side Glass Insert tilted to match cabin wall angle
        sg = Part.makeBox(1.0, 27.2, 5.6, App.Vector(side * 17.6 - (1.0 if side == 1 else 0), 73.4, 30.5))
        sg.rotate(App.Vector(side * 17.6, 87.0, 33.0), App.Vector(0, 1, 0), -side * 25.0)
        add_solid(grp_glass, sname, sg, (0.65, 0.88, 0.98), 65)

    # 8. PROPERLY ANGLED FENDER HEADLIGHT BUCKETS, 5mm LED SOCKETS & FLUSH LENSES
    # Fender slopes downward at 19.8 deg from Y=138 (Z=26.5) to Y=163 (Z=17.5)
    fender_slope_deg = 19.8
    for side, bname, lname in [(-1, "Headlight_Bucket_L", "Headlight_Clear_Lens_L"),
                               ( 1, "Headlight_Bucket_R", "Headlight_Clear_Lens_R")]:
        hx = side * 24.5
        # Cut recessed headlight pocket into top of sloped front fender (Y = 143 to 158 mm)
        pocket = Part.makeBox(6.8, 15.0, 6.5, App.Vector(hx - 3.4, 143.0, 18.2))
        pocket.rotate(App.Vector(hx, 143.0, 24.7), App.Vector(1, 0, 0), -fender_slope_deg)
        shell = shell.cut(pocket)

        # Internal Black Headlight Reflector Housing + Straight-Forward (+Y) 5.2mm LED Bore
        bucket = Part.makeBox(6.4, 14.4, 4.8, App.Vector(hx - 3.2, 143.3, 18.4))
        bucket.rotate(App.Vector(hx, 143.3, 23.2), App.Vector(1, 0, 0), -fender_slope_deg)
        led_socket = Part.makeCylinder(2.6, 22.0, App.Vector(hx, 139.0, 19.2), App.Vector(0, 1, 0))
        bucket = bucket.cut(led_socket)
        shell = shell.cut(led_socket)
        add_solid(grp_glass, bname, bucket, (0.12, 0.12, 0.14), 0)

        # Flush Clear Polycarbonate Headlight Cover matching the exact 19.8-deg fender slope
        lens = Part.makeBox(6.4, 14.4, 1.1, App.Vector(hx - 3.2, 143.3, 23.3))
        lens.rotate(App.Vector(hx, 143.3, 24.4), App.Vector(1, 0, 0), -fender_slope_deg)
        add_solid(grp_glass, lname, lens, (0.95, 0.98, 1.0), 45)

    # 9. Rear Engine Speaker Louvers & Snap-On Rocker Clips
    for sy in [10.0, 15.0, 20.0, 25.0, 30.0]:
        shell = shell.cut(Part.makeBox(28.0, 2.5, 10.0, App.Vector(-14.0, sy, 26.0)))

    for side in [-1, 1]:
        web_x = side * (hw_in - 0.5) - (2.2 if side == 1 else 0.0)
        lip_x = side * (hw_in - 1.8) - (1.8 if side == 1 else 0.0)
        shell = shell.fuse(Part.makeBox(2.2, 38.0, 4.0, App.Vector(web_x, 55.0, -1.5)))
        shell = shell.fuse(Part.makeBox(1.8, 38.0, 1.5, App.Vector(lip_x, 55.0, -1.5)))

    add_solid(grp_ext, "Main_Body_Shell_Enzo", shell, (0.85, 0.08, 0.08), 0)

    # Rear Diffuser & Quad Exhaust Tips
    diff = Part.makeBox(46.0, 7.0, 2.0, App.Vector(-23.0, -2.0, 8.5))
    for fx in [-15.0, -7.5, 0.0, 7.5, 15.0]:
        diff = diff.fuse(Part.makeBox(1.8, 7.0, 7.0, App.Vector(fx - 0.9, -2.0, 2.0)))
    for side in [-1, 1]:
        for off in [10.0, 14.5]:
            p = Part.makeCylinder(2.0, 4.5, App.Vector(side * off, 1.0, 13.5), App.Vector(0, -1, 0))
            b = Part.makeCylinder(1.3, 5.5, App.Vector(side * off, 1.5, 13.5), App.Vector(0, -1, 0))
            diff = diff.fuse(p).cut(b)
    add_solid(grp_ext, "Rear_Diffuser_And_Exhaust", diff, (0.15, 0.15, 0.17), 0)

# ==========================================
# MODULE 05: SEALED REAR SPEAKER ENCLOSURE
# ==========================================
def build_audio_enclosure():
    box_w, box_l, box_h = 44.0, 36.0, 10.3
    chamber_out = Part.makeBox(box_w, box_l, box_h, App.Vector(-box_w/2.0, 1.0, 16.2))
    chamber_in  = Part.makeBox(box_w - 4.4, box_l - 4.4, box_h - 3.5, App.Vector(-(box_w - 4.4)/2.0, 3.2, 18.2))
    enclosure = chamber_out.cut(chamber_in)
    enclosure = enclosure.cut(Part.makeCylinder(SPK_D / 2.0, 5.0, App.Vector(0, 19.0, 22.5)))
    enclosure = enclosure.cut(Part.makeCylinder((SPK_D / 2.0) + 1.5, 1.2, App.Vector(0, 19.0, 25.3)))
    add_solid(grp_audio, "Sealed_Speaker_Enclosure_36mm", enclosure, (0.2, 0.22, 0.25), 0)

# ==========================================
# MODULE 03, 04 & 06: CHASSIS, TOP-MOUNT PCB DECK & 34mm MARKET WHEELS
# ==========================================
def build_chassis_pcb_and_market_wheels():
    deck = Part.makeBox(CHASSIS_W, 148.0, 2.5, App.Vector(-CHASSIS_W/2.0, 4.0, 0))
    rail_l = Part.makeBox(3.0, 125.0, 8.5, App.Vector(-CHASSIS_W/2.0, 15.0, 0))
    rail_r = Part.makeBox(3.0, 125.0, 8.5, App.Vector(CHASSIS_W/2.0 - 3.0, 15.0, 0))
    chassis = deck.fuse(rail_l).fuse(rail_r)

    # Rear N20 + Bearing Gearbox
    gb_h = 16.2
    z_ax = gb_h / 2.0
    rear_gb = Part.makeBox(48.0, 36.0, gb_h, App.Vector(-24.0, 0, 0))
    rear_gb = rear_gb.cut(Part.makeBox(N20_W, N20_L, N20_H, App.Vector(-N20_W/2.0, 3.0, z_ax - N20_H/2.0)))
    rear_gb = rear_gb.cut(Part.makeBox(16.0, 14.0, 12.0, App.Vector(-8.0, 19.0, z_ax - 6.0)))
    rear_gb = rear_gb.cut(Part.makeCylinder(1.65, 50.0, App.Vector(-25.0, REAR_AXLE_Y, z_ax), App.Vector(1, 0, 0)))
    rear_low = rear_gb.cut(Part.makeBox(54.0, 42.0, gb_h, App.Vector(-27.0, -3.0, z_ax)))
    rear_up  = rear_gb.cut(Part.makeBox(54.0, 42.0, gb_h, App.Vector(-27.0, -3.0, z_ax - gb_h)))
    chassis = chassis.fuse(rear_low)
    add_solid(grp_chas, "Rear_Gearbox_Upper_Cap", rear_up, (0.3, 0.35, 0.4), 0)

    # 4x Pillars supporting Electronics Deck at Z = 22.0 mm (2S 18650 Battery sits underneath!)
    for px in [-CHASSIS_W/2.0 + 3.5, CHASSIS_W/2.0 - 3.5]:
        for py in [42.0, 122.0]:
            chassis = chassis.fuse(Part.makeCylinder(3.2, TRAY_Z - 2.5, App.Vector(px, py, 2.5)))

    # Front SG92R Servo & C-Hub Bridge
    front_y0 = 132.0
    total_ch = CHUB_GAP + (CHUB_ARM_T * 2)
    chassis = chassis.fuse(Part.makeBox(FRONT_TRACK + 8.0, 18.0, CHUB_ARM_T, App.Vector(-(FRONT_TRACK + 8.0)/2.0, front_y0, 0)))
    s_blk = Part.makeBox(SERVO_L + 10.0, SERVO_W + 6.0, SERVO_H, App.Vector(-(SERVO_L + 10.0)/2.0, front_y0, 0))
    s_pkt = Part.makeBox(SERVO_L, SERVO_W, SERVO_H + 1.0, App.Vector(-SERVO_L/2.0, front_y0 + 3.0, 2.0))
    chassis = chassis.fuse(s_blk.cut(s_pkt))

    for side in [-1, 1]:
        xp = side * (FRONT_TRACK / 2.0)
        cx = xp - (side * 6.5) - 2.0
        chassis = chassis.fuse(Part.makeBox(4.0, 12.0, total_ch, App.Vector(cx, front_y0 + 3.0, 0)))
        ax = min(cx, xp - 4.0)
        aw = abs(xp - cx) + 4.5
        chassis = chassis.fuse(Part.makeBox(aw, 12.0, CHUB_ARM_T, App.Vector(ax, front_y0 + 3.0, total_ch - CHUB_ARM_T)))
        chassis = chassis.cut(Part.makeCylinder(1.05, total_ch + 2.0, App.Vector(xp, front_y0 + 9.0, -1.0)))

    add_solid(grp_chas, "Main_Chassis_Base", chassis, (0.25, 0.25, 0.28), 0)

    # Electronics Deck (Z = 22.0 mm): Audio Modules at Rear (Y=42..70), PCB Mounted ON TOP at Front (Y=74..120)
    pcb_deck = Part.makeBox(CHASSIS_W, 86.0, 2.0, App.Vector(-CHASSIS_W/2.0, 38.0, TRAY_Z))
    # 4x M2 Standoffs ON TOP of deck for 46x32mm Carrier PCB (Y = 74 to 120 mm)
    for mx in [-13.5, 13.5]:
        for my in [76.5, 117.5]:
            pcb_deck = pcb_deck.fuse(Part.makeCylinder(2.4, 3.5, App.Vector(mx, my, TRAY_Z + 2.0)))
    add_solid(grp_elec, "Low_Profile_PCB_Deck", pcb_deck, (0.1, 0.45, 0.25), 0)

    # Visual Reference: Carrier PCB + ESP32-CAM Mounted ON TOP of Deck (Z = 25.5 to 36.0 mm)
    pcb_board = Part.makeBox(32.0, 46.0, 1.6, App.Vector(-16.0, 74.0, TRAY_Z + 5.5))
    add_solid(grp_elec, "Carrier_PCB_Top_Mounted_Ref", pcb_board, (0.05, 0.35, 0.15), 25)

    # Off-the-Shelf Market 34mm x 15mm N20 Rubber Wheels (Reference Fitment Check)
    for y_ax, prefix in [(REAR_AXLE_Y, "Rear"), (FRONT_AXLE_Y, "Front")]:
        for side, s_lbl in [(-1, "L"), (1, "R")]:
            wx = side * 21.0
            hub = Part.makeCylinder(11.0, MARKET_WHEEL_W, App.Vector(wx, y_ax, 8.1), App.Vector(side, 0, 0)).cut(
                  Part.makeCylinder(1.5, MARKET_WHEEL_W + 2.0, App.Vector(wx - side, y_ax, 8.1), App.Vector(side, 0, 0)))
            rubber = Part.makeCylinder(MARKET_WHEEL_OD / 2.0, MARKET_WHEEL_W, App.Vector(wx, y_ax, 8.1), App.Vector(side, 0, 0)).cut(
                     Part.makeCylinder(11.0, MARKET_WHEEL_W + 2.0, App.Vector(wx - side, y_ax, 8.1), App.Vector(side, 0, 0)))
            add_solid(grp_wheel, f"Market_34mm_Hub_{prefix}_{s_lbl}", hub, (0.85, 0.72, 0.1), 0)
            add_solid(grp_wheel, f"Market_34mm_Rubber_{prefix}_{s_lbl}", rubber, (0.12, 0.12, 0.13), 0)

build_exterior_glass_lights()
build_audio_enclosure()
build_chassis_pcb_and_market_wheels()

doc.recompute()
if App.GuiUp:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewAxonometric()
    Gui.SendMsgToActiveView("ViewFit")
