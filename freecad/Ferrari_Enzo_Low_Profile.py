import FreeCAD as App
import Part

doc = App.newDocument("Ferrari_Enzo_Low_Profile_RC")

# ==========================================
# LOW-PROFILE FERRARI ENZO PARAMETERS (mm)
# ==========================================
TOL = 0.15
FLOOR_T = 3.0
WHEELBASE = 115.0
CHASSIS_W = 54.0            # Inner chassis belly pan width
TRAY_Z = 22.0               # Lowered from 37mm -> 22mm (sits right above 2S battery!)
ROOF_Z = 38.5               # Lowered from 65mm -> 38.5mm for true supercar height!

WALL = 2.0
CLEARANCE = 0.4
INNER_W = CHASSIS_W + (CLEARANCE * 2.0)   # 54.8 mm chassis snap-fit width
FENDER_W = 74.0                           # Wide 74mm Ferrari Enzo supercar stance

REAR_AXLE_Y = 26.0
FRONT_AXLE_Y = 141.0
SPK_D = 36.5                # 36mm 3W Speaker mounted on top of Rear Gearbox

# Helper: Closed 6-point polygonal cross-section wire in X-Z plane
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
# 1. FERRARI ENZO LOW-SLUNG SUPERCAR SHELL
# ==========================================
def build_ferrari_enzo_shell():
    hw_fender = FENDER_W / 2.0      # 37.0 mm outer fender half-width
    hw_in = INNER_W / 2.0           # 27.4 mm inner chassis clip half-width

    # --- A. Outer Wide Fender Body (Low 26-28mm Deck Height) ---
    w_rear   = make_wire(-2.0,  hw_fender - 2.0, 2.5, 22.0, 27.5, 28.0)
    w_haunch = make_wire(32.0,  hw_fender,       1.0, 23.0, 28.5, 31.0)
    w_waist  = make_wire(82.0,  hw_fender - 2.5, 1.0, 21.0, 25.5, 29.0)
    w_ffend  = make_wire(138.0, hw_fender - 0.5, 1.5, 21.5, 26.5, 29.5)
    w_front  = make_wire(163.0, hw_fender - 5.0, 2.0, 13.0, 17.5, 25.0)
    fender_body = Part.makeLoft([w_rear, w_haunch, w_waist, w_ffend, w_front], True)

    # --- B. Central Teardrop Canopy + F1 Protruding Nose Cone ---
    c_rear   = make_wire(0.0,   16.0, 10.0, 25.0, 28.5, 11.0)
    c_spk    = make_wire(30.0,  21.0, 10.0, 29.0, 34.0, 15.0) # Clears rear-gearbox speaker
    c_cock1  = make_wire(72.0,  22.5, 10.0, 32.0, ROOF_Z, 15.5)
    c_cock2  = make_wire(105.0, 21.0, 10.0, 30.0, 36.5, 14.5)
    c_hood   = make_wire(136.0, 14.0,  6.0, 21.0, 24.5,  9.5)
    c_f1nose = make_wire(169.0,  7.5,  3.5, 11.5, 14.5,  5.0) # F1 Center Nose Tip
    canopy_spine = Part.makeLoft([c_rear, c_spk, c_cock1, c_cock2, c_hood, c_f1nose], True)

    outer_enzo = fender_body.fuse(canopy_spine)

    # --- C. Hollow Interior Cavity (Leaves 2.0mm Shell & 54.8mm Inner Snap Bay) ---
    wi_rear   = make_wire(0.0,   hw_in,       -2.0, 21.0, 26.0, 25.0)
    wi_haunch = make_wire(32.0,  hw_in,       -2.0, 22.0, 32.0, 19.0)
    wi_waist  = make_wire(82.0,  hw_in,       -2.0, 28.0, ROOF_Z - WALL, 15.0)
    wi_ffend  = make_wire(136.0, hw_in,       -2.0, 19.5, 24.5, 16.0)
    wi_front  = make_wire(160.5, hw_in - 3.0, -2.0, 11.0, 15.5, 14.0)
    inner_cavity = Part.makeLoft([wi_rear, wi_haunch, wi_waist, wi_ffend, wi_front], True)

    enzo = outer_enzo.cut(inner_cavity)

    # --- D. OUTER-ONLY Wheel Arch Cutouts (Never cuts the center nose!) ---
    for side in [-1, 1]:
        x_start = (17.5) if side == 1 else -(hw_fender + 5.0)
        cut_span = (hw_fender + 5.0) - 17.5

        r_arch = Part.makeCylinder(
            19.5, cut_span,
            App.Vector(x_start, REAR_AXLE_Y, 7.5),
            App.Vector(1, 0, 0)
        )
        f_arch = Part.makeCylinder(
            20.5, cut_span,
            App.Vector(x_start, FRONT_AXLE_Y, 7.5),
            App.Vector(1, 0, 0)
        )
        enzo = enzo.cut(r_arch).cut(f_arch)

    # --- E. Twin Ferrari Enzo Front Grille Intakes (Flanking F1 Nose) ---
    for side in [-1, 1]:
        ix = 8.5 if side == 1 else -28.5
        intake = Part.makeBox(20.0, 10.0, 8.5, App.Vector(ix, 156.0, 4.0))
        enzo = enzo.cut(intake)

    # --- F. Swept-Back Fender Headlight Recesses + 5mm LED Ports ---
    for side in [-1, 1]:
        lx = (side * 23.5) - 3.5
        lens_pkt = Part.makeBox(7.0, 14.0, 4.0, App.Vector(lx, 147.0, 21.0))
        led_bore = Part.makeCylinder(2.6, 18.0, App.Vector(side * 23.5, 142.0, 18.5), App.Vector(0, 1, 0))
        enzo = enzo.cut(lens_pkt).cut(led_bore)

    # --- G. Wrap-Around Windshield Viewport for ESP32-CAM & Side Windows ---
    windshield = Part.makeBox(26.0, 22.0, 11.0, App.Vector(-13.0, 102.0, 24.5))
    side_win = Part.makeBox(FENDER_W + 4.0, 28.0, 9.0, App.Vector(-FENDER_W/2 - 2.0, 68.0, 25.5))
    enzo = enzo.cut(windshield).cut(side_win)

    # --- H. Deep Sculpted Side NACA Air Scoops Ahead of Rear Wheels ---
    for side in [-1, 1]:
        sx = (hw_fender - 4.5) if side == 1 else -(hw_fender + 1.0)
        scoop = Part.makeBox(5.5, 30.0, 12.0, App.Vector(sx, 50.0, 8.0))
        enzo = enzo.cut(scoop)

    # --- I. Rear Engine Deck Speaker Louvers (Directly over Rear Gearbox Speaker at Y=10..34) ---
    for sy in [10.0, 15.0, 20.0, 25.0, 30.0]:
        louver = Part.makeBox(28.0, 2.5, 10.0, App.Vector(-14.0, sy, 26.0))
        enzo = enzo.cut(louver)

    # --- J. Rear Diffuser Strakes & Quad Exhaust Pipes ---
    for fx in [-14.0, -7.0, 0.0, 7.0, 14.0]:
        fin = Part.makeBox(1.6, 7.0, 7.5, App.Vector(fx - 0.8, -2.0, 2.0))
        enzo = enzo.fuse(fin)

    for side in [-1, 1]:
        for offset in [10.0, 14.5]:
            pipe = Part.makeCylinder(2.0, 4.0, App.Vector(side * offset, -2.0, 14.0), App.Vector(0, -1, 0))
            bore = Part.makeCylinder(1.3, 5.0, App.Vector(side * offset, -1.5, 14.0), App.Vector(0, -1, 0))
            enzo = enzo.fuse(pipe).cut(bore)

    # --- K. Snap-On Chassis Rocker Clips (Lock onto 54.0mm Chassis Floor at Y=55..95) ---
    for side in [-1, 1]:
        clip_y0, clip_len = 55.0, 38.0
        web_x = side * (hw_in - 0.5) - (2.2 if side == 1 else 0.0)
        lip_x = side * (hw_in - 1.8) - (1.8 if side == 1 else 0.0)
        web = Part.makeBox(2.2, clip_len, 4.0, App.Vector(web_x, clip_y0, -1.5))
        lip = Part.makeBox(1.8, clip_len, 1.5, App.Vector(lip_x, clip_y0, -1.5))
        enzo = enzo.fuse(web).fuse(lip)

    obj_enzo = doc.addObject("Part::Feature", "Ferrari_Enzo_Low_Shell")
    obj_enzo.Shape = enzo

# ==========================================
# 2. REAR GEARBOX CAP WITH TOP SPEAKER MOUNT
# ==========================================
def build_rear_gearbox_speaker_cap():
    gb_len = 36.0
    re_span = 48.0
    cap_h = 8.1

    # Upper Clamshell Cap of Rear N20 + Bearing Gearbox (Sits at Z = 8.1 to 16.2 mm)
    cap_box = Part.makeBox(re_span, gb_len, cap_h, App.Vector(-re_span / 2.0, 0, 8.1))
    n20_top = Part.makeBox(12.15, 16.0, 5.1, App.Vector(-6.075, 3.0, 8.1))
    cpl_top = Part.makeBox(16.0, 14.0, 6.0, App.Vector(-8.0, 19.0, 8.1))
    axle_top = Part.makeCylinder(1.65, re_span + 2.0, App.Vector(-re_span/2 - 1.0, 26.0, 8.1), App.Vector(1, 0, 0))
    brg_l = Part.makeCylinder(3.04, 3.1, App.Vector(-re_span/2 - 0.5, 26.0, 8.1), App.Vector(1, 0, 0))
    brg_r = Part.makeCylinder(3.04, 3.1, App.Vector(re_span/2 - 2.6, 26.0, 8.1), App.Vector(1, 0, 0))

    cap = cap_box.cut(n20_top).cut(cpl_top).cut(axle_top).cut(brg_l).cut(brg_r)

    # 36mm Speaker Acoustic Ring Mounted Directly on Top of Rear Gearbox (Z = 16.2 to 24.5 mm)
    spk_ring = Part.makeCylinder(SPK_D / 2.0 + 2.2, 8.3, App.Vector(0, 19.0, 16.2))
    spk_bore = Part.makeCylinder(SPK_D / 2.0, 9.0, App.Vector(0, 19.0, 16.2))
    cap = cap.fuse(spk_ring).cut(spk_bore)

    for sx in [-re_span / 2.0 + 4.0, re_span / 2.0 - 4.0]:
        for sy in [5.0, gb_len - 5.0]:
            cap = cap.cut(Part.makeCylinder(1.05, 18.0, App.Vector(sx, sy, 7.0)))

    cap.translate(App.Vector(-75.0, 0, -8.1))  # Placed beside shell at Z=0
    obj_cap = doc.addObject("Part::Feature", "Rear_Gearbox_With_Speaker_Mount")
    obj_cap.Shape = cap

build_ferrari_enzo_shell()
build_rear_gearbox_speaker_cap()

doc.recompute()
if App.GuiUp:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewAxonometric()
    Gui.SendMsgToActiveView("ViewFit")