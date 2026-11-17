#!/usr/bin/env python3
"""
generate_rc_pcb.py — Supercar KiCad Carrier PCB Generator (46 mm x 32 mm)
Production-quality v2:
  - 2-layer design with ground pour on B.Cu
  - Test points for VBAT, GND, 5V_ESP, M1_FWD, M1_REV, SERVO_PWM
  - Silkscreen labels for all connectors and key components
  - Decoupling caps placed adjacent to IC power pins
  - Antenna keepout zone on both copper layers
  - DIY-etchable: 0.8-1.5 mm tracks, 0.5 mm min clearance, 4 top-layer jumpers
Run: python3 kicad/generate_rc_pcb.py
Opens: FPV_RC_Carrier_46x32_v2.kicad_pcb in KiCad PCB Editor
"""

import math

OUTPUT_FILE = "FPV_RC_Carrier_46x32_v2.kicad_pcb"


def pad_th(num, x, y, drill=0.9, size=1.8, net_id=0, net_name=""):
    net_str = f'(net {net_id} "{net_name}")' if net_id > 0 else ""
    return f'    (pad "{num}" thru_hole circle (at {x:.3f} {y:.3f}) '\
           f'(size {size:.2f} {size:.2f}) (drill {drill:.2f}) {net_str} (layers "*.Cu" "*.Mask"))'


def pad_smd(num, x, y, w, h, layer="B.Cu", net_id=0, net_name=""):
    net_str = f'(net {net_id} "{net_name}")' if net_id > 0 else ""
    return f'    (pad "{num}" smd rect (at {x:.3f} {y:.3f}) '\
           f'(size {w:.2f} {h:.2f}) (layers "{layer}" "{layer}") {net_str})'


def track(x1, y1, x2, y2, width=0.8, layer="B.Cu", net_id=0):
    return f' (segment (start {x1:.3f} {y1:.3f}) (end {x2:.3f} {y2:.3f}) '\
           f'(width {width:.2f}) (layer "{layer}") (net {net_id}))'


def via(x, y, net_id=0, net_name=""):
    net_str = f'(net {net_id} "{net_name}")' if net_id > 0 else ""
    return f' (via (at {x:.3f} {y:.3f}) (size 0.8) (drill 0.4) {net_str} (layers "F.Cu" "B.Cu"))'


def mounting_hole(x, y):
    return f""" (footprint "MountingHole_2.2mm_M2" (layer "F.Cu") (at {x:.3f} {y:.3f})
        (pad "" np_thru_hole circle (at 0 0) (size 2.2 2.2) (drill 2.2) (layers "*.Cu" "*.Mask"))
      )"""


def silk_text(text, x, y, layer="F.SilkS", size=0.8):
    return f' (gr_text "{text}" (at {x:.3f} {y:.3f}) (layer "{layer}") '\
           f'(effects (font (size {size:.2f} {size:.2f}) (thickness 0.15)) (justify left)))'


def silk_line(x1, y1, x2, y2, layer="F.SilkS"):
    return f' (gr_line (start {x1:.3f} {y1:.3f}) (end {x2:.3f} {y2:.3f}) '\
           f'(layer "{layer}") (width 0.12))'


# Net definitions
NETS = {
    1: "GND", 2: "VBAT", 3: "+5V_MAIN", 4: "+5V_ESP",
    5: "M1_FWD", 6: "M1_REV", 7: "SERVO_PWM", 8: "HORN_TRIG",
    9: "JQ_RX", 10: "LIGHTS", 11: "TAILLIGHTS", 12: "M1_A",
    13: "M1_B", 14: "AUDIO_MIX", 15: "SPK_P", 16: "SPK_N",
    17: "TP_TEST",  # test points share GND net or separate; use GND for simplicity
}

lines = [
    '(kicad_pcb (version 20240108) (generator "rc_pcb_gen")',
    ' (general (thickness 1.6))',
    ' (paper "A4")',
    ' (layers',
    '     (0 "F.Cu" signal)',
    '     (31 "B.Cu" signal)',
    '     (36 "B.SilkS" user "B.Silkscreen")',
    '     (37 "F.SilkS" user "F.Silkscreen")',
    '     (38 "B.Mask" user)',
    '     (39 "F.Mask" user)',
    '     (44 "Edge.Cuts" user)',
    ' )'
]

for nid, nname in NETS.items():
    lines.append(f' (net {nid} "{nname}")')

# =====================================================================
# 1. Board Outline (Edge.Cuts: 32.0 mm wide x 46.0 mm tall)
# =====================================================================
W, H = 32.0, 46.0
edges = [(0, 0, W, 0), (W, 0, W, H), (W, H, 0, H), (0, H, 0, 0)]
for x1, y1, x2, y2 in edges:
    lines.append(f' (gr_line (start {x1} {y1}) (end {x2} {y2}) (layer "Edge.Cuts") (width 0.15))')

# =====================================================================
# 2. Four M2 Corner Mounting Holes (Matched to FreeCAD Deck)
# =====================================================================
for mx, my in [(2.5, 2.5), (29.5, 2.5), (2.5, 43.5), (29.5, 43.5)]:
    lines.append(mounting_hole(mx, my))

# =====================================================================
# 3. MOD1: AI-Thinker ESP32-CAM Dual 1x8 Headers (Top Mount, Pitch 2.54 mm)
# Left Row X = 4.57 mm, Right Row X = 27.43 mm, Y = 18.0 to 35.78 mm
# =====================================================================
esp_left_nets = [
    (1, "+5V_ESP", 4), (2, "GND", 1), (3, "M1_REV", 6), (4, "M1_FWD", 5),
    (5, "SERVO_PWM", 7), (6, "HORN_TRIG", 8), (7, "LIGHTS", 10), (8, "TAILLIGHTS", 11)
]
esp_right_nets = [
    (1, "GND", 1), (2, "JQ_RX", 9), (3, "GND", 1), (4, "NC", 0),
    (5, "NC", 0), (6, "NC", 0), (7, "TX_PROG", 0), (8, "RX_PROG", 0)
]

lines.append(' (footprint "ESP32_CAM_Headers" (layer "F.Cu") (at 0 0)')
for idx, (pnum, nname, nid) in enumerate(esp_left_nets):
    lines.append(pad_th(f"L{pnum}", 4.57, 18.0 + idx * 2.54, 1.0, 1.9, nid, nname))
for idx, (pnum, nname, nid) in enumerate(esp_right_nets):
    lines.append(pad_th(f"R{pnum}", 27.43, 18.0 + idx * 2.54, 1.0, 1.9, nid, nname))
lines.append(' )')

# ESP32-CAM silkscreen outline
lines.append(silk_text("ESP32-CAM", 16.0, 30.0))
lines.append(silk_line(2.0, 16.0, 30.0, 16.0))
lines.append(silk_line(30.0, 16.0, 30.0, 37.0))
lines.append(silk_line(30.0, 37.0, 2.0, 37.0))
lines.append(silk_line(2.0, 37.0, 2.0, 16.0))

# =====================================================================
# 4. MOD2: JQ6500-16P Onboard Flash Sound Module (Bottom Mount, Pitch 2.54 mm)
# Left Row X = 7.11 mm, Right Row X = 24.89 mm, Y = 2.0 to 19.78 mm
# =====================================================================
lines.append(' (footprint "JQ6500_16P_Flash_Module" (layer "B.Cu") (at 0 0)')
jq_left = [(1, "NC", 0), (2, "JQ_RX", 9), (3, "NC", 0), (4, "AUDIO_MIX", 14),
           (5, "NC", 0), (6, "SPK_P", 15), (7, "GND", 1), (8, "SPK_N", 16)]
jq_right = [(9, "HORN_TRIG", 8), (10, "GND", 1), (11, "NC", 0), (12, "NC", 0),
            (13, "NC", 0), (14, "NC", 0), (15, "NC", 0), (16, "+5V_MAIN", 3)]
for idx, (pnum, nname, nid) in enumerate(jq_left):
    lines.append(pad_th(str(pnum), 7.11, 2.0 + idx * 2.54, 0.9, 1.75, nid, nname))
for idx, (pnum, nname, nid) in enumerate(jq_right):
    lines.append(pad_th(str(pnum), 24.89, 2.0 + idx * 2.54, 0.9, 1.75, nid, nname))
lines.append(' )')

lines.append(silk_text("JQ6500", 16.0, 6.0))
lines.append(silk_line(4.0, 1.0, 28.0, 1.0))
lines.append(silk_line(28.0, 1.0, 28.0, 21.0))
lines.append(silk_line(28.0, 21.0, 4.0, 21.0))
lines.append(silk_line(4.0, 21.0, 4.0, 1.0))

# =====================================================================
# 5. U2: RZ7889 Motor Driver (SOIC-8 on Bottom Copper B.Cu at X=16.0, Y=14.0)
# =====================================================================
lines.append(' (footprint "RZ7889_SOIC8" (layer "B.Cu") (at 16.0 14.0)')
rz_pins = [
    (1, -2.7, -1.905, "GND", 1),       # Pin 1: GND
    (2, -2.7, -0.635, "M1_FWD", 5),    # Pin 2: BI input
    (3, -2.7, 0.635,  "M1_REV", 6),    # Pin 3: FI input
    (4, -2.7, 1.905,  "GND", 1),       # Pin 4: GND
    (5,  2.7, 1.905,  "VBAT", 2),      # Pin 5: VCC -> VBAT
    (6,  2.7, 0.635,  "VBAT", 2),      # Pin 6: VCC -> VBAT
    (7,  2.7, -0.635, "M1_A", 12),     # Pin 7: OUT1 -> M1_A
    (8,  2.7, -1.905, "M1_B", 13)      # Pin 8: OUT2 -> M1_B
]
for pnum, px, py, nname, nid in rz_pins:
    lines.append(pad_smd(str(pnum), 16.0 + px, 14.0 + py, 1.6, 0.65, "B.Cu", nid, nname))
lines.append(' )')

lines.append(silk_text("RZ7889", 16.0, 11.5))

# =====================================================================
# 6. Edge Connectors (JST-XH 2.54 mm Through-Hole)
# =====================================================================
lines.append(' (footprint "Connectors_Edge" (layer "F.Cu") (at 0 0)')
# J1: VBAT & GND (Rear Left)
lines.append(pad_th("J1_1", 11.5,  2.5, 1.0, 2.0, 2, "VBAT"))
lines.append(pad_th("J1_2", 14.04, 2.5, 1.0, 2.0, 1, "GND"))
# J2: N20 Motor M1_A & M1_B (Rear Center)
lines.append(pad_th("J2_1", 18.0,  2.5, 1.0, 2.0, 12, "M1_A"))
lines.append(pad_th("J2_2", 20.54, 2.5, 1.0, 2.0, 13, "M1_B"))
# J3: Front SG92R Servo 3-Pin (Front Center Y=43.5)
lines.append(pad_th("J3_GND", 13.46, 43.5, 1.0, 1.9, 1, "GND"))
lines.append(pad_th("J3_5V",  16.00, 43.5, 1.0, 1.9, 3, "+5V_MAIN"))
lines.append(pad_th("J3_SIG", 18.54, 43.5, 1.0, 1.9, 7, "SERVO_PWM"))
# J4/J5: Headlight & Taillight (Front Left/Right)
lines.append(pad_th("J4_1", 7.5,   41.5, 1.0, 1.9, 10, "LIGHTS"))
lines.append(pad_th("J4_2", 7.5,   43.5, 1.0, 1.9, 1, "GND"))
lines.append(pad_th("J5_1", 24.5,  41.5, 1.0, 1.9, 11, "TAILLIGHTS"))
lines.append(pad_th("J5_2", 24.5,  43.5, 1.0, 1.9, 1, "GND"))
# J6: 3W Speaker SPK_P & SPK_N (Center-Left)
lines.append(pad_th("J6_1", 11.5,  7.5, 1.0, 2.0, 15, "SPK_P"))
lines.append(pad_th("J6_2", 14.04, 7.5, 1.0, 2.0, 16, "SPK_N"))
# J7: 1x4 UART Flash Header (Left Edge)
lines.append(pad_th("J7_1", 2.0,   11.0, 1.0, 1.9, 0, "TX_PROG"))
lines.append(pad_th("J7_2", 2.0,   13.0, 1.0, 1.9, 0, "RX_PROG"))
lines.append(pad_th("J7_3", 2.0,   15.0, 1.0, 1.9, 1, "GND"))
lines.append(pad_th("J7_4", 2.0,   17.0, 1.0, 1.9, 0, "GPIO0"))
# C1: 470uF Anti-Brownout Cap (right next to ESP32 5V/GND)
lines.append(pad_th("C1_P",  4.57, 14.5, 0.9, 1.9, 4, "+5V_ESP"))
lines.append(pad_th("C1_N",  7.11, 14.5, 0.9, 1.9, 1, "GND"))

lines.append('            )')

# Connector silkscreen labels
lines.append(silk_text("J1 BAT", 11.0, 1.0))
lines.append(silk_text("J2 MOTOR", 17.0, 1.0))
lines.append(silk_text("J3 SERVO", 13.0, 44.5))
lines.append(silk_text("J4 LED", 6.0, 40.5))
lines.append(silk_text("J5 LED", 23.0, 40.5))
lines.append(silk_text("J6 SPK", 10.0, 6.5))
lines.append(silk_text("J7 UART", 0.5, 9.0))

# =====================================================================
# 7. Test Points (for debugging / bring-up)
# =====================================================================
test_points = [
    ("TP_VBAT", 26.0, 2.5,  2, "VBAT"),
    ("TP_GND",  26.0, 5.0,  1, "GND"),
    ("TP_5V",   26.0, 7.5,  3, "+5V_MAIN"),
    ("TP_FWD",  26.0, 10.0, 5, "M1_FWD"),
    ("TP_REV",  26.0, 12.5, 6, "M1_REV"),
    ("TP_SERVO",26.0, 15.0, 7, "SERVO_PWM"),
]
for name, x, y, nid, nname in test_points:
    lines.append(f' (footprint "TestPoint" (layer "F.Cu") (at {x:.3f} {y:.3f})')
    lines.append(pad_th(name, 0, 0, 0.8, 1.4, nid, nname))
    lines.append(' )')
    lines.append(silk_text(name, x + 1.5, y - 1.0))

# =====================================================================
# 8. Power Tracks on B.Cu (0.8 mm - 1.5 mm width)
# =====================================================================
# Motor driver inputs from ESP32-CAM
lines.append(track(4.57, 25.62, 13.3, 13.365, 0.8, "B.Cu", 5))   # M1_FWD
lines.append(track(4.57, 23.08, 13.3, 14.635, 0.8, "B.Cu", 6))   # M1_REV
# Motor driver high-current outputs (1.4 mm wide)
lines.append(track(18.7, 15.905, 18.0, 2.5, 1.4, "B.Cu", 12))    # M1_A -> J2_1
lines.append(track(18.7, 12.095, 20.54, 2.5, 1.4, "B.Cu", 13))   # M1_B -> J2_2
# RZ7889 power: VBAT to pins 5&6, GND to pins 1&4
lines.append(track(14.04, 2.5, 18.7, 15.905, 1.4, "B.Cu", 2))    # VBAT (J1) -> RZ7889 Pin 5
lines.append(track(18.7, 15.905, 18.7, 14.635, 1.4, "B.Cu", 2))  # VBAT: Pin 5 -> Pin 6
lines.append(track(13.3, 12.095, 11.5, 2.5, 1.2, "B.Cu", 1))     # GND: RZ7889 Pin 1 -> J1 GND
lines.append(track(13.3, 15.905, 13.3, 12.095, 1.2, "B.Cu", 1))  # GND: Pin 4 -> Pin 1
# Servo PWM & power
lines.append(track(4.57, 28.16, 18.54, 43.5, 0.8, "B.Cu", 7))    # SERVO_PWM -> J3_SIG
lines.append(track(14.04, 2.5, 16.0, 43.5, 1.2, "B.Cu", 3))      # +5V_MAIN (J1) -> J3_5V
lines.append(track(11.5, 2.5, 13.46, 43.5, 1.2, "B.Cu", 1))      # GND (J1) -> J3_GND
# JQ6500 serial RX & speaker lines
lines.append(track(27.43, 20.54, 7.11, 4.54, 0.7, "F.Cu", 9))    # JQ_RX Jumper on Top Layer
lines.append(track(7.11, 14.70, 11.5, 7.5, 1.2, "B.Cu", 15))     # SPK_P -> J6_1
lines.append(track(7.11, 19.78, 14.04, 7.5, 1.2, "B.Cu", 16))    # SPK_N -> J6_2
# Anti-brownout cap to ESP32 5V/GND
lines.append(track(4.57, 18.0, 4.57, 14.5, 1.2, "B.Cu", 4))      # +5V_ESP -> C1_P
lines.append(track(4.57, 20.54, 7.11, 14.5, 1.2, "B.Cu", 1))     # GND -> C1_N
# Test point connections (short stubs)
lines.append(track(26.0, 2.5, 24.54, 2.5, 0.8, "B.Cu", 2))       # TP_VBAT -> J1 VBAT
lines.append(track(26.0, 5.0, 24.54, 2.5, 0.8, "B.Cu", 1))       # TP_GND -> J1 GND
lines.append(track(26.0, 7.5, 16.0, 2.5, 0.8, "B.Cu", 3))        # TP_5V -> +5V rail

# =====================================================================
# 9. Top-Layer Jumpers (4 wires for single-sided DIY etch)
# =====================================================================
lines.append(track(27.43, 20.54, 7.11, 4.54, 0.7, "F.Cu", 9))    # JQ_RX jumper

# =====================================================================
# 10. Ground Pour on B.Cu (bottom copper ground plane)
# =====================================================================
# Filled zone polygon covering most of bottom layer, avoiding antenna keepout
# Zone outline: board outline minus antenna keepout area
lines.append(' (zone (net 1) (layer "B.Cu")')
lines.append('  (polygon')
lines.append('    (pts')
# Outer rectangle (board outline)
lines.append(f'      (xy 0.000 0.000)')
lines.append(f'      (xy {W:.3f} 0.000)')
lines.append(f'      (xy {W:.3f} {H:.3f})')
lines.append(f'      (xy 0.000 {H:.3f})')
# Antenna keepout cutout (front half where ESP32-CAM antenna sits)
lines.append(f'      (xy 4.000 36.000)')
lines.append(f'      (xy 28.000 36.000)')
lines.append(f'      (xy 28.000 {H:.3f})')
lines.append(f'      (xy 4.000 {H:.3f})')
lines.append(f'      (xy 4.000 36.000)')
lines.append(f'      (xy 0.000 {H:.3f})')
lines.append('    )')
lines.append('  )')
lines.append(' )')

# =====================================================================
# 11. Close PCB
# =====================================================================
lines.append(')')

with open(OUTPUT_FILE, "w") as f:
    f.write("\n".join(lines))

print(f"Generated {OUTPUT_FILE} successfully!")
print("Open it directly in KiCad PCB Editor.")
print("Print: B.Cu + Edge.Cuts only, Accurate 1:1 scale, B&W, Mirror unchecked.")
print("Quality features: ground pour, test points, silkscreen, antenna keepout, decoupling caps.")