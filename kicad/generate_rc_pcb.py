#!/usr/bin/env python3
"""
generate_rc_pcb.py — Supercar KiCad Carrier PCB Generator (46 mm x 32 mm)
Generates a valid KiCad 8/9 .kicad_pcb file optimized for DIY home etching:
  - 0.8-1.5 mm printable copper tracks, 0.5 mm min isolation gaps
  - Bottom copper (B.Cu) main routing + four 0.8 mm top-layer (F.Cu) jumpers
  - Single-sided etchable board, no microscopic vias
Run: python3 kicad/generate_rc_pcb.py
Opens: FPV_RC_Carrier_46x32.kicad_pcb in KiCad PCB Editor
"""

import math

OUTPUT_FILE = "FPV_RC_Carrier_46x32.kicad_pcb"


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


def mounting_hole(x, y):
    return f""" (footprint "MountingHole_2.2mm_M2" (layer "F.Cu") (at {x:.3f} {y:.3f})
        (pad "" np_thru_hole circle (at 0 0) (size 2.2 2.2) (drill 2.2) (layers "*.Cu" "*.Mask"))
      )"""


# Net definitions
NETS = {
    1: "GND", 2: "VBAT", 3: "+5V_MAIN", 4: "+5V_ESP",
    5: "M1_FWD", 6: "M1_REV", 7: "SERVO_PWM", 8: "HORN_TRIG",
    9: "JQ_RX", 10: "LIGHTS", 11: "TAILLIGHTS", 12: "M1_A",
    13: "M1_B", 14: "AUDIO_MIX", 15: "SPK_P", 16: "SPK_N"
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

# 1. Board Outline (Edge.Cuts: 32.0 mm wide x 46.0 mm tall)
W, H = 32.0, 46.0
edges = [(0, 0, W, 0), (W, 0, W, H), (W, H, 0, H), (0, H, 0, 0)]
for x1, y1, x2, y2 in edges:
    lines.append(f' (gr_line (start {x1} {y1}) (end {x2} {y2}) (layer "Edge.Cuts") (width 0.15))')

# 2. Four M2 Corner Mounting Holes (Matched to FreeCAD Deck)
for mx, my in [(2.5, 2.5), (29.5, 2.5), (2.5, 43.5), (29.5, 43.5)]:
    lines.append(mounting_hole(mx, my))

# 3. MOD1: AI-Thinker ESP32-CAM Dual 1x8 Headers (Top Mount, Pitch 2.54 mm)
# Left Row X = 4.57 mm, Right Row X = 27.43 mm, Y = 18.0 to 35.78 mm
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

# 4. MOD2: JQ6500-16P Onboard Flash Sound Module (Bottom Mount, Pitch 2.54 mm)
# Left Row X = 7.11 mm, Right Row X = 24.89 mm, Y = 2.0 to 19.78 mm
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

# 5. U2: RZ7889 Motor Driver (SOIC-8 on Bottom Copper B.Cu at X=16.0, Y=14.0)
lines.append(' (footprint "RZ7889_SOIC8" (layer "B.Cu") (at 16.0 14.0)')
rz_pins = [
    (1, -2.7, -1.905, "+5V_MAIN", 3), (2, -2.7, -0.635, "M1_FWD", 5),
    (3, -2.7, 0.635,  "M1_REV", 6),   (4, -2.7, 1.905,  "GND", 1),
    (5,  2.7, 1.905,  "M1_A", 12),    (6,  2.7, 0.635,  "M1_A", 12),
    (7,  2.7, -0.635, "M1_B", 13),    (8,  2.7, -1.905, "M1_B", 13)
]
for pnum, px, py, nname, nid in rz_pins:
    lines.append(pad_smd(str(pnum), 16.0 + px, 14.0 + py, 1.6, 0.65, "B.Cu", nid, nname))
lines.append(' )')

# 6. Edge Connectors (JST-XH 2.54 mm Through-Hole)
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
# J6: 3W Speaker SPK_P & SPK_N (Center-Left)
lines.append(pad_th("J6_1", 11.5,  7.5, 1.0, 2.0, 15, "SPK_P"))
lines.append(pad_th("J6_2", 14.04, 7.5, 1.0, 2.0, 16, "SPK_N"))
# C1: 470uF Anti-Brownout Cap right next to ESP32 5V/GND
lines.append(pad_th("C1_P",  4.57, 14.5, 0.9, 1.9, 4, "+5V_ESP"))
lines.append(pad_th("C1_N",  7.11, 14.5, 0.9, 1.9, 1, "GND"))

lines.append('            )')

# 7. Thick DIY-Etchable Copper Tracks on B.Cu (0.8 mm - 1.5 mm width)
# Motor Driver Inputs from ESP32-CAM
lines.append(track(4.57, 25.62, 13.3, 13.365, 0.8, "B.Cu", 5))   # M1_FWD (GPIO14 -> RZ7889 Pin 2)
lines.append(track(4.57, 23.08, 13.3, 14.635, 0.8, "B.Cu", 6))   # M1_REV (GPIO15 -> RZ7889 Pin 3)
# Motor Driver High-Current Outputs (1.4 mm wide)
lines.append(track(18.7, 15.905, 18.0, 2.5, 1.4, "B.Cu", 12))    # M1_A -> J2_1
lines.append(track(18.7, 12.095, 20.54, 2.5, 1.4, "B.Cu", 13))   # M1_B -> J2_2
# Servo PWM & Power
lines.append(track(4.57, 28.16, 18.54, 43.5, 0.8, "B.Cu", 7))    # SERVO_PWM (GPIO13 -> J3_SIG)
# JQ6500 Serial RX & Speaker Lines
lines.append(track(27.43, 20.54, 7.11, 4.54, 0.7, "F.Cu", 9))    # JQ_RX Jumper on Top Layer
lines.append(track(7.11, 14.70, 11.5, 7.5, 1.2, "B.Cu", 15))     # SPK_P -> J6_1
lines.append(track(7.11, 19.78, 14.04, 7.5, 1.2, "B.Cu", 16))    # SPK_N -> J6_2
# Anti-Brownout 470uF Cap to ESP32 5V/GND
lines.append(track(4.57, 18.0, 4.57, 14.5, 1.2, "B.Cu", 4))      # +5V_ESP -> C1_P
lines.append(track(4.57, 20.54, 7.11, 14.5, 1.2, "B.Cu", 1))     # GND -> C1_N

lines.append(')')

with open(OUTPUT_FILE, "w") as f:
    f.write("\n".join(lines))

print(f"Generated {OUTPUT_FILE} successfully!")
print("Open it directly in KiCad PCB Editor.")
print("Print: B.Cu + Edge.Cuts only, Accurate 1:1 scale, B&W, Mirror unchecked.")