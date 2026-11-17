import FreeCAD as App
import Part
import math

doc = App.newDocument("Ferrari_Enzo_Modular_Assembly")

# ==========================================
# MASTER VEHICLE PARAMETERS (mm)
# ==========================================
TOL = 0.15
FLOOR_T = 3.0
WHEELBASE = 115.0
REAR_AXLE_Y = 26.0
FRONT_AXLE_Y = REAR_AXLE_Y + WHEELBASE    # 141.0 mm

CHASSIS_W = 54.0
FENDER_W = 74.0
TRAY_Z = 22.0                             # Low-profile electronics deck above 2S battery
ROOF_Z = 38.5                             # True low-slung Enzo roof height

WALL = 2.0
CLEARANCE = 0.4
INNER_W = CHASSIS_W + (CLEARANCE * 2.0)   # 54.8 mm snap-fit cavity

# Hardware Dimensions
SPK_D = 36.2                              # 36mm 3W speaker outer diameter
SPK_MAG_D = 22.0                          # Speaker magnet diameter
N20_W, N20_H, N20_L = 12.15, 10.15, 16.0
SERVO_L, SERVO_W, SERVO_H = 23.25, 12.65, 15.5
FRONT_TRACK = 66.0
CHUB_GAP, CHUB_ARM_T = 14.0, 3.5

# Helper: Create valid, refined Part::Feature inside an App::Part container
def add_solid(group, name, shape, color=(0.8, 0.8, 0.8), transparency=0):
    clean_shape = shape.removeSplitter()
    if not clean_shape.isValid():
        App.Console.PrintWarning(f"Geometry warning on {name}: attempting fix...\n")
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
# CREATE MODULAR ASSEMBLY CONTAINERS (App::Part)
# ==========================================
grp_ext   = doc.addObject("App::Part", "01_Exterior_Body")
grp_glass = doc.addObject("App::Part", "02_Glass_And_Lights")
grp_chas  = doc.addObject("App::Part", "03_Chassis_And_Steering")
grp_wheel = doc.addObject("App::Part", "04_Wheels_And_Tires")
grp_audio = doc.addObject("App::Part", "05_Audio_System")
grp_elec  = doc.addObject("App::Part", "06_Electronics_Deck")

# ==========================================
# MODULE 01 & 02: EXTERIOR BODY, DIFFUSER & SEPARATE LENSES
# ==========================================
def build_exterior_and_glass():
    hw_f = FENDER_W / 2.0
    hw_in = INNER_W / 2.0

    # Wide Fender Body Loft
    w_rear   = make_wire(-2.0,  hw_f - 2.0, 2.5, 22.0, 27.5, 28.0)
    w_haunch = make_wire(32.0,  hw_f,       1.0, 23.0, 28.5, 31.0)
    w_waist  = make_wire(82.0,  hw_f - 2.5, 1.0, 21.0, 25.5, 29.0)
    w_ffend  = make_wire(138.0, hw_f - 0.5, 1.5, 21.5, 26.5, 29.5)
    w_front  = make_wire(163.0, hw_f - 5.0, 2.0, 13.0, 17.5, 25.0)
    fender_body = Part.makeLoft([w_rear, w_haunch, w_waist, w_ffend, w_front], True)

    # Central Teardrop Canopy + F1 Nose Cone
    c_rear   = make_wire(0.0,   16.0, 10.0, 25.0, 28.5, 11.0)
    c_spk    = make_wire(30.0,  21.5, 10.0, 29.5, 34.5, 15.5)
    c_cock1  = make_wire(72.0,  22.5, 10.0, 32.0, ROOF_Z, 15.5)
    c_cock2  = make_wire(105.0, 21.0, 10.0, 30.0, 36.5, 14.5)
    c_hood   = make_wire(136.0, 14.0,  6.0, 21.0, 24.5,  9.5)
    c_f1nose = make_wire(169.0,  7.5,  3.5, 11.5, 14.5,  5.0)
    canopy = Part.makeLoft([c_rear, c_spk, c_cock1, c_cock2, c_hood, c_f1nose], True)

    outer = fender_body.fuse(canopy)

    # Interior Cavity (2.0mm shell wall)
    wi_rear   = make_wire(0.0,   hw_in,       -2.0, 21.0, 26.0, 25.0)
    wi_haunch = make_wire(32.0,  hw_in,       -2.0, 22.0, 32.5, 19.5)
    wi_waist  = make_wire(82.0,  hw_in,       -2.0, 28.0, ROOF_Z - WALL, 15.0)
    wi_ffend  = make_wire(136.0, hw_in,       -2.0, 19.5, 24.5, 16.0)
    wi_front  = make_wire(160.5, hw_in - 3.0, -2.0, 11.0, 15.5, 14.0)
    cavity = Part.makeLoft([wi_rear, wi_haunch, wi_waist, wi_ffend, wi_front], True)

    shell = outer.cut(cavity)

    # Outer-Only Wheel Arches (Preserves F1 Nose & Center Spine)
    for side in [-1, 1]:
        x_start = 17.5 if side == 1 else -(hw_f + 5.0)
        span = (hw_f + 5.0) - 17.5
        shell = shell.cut(Part.makeCylinder(19.5, span, App.Vector(x_start, REAR_AXLE_Y, 7.5), App.Vector(1, 0, 0)))
        shell = shell.cut(Part.makeCylinder(20.5, span, App.Vector(x_start, FRONT_AXLE_Y, 7.5), App.Vector(1, 0, 0)))

    # Front Grille Intakes & Side NACA Air Scoops
    for side in [-1, 1]:
        ix = 8.5 if side == 1 else -28.5
        shell = shell.cut(Part.makeBox(20.0, 10.0, 8.5, App.Vector(ix, 156.0, 4.0)))
        sx = (hw_f - 4.5) if side == 1 else -(hw_f + 1.0)
        shell = shell.cut(Part.makeBox(5.5, 30.0, 12.0, App.Vector(sx, 50.0, 8.0)))

    # Recessed Windshield Frame (1.3mm Step Seat) + Separate Clear Windshield Insert
    ws_outer_cut = Part.makeBox(26.0, 22.0, 11.0, App.Vector(-13.0, 102.0, 24.5))
    shell = shell.cut(ws_outer_cut)

    # Separate Clear Windshield Frame with Unobstructed Center Camera Aperture
    ws_glass = Part.makeBox(25.4, 1.2, 10.2, App.Vector(-12.7, 112.0, 24.8))
    ws_glass.rotate(App.Vector(0, 112.0, 24.8), App.Vector(1, 0, 0), -28.0)
    cam_aperture = Part.makeCylinder(5.5, 12.0, App.Vector(0, 106.0, 29.0), App.Vector(0, 1, 0))
    ws_glass = ws_glass.cut(cam_aperture)
    add_solid(grp_glass, "Front_Windshield_Clear_Insert", ws_glass, (0.6, 0.85, 0.95), 65)

    # Side Windows Cutout + Separate Clear Side Glass Inserts
    shell = shell.cut(Part.makeBox(FENDER_W + 4.0, 26.0, 8.5, App.Vector(-FENDER_W/2 - 2.0, 70.0, 26.0)))
    for side, sname in [(-1, "Side_Glass_L"), (1, "Side_Glass_R")]:
        gx = (16.5) if side == 1 else -17.5
        s_glass = Part.makeBox(1.0, 25.4, 8.0, App.Vector(gx, 70.3, 26.2))
        add_solid(grp_glass, sname, s_glass, (0.6, 0.85, 0.95), 65)

    # Headlight Housings + Separate Clear Headlight Covers
    for side, lname in [(-1, "Headlight_Lens_L"), (1, "Headlight_Lens_R")]:
        lx = (side * 23.5) - 3.5
        shell = shell.cut(Part.makeBox(7.2, 14.2, 4.2, App.Vector(lx - 0.1, 146.9, 20.9)))
        shell = shell.cut(Part.makeCylinder(2.6, 18.0, App.Vector(side * 23.5, 142.0, 18.5), App.Vector(0, 1, 0)))
        lens = Part.makeBox(6.8, 13.8, 1.2, App.Vector(lx + 0.1, 147.1, 22.8))
        add_solid(grp_glass, lname, lens, (0.9, 0.95, 1.0), 50)

    # Rear Engine Speaker Louvers + Snap-On Rocker Clips
    for sy in [10.0, 15.0, 20.0, 25.0, 30.0]:
        shell = shell.cut(Part.makeBox(28.0, 2.5, 10.0, App.Vector(-14.0, sy, 26.0)))

    for side in [-1, 1]:
        web_x = side * (hw_in - 0.5) - (2.2 if side == 1 else 0.0)
        lip_x = side * (hw_in - 1.8) - (1.8 if side == 1 else 0.0)
        shell = shell.fuse(Part.makeBox(2.2, 38.0, 4.0, App.Vector(web_x, 55.0, -1.5)))
        shell = shell.fuse(Part.makeBox(1.8, 38.0, 1.5, App.Vector(lip_x, 55.0, -1.5)))

    add_solid(grp_ext, "Main_Body_Shell_Enzo", shell, (0.85, 0.08, 0.08), 0)

    # Separate Rear Diffuser & Quad Exhaust Module (Printable in Matte Black PETG)
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
# MODULE 05: SEALED REAR ACOUSTIC SPEAKER ENCLOSURE
# ==========================================
def build_audio_enclosure():
    # Sealed Chamber sitting atop Rear Gearbox (Y = 1..37mm, Z = 16.2..26.5mm)
    # Internal sealed volume ~ 15.5 cm^3 with magnet clearance & TPU gasket seat
    box_w, box_l, box_h = 44.0, 36.0, 10.3
    chamber_out = Part.makeBox(box_w, box_l, box_h, App.Vector(-box_w/2.0, 1.0, 16.2))
    chamber_in  = Part.makeBox(box_w - 4.4, box_l - 4.4, box_h - 3.5, App.Vector(-(box_w - 4.4)/2.0, 3.2, 18.2))
    enclosure = chamber_out.cut(chamber_in)

    # Top Speaker Bore (36.2mm) + 1.2mm Recessed Gasket Seat
    spk_hole = Part.makeCylinder(SPK_D / 2.0, 5.0, App.Vector(0, 19.0, 22.5))
    gasket_seat = Part.makeCylinder((SPK_D / 2.0) + 1.5, 1.2, App.Vector(0, 19.0, 25.3))
    enclosure = enclosure.cut(spk_hole).cut(gasket_seat)

    # 4x M2 Mounting Bosses around Speaker Flange
    for ang in [45, 135, 225, 315]:
        bx = 20.5 * math.cos(math.radians(ang))
        by = 19.0 + 20.5 * math.sin(math.radians(ang))
        enclosure = enclosure.cut(Part.makeCylinder(0.85, 6.0, App.Vector(bx, by, 21.0)))

    add_solid(grp_audio, "Sealed_Speaker_Enclosure_36mm", enclosure, (0.2, 0.22, 0.25), 0)

    # Separate Printable TPU Speaker Gasket Ring
    gasket = Part.makeCylinder((SPK_D / 2.0) + 1.4, 1.2, App.Vector(0, 19.0, 25.4)).cut(
             Part.makeCylinder((SPK_D / 2.0) - 1.5, 2.0, App.Vector(0, 19.0, 25.0)))
    add_solid(grp_audio, "TPU_Speaker_Gasket", gasket, (0.1, 0.6, 0.6), 0)

# ==========================================
# MODULE 03, 04 & 06: CHASSIS, STEERING, WHEELS & LOW-PROFILE PCB DECK
# ==========================================
def build_chassis_electronics_wheels():
    # Main Chassis Base Plate (2.5mm belly pan + side rails + rear N20 lower gearbox + front C-hubs)
    deck = Part.makeBox(CHASSIS_W, 148.0, 2.5, App.Vector(-CHASSIS_W/2.0, 4.0, 0))
    rail_l = Part.makeBox(3.0, 125.0, 8.5, App.Vector(-CHASSIS_W/2.0, 15.0, 0))
    rail_r = Part.makeBox(3.0, 125.0, 8.5, App.Vector(CHASSIS_W/2.0 - 3.0, 15.0, 0))
    chassis = deck.fuse(rail_l).fuse(rail_r)

    # Rear Gearbox Lower Half (Z = 0..8.1mm)
    gb_h = 16.2
    z_ax = gb_h / 2.0
    rear_gb = Part.makeBox(48.0, 36.0, gb_h, App.Vector(-24.0, 0, 0))
    rear_gb = rear_gb.cut(Part.makeBox(N20_W, N20_L, N20_H, App.Vector(-N20_W/2.0, 3.0, z_ax - N20_H/2.0)))
    rear_gb = rear_gb.cut(Part.makeBox(16.0, 14.0, 12.0, App.Vector(-8.0, 19.0, z_ax - 6.0)))
    rear_gb = rear_gb.cut(Part.makeCylinder(1.65, 50.0, App.Vector(-25.0, REAR_AXLE_Y, z_ax), App.Vector(1, 0, 0)))
    rear_gb = rear_gb.cut(Part.makeCylinder(3.04, 3.1, App.Vector(-24.5, REAR_AXLE_Y, z_ax), App.Vector(1, 0, 0)))
    rear_gb = rear_gb.cut(Part.makeCylinder(3.04, 3.1, App.Vector(21.4, REAR_AXLE_Y, z_ax), App.Vector(1, 0, 0)))

    rear_low = rear_gb.cut(Part.makeBox(54.0, 42.0, gb_h, App.Vector(-27.0, -3.0, z_ax)))
    rear_up  = rear_gb.cut(Part.makeBox(54.0, 42.0, gb_h, App.Vector(-27.0, -3.0, z_ax - gb_h)))
    chassis = chassis.fuse(rear_low)
    add_solid(grp_chas, "Rear_Gearbox_Upper_Cap", rear_up, (0.3, 0.35, 0.4), 0)

    # 4x Low-Profile Pillars supporting Electronics Deck at Z = 22.0 mm
    for px in [-CHASSIS_W/2.0 + 3.5, CHASSIS_W/2.0 - 3.5]:
        for py in [42.0, 118.0]:
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

    # Low-Profile Electronics & PCB Deck (Z = 22.0 mm, fits cleanly under 38.5mm Enzo canopy)
    pcb_deck = Part.makeBox(CHASSIS_W, 84.0, 2.0, App.Vector(-CHASSIS_W/2.0, 38.0, TRAY_Z))
    for mx in [-13.5, 13.5]:
        for my in [68.0, 109.0]:
            pcb_deck = pcb_deck.fuse(Part.makeCylinder(2.4, 3.5, App.Vector(mx, my, TRAY_Z + 2.0)))
    add_solid(grp_elec, "Low_Profile_PCB_Deck", pcb_deck, (0.1, 0.45, 0.25), 0)

    # 4x Wheels & TPU Tires Positioned on Axles
    for y_ax, prefix in [(REAR_AXLE_Y, "Rear"), (FRONT_AXLE_Y, "Front")]:
        for side, s_lbl in [(-1, "L"), (1, "R")]:
            wx = side * 26.5
            rim = Part.makeCylinder(12.0, 13.0, App.Vector(wx, y_ax, 8.1), App.Vector(side, 0, 0)).cut(
                  Part.makeCylinder(1.55, 15.0, App.Vector(wx - side, y_ax, 8.1), App.Vector(side, 0, 0)))
            tire = Part.makeCylinder(16.8, 13.0, App.Vector(wx, y_ax, 8.1), App.Vector(side, 0, 0)).cut(
                   Part.makeCylinder(11.9, 15.0, App.Vector(wx - side, y_ax, 8.1), App.Vector(side, 0, 0)))
            add_solid(grp_wheel, f"{prefix}_Rim_{s_lbl}", rim, (0.75, 0.75, 0.78), 0)
            add_solid(grp_wheel, f"{prefix}_TPU_Tire_{s_lbl}", tire, (0.12, 0.12, 0.13), 0)

build_exterior_and_glass()
build_audio_enclosure()
build_chassis_electronics_wheels()

doc.recompute()
if App.GuiUp:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewAxonometric()
    Gui.SendMsgToActiveView("ViewFit")
