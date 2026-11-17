#!/usr/bin/env python3
"""
body_shell.py — FreeCAD Python Macro
Supercar: Snap-On Aerodynamic Outer Car Body Shell
Precision-matched to Complete_FPV_RC_Chassis_500g_v2 coordinates.
Run: FreeCAD -> Macro -> Macros... -> Create -> paste -> Execute (Ctrl+F6)
"""

import FreeCAD as App
import Part

doc = App.newDocument("FPV_RC_Aerodynamic_Shell")

# ==========================================
# MATCHED CHASSIS & SHELL PARAMETERS (mm)
# ==========================================
CHASSIS_W  = 54.0            # Matches main chassis belly pan width
CHASSIS_L  = 160.0           # Full length from rear gearbox to front bumper
SHELL_T    = 2.0             # 2.0 mm rugged outer wall thickness (PETG/ABS)
CLEARANCE  = 0.4             # Slip-fit clearance around chassis rails

INNER_W = CHASSIS_W + (CLEARANCE * 2.0)   # 54.8 mm interior width
OUTER_W = INNER_W + (SHELL_T * 2.0)       # 58.8 mm outer body width
ROOF_Z  = 65.0                            # Clears top of ESP32-CAM (59.5 mm) + 3.5 mm air gap

# Axle Y-Coordinates (Matched to Complete_FPV_RC_Chassis_500g_v2)
REAR_AXLE_Y   = 27.0
FRONT_AXLE_Y  = 142.0

def make_profile_wire(y_pos, half_w, z_bot, z_belt, z_top, roof_half_w):
    """Cross-section wire in X-Z plane at given Y position."""
    pts = [
        App.Vector(-half_w, y_pos, z_bot),
        App.Vector(-half_w, y_pos, z_belt),
        App.Vector(-roof_half_w, y_pos, z_top),
        App.Vector( roof_half_w, y_pos, z_top),
        App.Vector( half_w, y_pos, z_belt),
        App.Vector( half_w, y_pos, z_bot),
        App.Vector(-half_w, y_pos, z_bot)
    ]
    poly = Part.makePolygon(pts)
    return Part.Wire(poly.Edges)

def build_aerodynamic_shell():
    # ------------------------------------------
    # 1. LOFTED OUTER AERODYNAMIC PROFILE
    # ------------------------------------------
    hw_out = OUTER_W / 2.0

    # Define 5 aerodynamic stations from Rear Tail (Y=-2) to Front Nose (Y=163)
    w_rear   = make_profile_wire(-2.0,  hw_out - 1.5, 4.0, 34.0, 56.0, 19.0)
    w_cabin1 = make_profile_wire( 35.0, hw_out,       1.5, 38.0, ROOF_Z, 21.0)
    w_cabin2 = make_profile_wire(105.0, hw_out,       1.5, 38.0, ROOF_Z, 21.0)
    w_hood   = make_profile_wire(136.0, hw_out - 1.0, 2.0, 30.0, 56.0, 19.5)
    w_nose   = make_profile_wire(163.0, hw_out - 4.0, 3.0, 16.0, 24.0, 16.0)

    outer_solid = Part.makeLoft([w_rear, w_cabin1, w_cabin2, w_hood, w_nose], True)

    # ------------------------------------------
    # 2. HOLLOW INTERIOR CAVITY (2.0 mm WALLS)
    # ------------------------------------------
    hw_in = INNER_W / 2.0
    wi_rear   = make_profile_wire( 0.0,   hw_in - 1.5, -2.0, 32.0, 54.0, 17.0)
    wi_cabin1 = make_profile_wire( 35.0, hw_in,       -2.0, 36.0, ROOF_Z - SHELL_T, 19.0)
    wi_cabin2 = make_profile_wire(105.0, hw_in,       -2.0, 36.0, ROOF_Z - SHELL_T, 19.0)
    wi_hood   = make_profile_wire(136.0, hw_in - 1.0, -2.0, 28.0, 54.0, 17.5)
    wi_nose   = make_profile_wire(160.5, hw_in - 4.0, -2.0, 14.0, 22.0, 14.0)

    inner_cavity = Part.makeLoft([wi_rear, wi_cabin1, wi_cabin2, wi_hood, wi_nose], True)
    shell = outer_solid.cut(inner_cavity)

    # ------------------------------------------
    # 3. WHEEL ARCH CUTOUTS (FULL STEERING LOCK)
    # ------------------------------------------
    # Rear wheel arch (Radius 20 mm centered at Y=27, Z=8)
    rear_arch = Part.makeCylinder(
        20.0, OUTER_W + 10.0,
        App.Vector(-OUTER_W / 2.0 - 5.0, REAR_AXLE_Y, 8.0),
        App.Vector(1, 0, 0)
    )
    # Front wheel arch (Wider 22.5 mm radius so front tires turn +/-40 deg cleanly)
    front_arch = Part.makeCylinder(
        22.5, OUTER_W + 10.0,
        App.Vector(-OUTER_W / 2.0 - 5.0, FRONT_AXLE_Y, 8.0),
        App.Vector(1, 0, 0)
    )
    shell = shell.cut(rear_arch).cut(front_arch)

    # ------------------------------------------
    # 4. FPV CAMERA WINDSHIELD VIEWPORT & LED PORTS
    # ------------------------------------------
    # Wide-angle windshield viewport aligned with ESP32-CAM lens (Z ~ 54 mm, Y ~ 134 mm)
    cam_window = Part.makeBox(22.0, 18.0, 14.0, App.Vector(-11.0, 125.0, 46.0))
    shell = shell.cut(cam_window)

    # Lower bumper headlight openings aligned with chassis LED pods
    led_cut_l = Part.makeCylinder(3.4, 15.0, App.Vector(-16.0, 153.0, 8.5), App.Vector(0, 1, 0))
    led_cut_r = Part.makeCylinder(3.4, 15.0, App.Vector( 16.0, 153.0, 8.5), App.Vector(0, 1, 0))
    shell = shell.cut(led_cut_l).cut(led_cut_r)

    # ------------------------------------------
    # 5. SPEAKER ACOUSTIC VENTS & ANTENNA SLOT
    # ------------------------------------------
    # 5x Roof louver slots directly above 36 mm speaker (Y = 50 to 70 mm)
    for sy in [51.0, 55.5, 60.0, 64.5, 69.0]:
        vent = Part.makeBox(26.0, 2.2, 8.0, App.Vector(-13.0, sy, ROOF_Z - 4.0))
        shell = shell.cut(vent)

    # Rear DFPlayer MicroSD access cutout at tail (Y = -2 to 3 mm, Z = 26 to 36 mm)
    sd_access = Part.makeBox(18.0, 8.0, 10.0, App.Vector(-9.0, -4.0, 26.0))
    shell = shell.cut(sd_access)

    # ------------------------------------------
    # 6. SNAP-ON ROCKER RETENTION CLIPS (LEFT & RIGHT)
    # ------------------------------------------
    # Clips snap under the 3.0 mm chassis belly pan edge between wheel arches (Y = 62 to 98 mm)
    for side in [-1, 1]:
        clip_len = 34.0
        clip_y0  = 63.0
        # Vertical inner skirt extension reaching Z = -1.5 mm
        skirt_x  = side * (INNER_W / 2.0 - 0.8) - (0.8 if side == 1 else 0.0)
        skirt = Part.makeBox(0.8, clip_len, 4.0, App.Vector(skirt_x, clip_y0, -1.5))

        # Inward bevel snap lip at Z = -1.5 to 0.0 mm that hooks under chassis floor (Z = 0)
        lip_x  = side * (INNER_W / 2.0 - 1.8) - (1.8 if side == 1 else 0.0)
        lip = Part.makeBox(1.8, clip_len, 1.5, App.Vector(lip_x, clip_y0, -1.5))
        shell = shell.fuse(skirt).fuse(lip)

    # ------------------------------------------
    # 7. AERODYNAMIC REAR SPOILER WING
    # ------------------------------------------
    strut_l = Part.makeBox(2.5, 10.0, 9.0, App.Vector(-15.0,  2.0, 54.0))
    strut_r = Part.makeBox(2.5, 10.0, 9.0, App.Vector( 12.5,  2.0, 54.0))
    wing    = Part.makeBox(52.0, 13.0, 2.2, App.Vector(-26.0, -1.0, 62.0))
    wing.rotate(App.Vector(0, 5.0, 62.0), App.Vector(1, 0, 0), -8.0)   # 8-degree downforce angle

    endplate_l = Part.makeBox(1.8, 15.0, 8.0, App.Vector(-26.5, -2.0, 59.0))
    endplate_r = Part.makeBox(1.8, 15.0, 8.0, App.Vector( 24.7, -2.0, 59.0))

    shell = shell.fuse(strut_l).fuse(strut_r).fuse(wing).fuse(endplate_l).fuse(endplate_r)

    obj_shell = doc.addObject("Part::Feature", "Aerodynamic_Car_Body_Shell")
    obj_shell.Shape = shell

build_aerodynamic_shell()
doc.recompute()
if App.GuiUp:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewAxonometric()
    Gui.SendMsgToActiveView("ViewFit")

print("body_shell.py: Aerodynamic_Car_Body_Shell generated")
print("  Print upside-down on roof; PETG, 0.2 mm layer, 3 walls, 20% infill")
print("  Tree supports only under rear spoiler wing")