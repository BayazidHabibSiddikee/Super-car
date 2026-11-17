import FreeCAD as App
import Part

doc = App.newDocument("Jeep_And_Ferrari_RC_Shells")

# ==========================================
# SHARED CHASSIS INTERFACE DIMENSIONS (mm)
# ==========================================
CHASSIS_W = 54.0            # Matches Main_Chassis_Base width
CLEARANCE = 0.4             # Slip-fit margin per side
WALL = 2.0                  # 2.0mm rugged PETG shell wall
INNER_W = CHASSIS_W + (CLEARANCE * 2.0)   # 54.8 mm inner cavity width
OUTER_W = INNER_W + (WALL * 2.0)          # 58.8 mm base body width

REAR_AXLE_Y = 26.0          # Matches Rear Gearbox axle center
FRONT_AXLE_Y = 141.0        # Matches Front C-Hub kingpin center
ROOF_Z = 65.0               # Clears ESP32-CAM (59.5mm) + air gap

# Helper: 6-point closed cross-section wire for reliable Loft generation
def make_section_wire(y_pos, half_w, z_bot, z_belt, z_top, roof_half_w):
    pts = [
        App.Vector(-half_w, y_pos, z_bot),
        App.Vector(-half_w, y_pos, z_belt),
        App.Vector(-roof_half_w, y_pos, z_top),
        App.Vector(roof_half_w, y_pos, z_top),
        App.Vector(half_w, y_pos, z_belt),
        App.Vector(half_w, y_pos, z_bot),
        App.Vector(-half_w, y_pos, z_bot)
    ]
    return Part.Wire(Part.makePolygon(pts).Edges)

# Helper: Shared internal chassis cuts (wheel arches, snap clips, camera, LEDs, SD slot)
def apply_chassis_cuts_and_clips(shell):
    hw_in = INNER_W / 2.0

    # 1. Rear & Front Wheel Arches (Front is wider for +/-40 deg steering lock)
    rear_arch = Part.makeCylinder(20.0, OUTER_W + 20.0, App.Vector(-OUTER_W/2 - 10.0, REAR_AXLE_Y, 8.0), App.Vector(1, 0, 0))
    front_arch = Part.makeCylinder(22.5, OUTER_W + 20.0, App.Vector(-OUTER_W/2 - 10.0, FRONT_AXLE_Y, 8.0), App.Vector(1, 0, 0))
    shell = shell.cut(rear_arch).cut(front_arch)

    # 2. Front Bumper 5mm LED Headlight Cutouts (Aligned with chassis bumper at X=+/-16, Z=8.5)
    led_l = Part.makeCylinder(3.5, 20.0, App.Vector(-16.0, 148.0, 8.5), App.Vector(0, 1, 0))
    led_r = Part.makeCylinder(3.5, 20.0, App.Vector(16.0, 148.0, 8.5), App.Vector(0, 1, 0))
    shell = shell.cut(led_l).cut(led_r)

    # 3. Rear USB / Audio Access Slot (Y = -5 to 4 mm, Z = 26 to 38 mm)
    usb_slot = Part.makeBox(18.0, 10.0, 12.0, App.Vector(-9.0, -5.0, 26.0))
    shell = shell.cut(usb_slot)

    # 4. Snap-On Rocker Retention Clips (Lock under the 3.0mm chassis floor at Y = 62..96 mm)
    for side in [-1, 1]:
        clip_len = 34.0
        clip_y0 = 62.0
        skirt_x = side * (hw_in - 0.8) - (0.8 if side == 1 else 0.0)
        skirt = Part.makeBox(0.8, clip_len, 4.0, App.Vector(skirt_x, clip_y0, -1.5))
        lip_x = side * (hw_in - 1.8) - (1.8 if side == 1 else 0.0)
        lip = Part.makeBox(1.8, clip_len, 1.5, App.Vector(lip_x, clip_y0, -1.5))
        shell = shell.fuse(skirt).fuse(lip)

    return shell

# ==========================================
# DESIGN 1: JEEP WRANGLER RUBICON 4x4 SHELL
# ==========================================
def build_jeep_shell():
    hw_out = OUTER_W / 2.0
    hw_in = INNER_W / 2.0

    # Boxy SUV Cabin + Stepped Off-Road Hood Profile
    w_tail   = make_section_wire(-2.0,  hw_out, 2.0, 42.0, ROOF_Z, 25.0)
    w_cabinR = make_section_wire(112.0, hw_out, 1.5, 42.0, ROOF_Z, 25.0)
    w_cowl   = make_section_wire(124.0, hw_out, 1.5, 38.0, 42.0,   24.0)
    w_grille = make_section_wire(162.0, hw_out - 2.0, 2.0, 35.0, 39.0, 22.0)
    outer_jeep = Part.makeLoft([w_tail, w_cabinR, w_cowl, w_grille], True)

    wi_tail   = make_section_wire(0.0,   hw_in, -2.0, 40.0, ROOF_Z - WALL, 23.0)
    wi_cabinR = make_section_wire(111.0, hw_in, -2.0, 40.0, ROOF_Z - WALL, 23.0)
    wi_cowl   = make_section_wire(123.0, hw_in, -2.0, 36.0, 40.0,          22.0)
    wi_grille = make_section_wire(159.5, hw_in - 2.0, -2.0, 33.0, 37.0,    20.0)
    inner_jeep = Part.makeLoft([wi_tail, wi_cabinR, wi_cowl, wi_grille], True)

    jeep = outer_jeep.cut(inner_jeep)

    # Heavy-Duty Trapezoidal Off-Road Fender Flares (Left & Right, Front & Rear)
    for side in [-1, 1]:
        fx = (hw_out - 1.0) if side == 1 else -(hw_out + 4.5)
        rear_flare = Part.makeBox(5.5, 42.0, 24.0, App.Vector(fx, REAR_AXLE_Y - 21.0, 4.0))
        front_flare = Part.makeBox(5.5, 45.0, 25.0, App.Vector(fx, FRONT_AXLE_Y - 22.5, 4.0))
        jeep = jeep.fuse(rear_flare).fuse(front_flare)

    # Apply standard wheel arches, LEDs, and snap clips
    jeep = apply_chassis_cuts_and_clips(jeep)

    # Iconic Jeep 7-Slot Front Grille Cutouts (Y = 158 to 163 mm, Z = 16 to 33 mm)
    for slot_idx in range(-3, 4):
        sx = slot_idx * 5.2
        slot = Part.makeBox(3.0, 6.0, 16.0, App.Vector(sx - 1.5, 158.0, 17.0))
        jeep = jeep.cut(slot)

    # Wide Off-Road Windshield Cutout for ESP32-CAM + Side Safari Windows
    windshield = Part.makeBox(42.0, 20.0, 18.0, App.Vector(-21.0, 110.0, 43.0))
    side_win_f = Part.makeBox(OUTER_W + 4.0, 32.0, 16.0, App.Vector(-OUTER_W/2 - 2.0, 72.0, 44.0))
    side_win_r = Part.makeBox(OUTER_W + 4.0, 34.0, 16.0, App.Vector(-OUTER_W/2 - 2.0, 28.0, 44.0))
    jeep = jeep.cut(windshield).cut(side_win_f).cut(side_win_r)

    # Roof Rack Side Rails + 6x Speaker Acoustic Slots (Y = 48 to 74 mm)
    rail_l = Part.makeBox(2.5, 95.0, 3.0, App.Vector(-21.0, 10.0, ROOF_Z))
    rail_r = Part.makeBox(2.5, 95.0, 3.0, App.Vector(18.5, 10.0, ROOF_Z))
    jeep = jeep.fuse(rail_l).fuse(rail_r)
    for sy in [48.0, 52.5, 57.0, 61.5, 66.0, 70.5]:
        vent = Part.makeBox(28.0, 2.4, 8.0, App.Vector(-14.0, sy, ROOF_Z - 4.0))
        jeep = jeep.cut(vent)

    # Rear Tailgate Spare Tire Ring Boss (Hollow center so weight stays low)
    spare_outer = Part.makeCylinder(14.0, 5.0, App.Vector(0, -2.0, 48.0), App.Vector(0, -1, 0))
    spare_inner = Part.makeCylinder(8.0, 6.0, App.Vector(0, -1.5, 48.0), App.Vector(0, -1, 0))
    jeep = jeep.fuse(spare_outer.cut(spare_inner))

    obj_jeep = doc.addObject("Part::Feature", "Jeep_Wrangler_4x4_Shell")
    obj_jeep.Shape = jeep

# ==========================================
# DESIGN 2: FERRARI F40 / GT SUPERCAR SHELL
# ==========================================
def build_ferrari_shell():
    hw_out = OUTER_W / 2.0
    hw_in = INNER_W / 2.0

    # Sleek Wedge Nose + GT Canopy Dome + Fastback Engine Deck Profile
    w_rear   = make_section_wire(-2.0,  hw_out,       3.5, 34.0, 48.0,   21.0)
    w_eng    = make_section_wire(45.0,  hw_out + 1.5, 1.5, 36.0, 56.0,   20.0)
    w_cock1  = make_section_wire(88.0,  hw_out,       1.5, 35.0, ROOF_Z, 18.5)
    w_cock2  = make_section_wire(118.0, hw_out,       1.5, 34.0, ROOF_Z, 18.0)
    w_hood   = make_section_wire(140.0, hw_out - 0.5, 2.0, 26.0, 38.0,   19.0)
    w_nose   = make_section_wire(165.0, hw_out - 4.0, 2.5, 14.0, 20.0,   15.0)
    outer_gt = Part.makeLoft([w_rear, w_eng, w_cock1, w_cock2, w_hood, w_nose], True)

    wi_rear  = make_section_wire(0.0,   hw_in,       -2.0, 32.0, 46.0,          19.0)
    wi_eng   = make_section_wire(45.0,  hw_in + 1.0, -2.0, 34.0, 54.0,          18.0)
    wi_cock1 = make_section_wire(88.0,  hw_in,       -2.0, 33.0, ROOF_Z - WALL, 16.5)
    wi_cock2 = make_section_wire(118.0, hw_in,       -2.0, 32.0, ROOF_Z - WALL, 16.0)
    wi_hood  = make_section_wire(140.0, hw_in - 0.5, -2.0, 24.0, 36.0,          17.0)
    wi_nose  = make_section_wire(162.5, hw_in - 4.0, -2.0, 12.0, 18.0,          13.0)
    inner_gt = Part.makeLoft([wi_rear, wi_eng, wi_cock1, wi_cock2, wi_hood, wi_nose], True)

    ferrari = outer_gt.cut(inner_gt)
    ferrari = apply_chassis_cuts_and_clips(ferrari)

    # Ferrari Cockpit Windshield Viewport (Aligned with ESP32-CAM at Y=115..138, Z=44..60)
    gt_windshield = Part.makeBox(26.0, 24.0, 16.0, App.Vector(-13.0, 116.0, 44.0))
    ferrari = ferrari.cut(gt_windshield)

    # Sculpted Side Door Air Scoops (Left & Right at Y = 58 to 88 mm, Z = 16 to 30 mm)
    scoop_l = Part.makeBox(5.0, 28.0, 12.0, App.Vector(-hw_out - 2.0, 58.0, 17.0))
    scoop_r = Part.makeBox(5.0, 28.0, 12.0, App.Vector(hw_out - 3.0, 58.0, 17.0))
    ferrari = ferrari.cut(scoop_l).cut(scoop_r)

    # Signature Ferrari F40 Fastback Engine Cover Louvers (Speaker Sound Vents at Y = 42..72)
    for sy in [44.0, 50.0, 56.0, 62.0, 68.0]:
        louver = Part.makeBox(28.0, 2.6, 14.0, App.Vector(-14.0, sy, 48.0))
        ferrari = ferrari.cut(louver)

    # High-Mounted Ferrari F40 Rear Wing & Side Endplates (Y = -2 to 14 mm)
    wing_l = Part.makeBox(2.5, 14.0, 16.0, App.Vector(-25.0, 0.0, 46.0))
    wing_r = Part.makeBox(2.5, 14.0, 16.0, App.Vector(22.5, 0.0, 46.0))
    blade = Part.makeBox(50.0, 14.0, 2.4, App.Vector(-25.0, 0.0, 59.5))
    blade.rotate(App.Vector(0, 7.0, 59.5), App.Vector(1, 0, 0), -7.0)
    ferrari = ferrari.fuse(wing_l).fuse(wing_r).fuse(blade)

    # Place Ferrari shell beside the Jeep shell at X = 95 mm
    ferrari.translate(App.Vector(95.0, 0, 0))
    obj_ferrari = doc.addObject("Part::Feature", "Ferrari_F40_Supercar_Shell")
    obj_ferrari.Shape = ferrari

build_jeep_shell()
build_ferrari_shell()

doc.recompute()
if App.GuiUp:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewAxonometric()
    Gui.SendMsgToActiveView("ViewFit")