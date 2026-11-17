# -*- coding: utf-8 -*-
# Ferrari Enzo FPV RC car  --  v2 (ground-up rebuild)   FreeCAD 1.x macro
# Scale ~1:22.4 (210 x 91 x 51.5 mm) so that 34 mm off-the-shelf N20 wheels are scale-correct.
# Axes: X = left/right, Y = rear(0) -> nose(210), Z = up (ground = 0).
import math, traceback
import FreeCAD as App
import Part
from FreeCAD import Vector as V

doc = App.newDocument("Enzo_FPV_v2")
PARTS = {}

# ---------------------------------------------------------------- parameters
L = 210.0
WALL = 2.4
AX_R, AX_F = 49.0, 167.0          # axle Y positions (wheelbase 118)
WR, WW, WZ = 17.0, 15.0, 17.0     # wheel radius, width, axle height (wheel touches Z=0)
W_IN = 29.5                       # wheel inner face |X| (outer face 44.5)
PLATE_Z0, PLATE_Z1 = 3.5, 5.5     # chassis plate
BATT_TOP = 25.0                   # top of 2S 18650 holder
DECK_Z0, DECK_Z1 = 25.0, 26.6
KP_X, KP_Y = 24.5, AX_F           # kingpin position
ARM_END = (22.26, 156.2)          # Ackermann arm end (points at rear axle centre)

# ---------------------------------------------------------------- helpers
def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))

def cyl(r, h, x, y, z, d=(0, 0, 1)):
    return Part.makeCylinder(r, h, V(x, y, z), V(*d))

def prism_yz(pts, x0, x1):
    vs = [V(x0, y, z) for y, z in pts]; vs.append(vs[0])
    return Part.Face(Part.makePolygon(vs)).extrude(V(x1 - x0, 0, 0))

def prism_xz(pts, y0, y1):
    vs = [V(x, y0, z) for x, z in pts]; vs.append(vs[0])
    return Part.Face(Part.makePolygon(vs)).extrude(V(0, y1 - y0, 0))

def bar(p1, p2, w, z0, h):
    d = p2 - p1
    b = Part.makeBox(math.hypot(d.x, d.y), w, h, V(0, -w / 2.0, 0))
    b.rotate(V(0, 0, 0), V(0, 0, 1), math.degrees(math.atan2(d.y, d.x)))
    b.translate(V(p1.x, p1.y, z0))
    return b

def fuse_all(shapes):
    s = shapes[0]
    for o in shapes[1:]:
        s = s.fuse(o)
    return s

def add(group, name, shape, color=(0.7, 0.7, 0.7), transp=0):
    s = shape.removeSplitter()
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = s
    group.addObject(obj)
    PARTS[name] = s
    if App.GuiUp:
        obj.ViewObject.ShapeColor = color
        obj.ViewObject.Transparency = transp
    return obj

g_body  = doc.addObject("App::Part", "01_Body")
g_glass = doc.addObject("App::Part", "02_Glass_And_Lights")
g_chas  = doc.addObject("App::Part", "03_Chassis")
g_steer = doc.addObject("App::Part", "04_Steering")
g_wheel = doc.addObject("App::Part", "05_Wheels_34mm")
g_drive = doc.addObject("App::Part", "06_Drivetrain_Ref")
g_elec  = doc.addObject("App::Part", "07_Electronics_Ref")
g_audio = doc.addObject("App::Part", "08_Audio")

def step(fn):
    try:
        fn()
        print("OK     :", fn.__name__)
    except Exception:
        print("FAILED :", fn.__name__)
        traceback.print_exc()

# ---------------------------------------------------------------- body
def make_body(ins):
    """Body solid. ins=0 -> outer skin, ins=WALL -> inner cavity (open at the bottom)."""
    k = ins * 1.25
    zb = 3.0 if ins == 0 else -1.0
    # side silhouette (Y,Z) - straight runs are on exact lines so glass/lens planes match
    top = [(0, 26), (12, 34), (36, 41), (62, 45), (84, 50.5), (100, 51.5), (112, 49.5),
           (126, 43.75), (140, 38), (152, 40.5), (168, 41), (184, 35), (191, 30.5),
           (198, 26), (210, 14)]
    pts = [(y, z - ins) for y, z in top]
    if ins:
        pts[0] = (ins, pts[0][1]); pts[-1] = (L - ins, pts[-1][1])
    sv = [V(-60, y, z) for y, z in pts]
    bs = Part.BSplineCurve(); bs.interpolate(sv)
    y0, yN = pts[0][0], pts[-1][0]
    e = [Part.makeLine(V(-60, y0, zb), sv[0]), bs.toShape(),
         Part.makeLine(sv[-1], V(-60, yN, zb)), Part.makeLine(V(-60, yN, zb), V(-60, y0, zb))]
    side = Part.Face(Part.Wire(e)).extrude(V(120, 0, 0))
    # plan view (half widths)
    R = [(38, 0), (44, 18), (45.5, 45), (42, 95), (43, 135), (45, 167), (41, 190), (26, 205), (14, 210)]
    R = [(x - ins, y) for x, y in R]
    R[0] = (R[0][0], ins); R[-1] = (R[-1][0], L - ins)
    rv = [V(x, y, -5) for x, y in R]
    lv = [V(-x, y, -5) for x, y in reversed(R)]
    b1 = Part.BSplineCurve(); b1.interpolate(rv)
    b2 = Part.BSplineCurve(); b2.interpolate(lv)
    e = [b1.toShape(), Part.makeLine(rv[-1], lv[0]), b2.toShape(), Part.makeLine(lv[-1], rv[0])]
    plan = Part.Face(Part.Wire(e)).extrude(V(0, 0, 80))
    body = side.common(plan)
    # cabin tumblehome (only between the rear haunch and the front fenders)
    for sg in (-1, 1):
        wedge = [(sg * (36 - k), 33), (sg * 60, 33), (sg * 60, 60), (sg * (17 - k), 60)]
        body = body.cut(prism_xz(wedge, 56 - ins, 140 + ins))
    # lowered centre hood between the higher front fenders
    hood = [(140, 38), (148, 36), (172, 32), (190, 27), (212, 19.5)]
    hp = [(y, z - ins) for y, z in hood] + [(212, 60), (140, 60)]
    body = body.cut(prism_yz(hp, -(20 + ins), (20 + ins)))
    return body

def expand(q, m):
    c = sum(q, V(0, 0, 0)) * (1.0 / len(q))
    out = []
    for p in q:
        d = p - c; d.normalize()
        out.append(p + d * m)
    return out

def slab(q, n, a, b):
    f = Part.Face(Part.makePolygon(q + [q[0]]))
    f.translate(n * a)
    return f.extrude(n * (b - a))

def pane(q, n):
    """opening (through the skin), recess (1 mm rebate), 0.5 mm PETG glass lying flat in the rebate"""
    opening = slab(q, n, -3.5, 3.5)
    recess = slab(expand(q, 2.0), n, -1.0, 3.5)
    glass = slab(expand(q, 1.7), n, -1.0, -0.5)
    return opening, recess, glass

def build_body():
    outer = make_body(0.0)
    cav = make_body(WALL)
    shell = outer.cut(cav)

    # wheel arches: round holes in the side walls sized for the 34 mm wheels
    for sg in (-1, 1):
        shell = shell.cut(cyl(19.5, 30, sg * 26, AX_R, WZ, (sg, 0, 0)))
        shell = shell.cut(cyl(21.0, 30, sg * 26, AX_F, WZ, (sg, 0, 0)))

    # windshield (planar, flush, in a rebate)
    n_ws = V(0, 0.4107, 1.0); n_ws.normalize()
    q = [V(-19, 112, 49.5), V(19, 112, 49.5), V(27.5, 140, 38.0), V(-27.5, 140, 38.0)]
    op, rc, gl = pane(q, n_ws)
    shell = shell.cut(op).cut(rc)
    add(g_glass, "Windshield_Glass", gl, (0.65, 0.88, 0.98), 60)

    # side windows lying in the 35 deg tumblehome wall (x = 36 - 19/27*(z-33))
    def xw(z): return 36.0 - (19.0 / 27.0) * (z - 33.0)
    for sg, nm in ((1, "Side_Glass_R"), (-1, "Side_Glass_L")):
        q = [V(sg * xw(38), 84, 38), V(sg * xw(45), 84, 45), V(sg * xw(45), 110, 45), V(sg * xw(38), 110, 38)]
        n = V(sg * 1.0, 0, 19.0 / 27.0); n.normalize()
        op, rc, gl = pane(q, n)
        shell = shell.cut(op).cut(rc)
        add(g_glass, nm, gl, (0.65, 0.88, 0.98), 60)

    # headlights: pocket + rebate + 0.5 mm lens flush with the 32.7 deg fender slope, 5 mm LED bore pointing +Y
    phi = math.degrees(math.atan2(9.0, 14.0))
    rot = App.Rotation(V(1, 0, 0), -phi)
    for sg, tag in ((1, "R"), (-1, "L")):
        cx = sg * 27.0
        def place(sh, cx=cx):
            sh.rotate(V(0, 0, 0), V(1, 0, 0), -phi)
            sh.translate(V(cx, 184.0, 35.0))
            return sh
        hw = 5.5
        shell = shell.cut(place(box(-(hw - 1.5), hw - 1.5, 0, 14, -4, 3)))
        shell = shell.cut(place(box(-hw, hw, 0, 14, -1.0, 3)))
        lens = place(box(-(hw - 0.3), hw - 0.3, 0.3, 13.7, -1.0, -0.5))
        add(g_glass, "Headlight_Lens_" + tag, lens, (0.95, 0.98, 1.0), 40)
        bucket = box(-(hw - 0.6), hw - 0.6, 0.5, 13.5, -7.0, -1.0)
        bucket = bucket.cut(box(-(hw - 1.8), hw - 1.8, 1.5, 12.5, -5.2, -1.0))
        bucket = place(bucket)
        gp = rot.multVec(V(0, 6, -4.2)) + V(cx, 184.0, 35.0)
        bucket = bucket.cut(cyl(2.6, 18, cx, gp.y - 8, gp.z, (0, 1, 0)))
        add(g_glass, "Headlight_Bucket_" + tag, bucket, (0.1, 0.1, 0.12))

    # nose camera window (OV2640 on a long flex cable sits behind it)
    shell = shell.cut(cyl(3.75, 8, 0, 206, 9.05, (0, 1, 0)))
    # tail: LED bores + exhaust bores
    for sg in (-1, 1):
        shell = shell.cut(cyl(1.6, 6, sg * 28, -1, 19, (0, 1, 0)))
        for xo in (9.0, 15.0):
            shell = shell.cut(cyl(1.6, 5, sg * xo, -1, 12, (0, 1, 0)))
    # engine-cover louvers over the speaker
    for sy in (24.0, 29.0, 34.0, 39.0, 44.0):
        shell = shell.cut(box(-14, 14, sy, sy + 2.6, 30, 60))
    # body screw bosses (M2 from below through the chassis wings)
    for sg in (-1, 1):
        for yc in (84.0, 128.0):
            xa, xb = sorted((sg * 31.0, sg * 41.5))
            boss = box(xa, xb, yc - 5, yc + 5, 5.5, 12.0)
            shell = shell.fuse(boss)
            shell = shell.cut(cyl(0.9, 6, sg * 34.5, yc, 5.5))
    add(g_body, "Body_Shell", shell, (0.85, 0.08, 0.08))

    ex = None
    for sg in (-1, 1):
        for xo in (9.0, 15.0):
            t = cyl(2.4, 6, sg * xo, 3.0, 12, (0, -1, 0)).cut(cyl(1.6, 8, sg * xo, 4.0, 12, (0, -1, 0)))
            ex = t if ex is None else ex.fuse(t)
    add(g_body, "Exhaust_Tips", ex, (0.35, 0.35, 0.38))

# ---------------------------------------------------------------- chassis
def build_chassis():
    parts = [box(-26, 26, 40, 150, PLATE_Z0, PLATE_Z1),
             box(-22, 22, 14, 40, PLATE_Z0, PLATE_Z1),
             box(-21, 21, 150, 205, PLATE_Z0, PLATE_Z1)]
    for y0, y1 in ((79, 89), (123, 133)):
        parts.append(box(-36, 36, y0, y1, PLATE_Z0, PLATE_Z1))
    ch = fuse_all(parts)
    for sg in (-1, 1):
        for y in (66.0, 130.0):
            ch = ch.fuse(cyl(2.8, BATT_TOP - PLATE_Z1, sg * 23.0, y, PLATE_Z1))
        ch = ch.fuse(cyl(2.5, 23.6 - PLATE_Z1, sg * 17.0, 24.0, PLATE_Z1))
        # rear N20 motor tunnels (one motor per rear wheel, transverse, shaft straight into the wheel)
        xa, xb = sorted((sg * 1.5, sg * 26.5))
        blk = box(xa, xb, 41, 57, PLATE_Z1, 23.6)
        xa2, xb2 = sorted((sg * 1.0, sg * 27.0))
        blk = blk.cut(box(xa2, xb2, AX_R - 6.2, AX_R + 6.2, WZ - 5.2, WZ + 5.2))
        ch = ch.fuse(blk)
        # front fork: two pillars + upper bridge, kingpin hangs from the bridge
        xa, xb = sorted((sg * 16.0, sg * 19.0))
        ch = ch.fuse(box(xa, xb, 162, 172, PLATE_Z1, 27.8))
    br = box(-26.5, 26.5, 162, 172, 27.8, 30.3)
    for sg in (-1, 1):
        br = br.cut(cyl(1.1, 5, sg * KP_X, KP_Y, 27.0))
    ch = ch.fuse(br)
    # servo cradle
    cr = box(-12.9, 12.9, 137.6, 152.9, PLATE_Z1, 18.0).cut(box(-11.4, 11.4, 139.0, 151.5, PLATE_Z1, 30))
    ch = ch.fuse(cr)
    # nose camera cradle (open on top and front)
    cc = box(-6.5, 6.5, 197, 205, PLATE_Z0, 16.0).cut(box(-4.4, 4.4, 196, 205.5, 4.7, 17))
    ch = ch.fuse(cc)
    # body-screw holes
    for sg in (-1, 1):
        for yc in (84.0, 128.0):
            ch = ch.cut(cyl(1.1, 4, sg * 34.5, yc, 3.0))
    add(g_chas, "Chassis", ch, (0.25, 0.25, 0.3))

# ---------------------------------------------------------------- steering
def build_steering():
    for sg, tag in ((1, "R"), (-1, "L")):
        xa, xb = sorted((sg * (KP_X - 2.5), sg * (KP_X + 2.5)))
        kn = box(xa, xb, 162, 172, 11, 25)
        kn = kn.fuse(cyl(1.5, 12.5, sg * (KP_X + 2.5), KP_Y, WZ, (sg, 0, 0)))
        kn = kn.fuse(bar(V(sg * KP_X, KP_Y, 0), V(sg * ARM_END[0], ARM_END[1], 0), 4.0, 25.0, 2.5))
        kn = kn.cut(cyl(1.1, 20, sg * KP_X, KP_Y, 9.0))
        kn = kn.cut(cyl(1.1, 6, sg * ARM_END[0], ARM_END[1], 23.0))
        add(g_steer, "Knuckle_" + tag, kn, (0.2, 0.5, 0.8))
    rod = bar(V(-ARM_END[0], ARM_END[1], 0), V(ARM_END[0], ARM_END[1], 0), 3.0, 22.2, 2.6)
    for sg in (-1, 1):
        rod = rod.fuse(cyl(1.0, 5.3, sg * ARM_END[0], ARM_END[1], 22.2))
    add(g_steer, "Tie_Rod", rod, (0.2, 0.5, 0.8))

# ---------------------------------------------------------------- wheels, drivetrain
def build_wheels():
    for nm, y in (("Rear", AX_R), ("Front", AX_F)):
        for sg, s in ((-1, "L"), (1, "R")):
            base = V(sg * W_IN, y, WZ); d = V(sg, 0, 0)
            tyre = Part.makeCylinder(WR, WW, base, d).cut(Part.makeCylinder(11.0, WW, base, d))
            hub = Part.makeCylinder(11.0, WW, base, d).cut(Part.makeCylinder(1.5, WW, base, d))
            add(g_wheel, "Tyre_%s_%s" % (nm, s), tyre, (0.1, 0.1, 0.11))
            add(g_wheel, "Hub_%s_%s" % (nm, s), hub, (0.85, 0.72, 0.1))

def build_drivetrain_ref():
    for sg, s in ((-1, "L"), (1, "R")):
        xa, xb = sorted((sg * 1.5, sg * 26.5))
        m = box(xa, xb, AX_R - 6.075, AX_R + 6.075, WZ - 5.075, WZ + 5.075)
        m = m.fuse(cyl(1.5, 13.0, sg * 26.5, AX_R, WZ, (sg, 0, 0)))
        add(g_drive, "N20_Motor_" + s, m, (0.6, 0.6, 0.65))
    sv = box(-11.25, 11.25, 139.0, 151.2, PLATE_Z1, 28.2)
    horn = bar(V(5.25, 145.0, 0), V(5.25, ARM_END[1], 0), 4.0, 28.6, 1.6)
    horn = horn.fuse(cyl(1.0, 4.0, 5.25, ARM_END[1], 24.8))
    add(g_drive, "Servo_SG92R_Ref", sv, (0.15, 0.15, 0.7), 20)
    add(g_drive, "Servo_Horn_Ref", horn, (0.9, 0.9, 0.9))

# ---------------------------------------------------------------- electronics + audio
def build_electronics_ref():
    add(g_elec, "Battery_2S18650_Ref", box(-20, 20, 63, 131, PLATE_Z1, BATT_TOP), (0.2, 0.4, 0.8), 40)
    deck = box(-26, 26, 62, 137, DECK_Z0, DECK_Z1)
    for sx in (-13.5, 13.5):
        for sy in (70.5, 111.5):
            deck = deck.fuse(cyl(2.0, 2.0, sx, sy, DECK_Z1))
    add(g_elec, "Electronics_Deck", deck, (0.1, 0.45, 0.25))
    add(g_elec, "Carrier_PCB_46x32", box(-16, 16, 68, 114, 28.6, 30.2), (0.05, 0.35, 0.15), 20)
    add(g_elec, "ESP32CAM_Board_Ref", box(-13.5, 13.5, 72, 112.5, 38.7, 43.7), (0.1, 0.1, 0.1), 30)
    add(g_elec, "MH_M18_Ref", box(2, 24, 117, 131, DECK_Z1, 31), (0.5, 0.2, 0.2), 30)
    add(g_elec, "JQ6500_Ref", box(-25, -1, 117, 131, DECK_Z1, 31), (0.5, 0.2, 0.2), 30)
    cam = box(-4.25, 4.25, 197, 205, 4.8, 13.3).fuse(cyl(3.2, 2.0, 0, 205, 9.05, (0, 1, 0)))
    add(g_elec, "OV2640_Camera_Ref", cam, (0.1, 0.1, 0.1))

def build_audio():
    enc = box(-22, 22, 19, 61, 23.6, 32.6)
    enc = enc.cut(box(-20, 20, 21, 59, 25.6, 30.6))          # interior 40 x 38 x 5
    enc = enc.cut(cyl(16.0, 4, 0, 40, 30.0))                  # sound hole in the 2 mm lid
    add(g_audio, "Speaker_Box_36mm", enc, (0.2, 0.22, 0.25))
    spk = cyl(18.1, 4.6, 0, 40, 25.7)
    add(g_audio, "Speaker_36mm_Ref", spk, (0.6, 0.6, 0.6), 30)

# ---------------------------------------------------------------- interference report
def report():
    pairs = []
    wheels = [n for n in PARTS if n.startswith("Tyre_") or n.startswith("Hub_")]
    for w in wheels:
        for o in ("Body_Shell", "Chassis", "Knuckle_L", "Knuckle_R", "Tie_Rod"):
            pairs.append((w, o))
    for o in ("Chassis", "Speaker_Box_36mm", "Electronics_Deck", "ESP32CAM_Board_Ref", "MH_M18_Ref",
              "JQ6500_Ref", "Servo_SG92R_Ref", "Servo_Horn_Ref", "OV2640_Camera_Ref", "Battery_2S18650_Ref",
              "Knuckle_L", "Knuckle_R", "Tie_Rod", "Headlight_Bucket_L", "Headlight_Bucket_R"):
        pairs.append(("Body_Shell", o))
    pairs += [("Speaker_Box_36mm", "Chassis"), ("Battery_2S18650_Ref", "Electronics_Deck"),
              ("Knuckle_L", "Chassis"), ("Knuckle_R", "Chassis"), ("Tie_Rod", "Servo_SG92R_Ref"),
              ("Servo_Horn_Ref", "Chassis"), ("N20_Motor_L", "Chassis"), ("N20_Motor_R", "Chassis")]
    print("=== INTERFERENCE REPORT (mm^3, 0 = clean) ===")
    bad = 0
    for a, b in pairs:
        if a not in PARTS or b not in PARTS:
            continue
        try:
            v = PARTS[a].common(PARTS[b]).Volume
        except Exception:
            print("  ?  %-22s x %-22s (boolean failed)" % (a, b)); continue
        if v > 0.5:
            bad += 1
            print("  !! %-22s x %-22s %.1f" % (a, b, v))
    print("=== %d overlapping pairs ===" % bad)

for f in (build_body, build_chassis, build_steering, build_wheels,
          build_drivetrain_ref, build_electronics_ref, build_audio):
    step(f)

doc.recompute()
step(report)
if App.GuiUp:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
