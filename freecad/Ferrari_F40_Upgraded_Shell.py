import FreeCAD as App
import Part

doc = App.newDocument("Ferrari_F40_Upgraded_Shell")

# ==========================================
# CHASSIS INTERFACE & SHELL DIMENSIONS (mm)
# ==========================================
CHASSIS_W = 54.0            # Matches Main_Chassis_Base width
CLEARANCE = 0.4             # Slip-fit margin per side
WALL = 2.0                  # 2.0mm rugged PETG shell wall
INNER_W = CHASSIS_W + (CLEARANCE * 2.0)   # 54.8 mm inner cavity width
OUTER_W = INNER_W + (WALL * 2.0)          # 58.8 mm base body width

REAR_AXLE_Y = 26.0          # Matches Rear Gearbox axle center
FRONT_AXLE_Y = 141.0        # Matches Front C-Hub kingpin center
ROOF_Z = 65.0               # Clears ESP32-CAM (59.5mm) + air gap

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

def build_ferrari_f40_upgraded():
    hw_out = OUTER_W / 2.0
    hw_in = INNER_W / 2.0

    # ------------------------------------------
    # 1. MAIN LOFTED SUPERCAR BODY & CAVITY
    # ------------------------------------------
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

    # ------------------------------------------
    # 2. POP-UP HEADLIGHT PODS (FENDER MOUNTED)
    # ------------------------------------------
    pod_holes = []
    for side in [-1, 1]:
        px = (side * 18.0) - 4.5
        # Angled wedge housing rising out of the front hood
        pod_box = Part.makeBox(9.0, 13.0, 9.5, App.Vector(px, 146.0, 20.0))
        pod_bevel = Part.makeBox(10.0, 16.0, 8.0, App.Vector(px - 0.5, 145.0, 26.5))
        pod_bevel.rotate(App.Vector(px, 146.0, 26.5), App.Vector(1, 0, 0), -18.0)
        pod = pod_box.cut(pod_bevel)
        ferrari = ferrari.fuse(pod)

        # 5.2mm LED socket bored straight through the pop-up pod face
        led_pod_bore = Part.makeCylinder(
            2.6, 16.0,
            App.Vector(side * 18.0, 144.0, 23.5),
            App.Vector(0, 1, 0)
        )
        pod_holes.append(led_pod_bore)

    for hole in pod_holes:
        ferrari = ferrari.cut(hole)

    # Front nose aerodynamic chin splitter lip
    splitter = Part.makeBox(OUTER_W - 6.0, 8.0, 2.2, App.Vector(-(OUTER_W - 6.0) / 2.0, 158.5, 2.0))
    ferrari = ferrari.fuse(splitter)

    # ------------------------------------------
    # 3. DEEPER AERO SIDE SKIRTS & SNAP CLIPS
    # ------------------------------------------
    skirt_y0 = 47.0
    skirt_len = 71.0  # Spans between rear and front wheel arches
    for side in [-1, 1]:
        # Vertical aero rocker drop-down panel (reaches Z = -1.5 mm)
        sx = (hw_out - 1.5) if side == 1 else -(hw_out + 2.0)
        deep_skirt = Part.makeBox(3.5, skirt_len, 10.0, App.Vector(sx, skirt_y0, -1.5))

        # Outward ground-effect horizontal blade + rear shark-fin winglet
        blade_x = (hw_out - 0.5) if side == 1 else -(hw_out + 3.5)
        aero_blade = Part.makeBox(4.0, skirt_len, 2.2, App.Vector(blade_x, skirt_y0, -1.5))
        winglet_x = (hw_out + 1.8) if side == 1 else -(hw_out + 3.5)
        winglet = Part.makeBox(1.7, 12.0, 9.5, App.Vector(winglet_x, skirt_y0, -1.5))

        # Inward chassis snap-lip (hooks under the Z=0 chassis belly pan)
        clip_y0 = 62.0
        clip_len = 34.0
        lip_x = side * (hw_in - 1.8) - (1.8 if side == 1 else 0.0)
        snap_web = Part.makeBox(2.2, clip_len, 4.5, App.Vector(
            side * (hw_in - 0.5) - (2.2 if side == 1 else 0.0), clip_y0, -1.5
        ))
        snap_lip = Part.makeBox(1.8, clip_len, 1.5, App.Vector(lip_x, clip_y0, -1.5))

        ferrari = ferrari.fuse(deep_skirt).fuse(aero_blade).fuse(winglet).fuse(snap_web).fuse(snap_lip)

    # ------------------------------------------
    # 4. REAR UNDERBODY DIFFUSER & TRIPLE EXHAUST
    # ------------------------------------------
    # Diffuser outer shroud and upper deckplate at rear bumper (Y = -4.0 to 5.0 mm)
    diff_w = 44.0
    diff_shroud = Part.makeBox(diff_w, 8.0, 12.0, App.Vector(-diff_w / 2.0, -4.0, 2.0))
    diff_tunnel = Part.makeBox(diff_w - 4.0, 9.0, 9.5, App.Vector(-(diff_w - 4.0) / 2.0, -4.5, 1.5))
    diffuser = diff_shroud.cut(diff_tunnel)

    # 5x Vertical Aerodynamic Diffuser Strakes (Fins)
    for fx in [-15.0, -7.5, 0.0, 7.5, 15.0]:
        fin = Part.makeBox(1.8, 8.5, 10.0, App.Vector(fx - 0.9, -4.0, 2.0))
        diffuser = diffuser.fuse(fin)

    ferrari = ferrari.fuse(diffuser)

    # Signature F40 Central Triple Exhaust Tips (Centered at Z = 17.5 mm)
    for ex in [-5.5, 0.0, 5.5]:
        pipe_out = Part.makeCylinder(2.2, 5.5, App.Vector(ex, 1.0, 17.5), App.Vector(0, -1, 0))
        pipe_in  = Part.makeCylinder(1.4, 6.5, App.Vector(ex, 1.5, 17.5), App.Vector(0, -1, 0))
        ferrari = ferrari.fuse(pipe_out).cut(pipe_in)

    # ------------------------------------------
    # 5. WHEEL ARCHES, WINDOWS, VENTS & F40 WING
    # ------------------------------------------
    rear_arch = Part.makeCylinder(20.0, OUTER_W + 20.0, App.Vector(-OUTER_W/2 - 10.0, REAR_AXLE_Y, 8.0), App.Vector(1, 0, 0))
    front_arch = Part.makeCylinder(22.5, OUTER_W + 20.0, App.Vector(-OUTER_W/2 - 10.0, FRONT_AXLE_Y, 8.0), App.Vector(1, 0, 0))
    ferrari = ferrari.cut(rear_arch).cut(front_arch)

    # Lower Bumper Fog/Driving Light Ports (X = +/-16, Z = 8.5)
    led_l = Part.makeCylinder(3.5, 20.0, App.Vector(-16.0, 148.0, 8.5), App.Vector(0, 1, 0))
    led_r = Part.makeCylinder(3.5, 20.0, App.Vector(16.0, 148.0, 8.5), App.Vector(0, 1, 0))
    ferrari = ferrari.cut(led_l).cut(led_r)

    # Rear JQ6500 USB Access Slot (Above exhaust at Z = 26 to 38 mm)
    usb_slot = Part.makeBox(18.0, 10.0, 12.0, App.Vector(-9.0, -5.0, 26.0))
    ferrari = ferrari.cut(usb_slot)

    # Cockpit Windshield Viewport for ESP32-CAM & Side NACA Scoops
    gt_windshield = Part.makeBox(26.0, 24.0, 16.0, App.Vector(-13.0, 116.0, 44.0))
    scoop_l = Part.makeBox(5.0, 28.0, 12.0, App.Vector(-hw_out - 2.0, 58.0, 17.0))
    scoop_r = Part.makeBox(5.0, 28.0, 12.0, App.Vector(hw_out - 3.0, 58.0, 17.0))
    ferrari = ferrari.cut(gt_windshield).cut(scoop_l).cut(scoop_r)

    # Fastback Engine Cover Louvers (Speaker Sound Vents at Y = 44..68)
    for sy in [44.0, 50.0, 56.0, 62.0, 68.0]:
        louver = Part.makeBox(28.0, 2.6, 14.0, App.Vector(-14.0, sy, 48.0))
        ferrari = ferrari.cut(louver)

    # High-Mounted Ferrari F40 Rear Wing
    wing_l = Part.makeBox(2.5, 14.0, 16.0, App.Vector(-25.0, 0.0, 46.0))
    wing_r = Part.makeBox(2.5, 14.0, 16.0, App.Vector(22.5, 0.0, 46.0))
    blade = Part.makeBox(50.0, 14.0, 2.4, App.Vector(-25.0, 0.0, 59.5))
    blade.rotate(App.Vector(0, 7.0, 59.5), App.Vector(1, 0, 0), -7.0)
    ferrari = ferrari.fuse(wing_l).fuse(wing_r).fuse(blade)

    obj_ferrari = doc.addObject("Part::Feature", "Ferrari_F40_Competizione_Shell")
    obj_ferrari.Shape = ferrari

build_ferrari_f40_upgraded()
doc.recompute()

if App.GuiUp:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewAxonometric()
    Gui.SendMsgToActiveView("ViewFit")