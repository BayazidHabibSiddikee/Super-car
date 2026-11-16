# KiCad Carrier PCB Guide — 46 mm × 32 mm

Source: `super car.pdf` KiCad schematic + layout sections. The carrier board plugs the ESP32-CAM on top and holds all SMD power/driver/audio parts underneath.

## Board Origin & Outline

- Edge.Cuts rectangle: X = 0 → 32.0 mm (width), Y = 0 → 46.0 mm (length)
- Y = 46.0 mm = Front (camera) edge; Y = 0.0 mm = Rear (speaker/battery) edge
- Four M2 mounting holes at: (2.5, 2.5), (29.5, 2.5), (2.5, 43.5), (29.5, 43.5)

## Component Placement (Coordinate Map)

| Module | Side | Center (X, Y) | Orientation |
|--------|------|---------------|-------------|
| 4× M2 mounting holes | Both | (2.5, 2.5), (29.5, 2.5), (2.5, 43.5), (29.5, 43.5) | Match FreeCAD deck bosses |
| MOD1 ESP32-CAM headers | Top (F.Cu) | Left row X=4.57, Right row X=27.43, Y=18→35.78 | 22.86 mm row spacing; overhangs front edge |
| MOD2 JQ6500/DFPlayer headers | Bottom (B.Cu) | Left row X=7.11, Right row X=24.89, Y=2→19.78 | 17.78 mm row spacing; MicroSD slot faces rear |
| U1 MP1584EN + L1 buck | Top | (16.0, 26.0) | Under ESP32-CAM, height < 3 mm |
| U2 RZ7889 motor driver | Top | (16.0, 14.0) | Under rear half of ESP32-CAM |
| Q1,Q2,Q3 AO3400 | Top | X=10,16,22 at Y=35.0 | Near front edge, short traces to LED/horn plugs |
| C1 470 µF + C2/C3 220 µF | Top | X=6,14,22 at Y=7.5 | Rear zone, full vertical height unobstructed |
| J1 battery + J2 motor | Top | J1 (6.0, 2.5), J2 (14.0, 2.5) | Rear edge, facing up/rear-entry |
| J6 speaker + SW1 switch | Top | J6 (22.0, 2.5), SW1 (28.5, 9.0) | Rear edge / right edge protrusion |
| J3 servo + J4/J5 LEDs | Top | J3 (16.0, 41.5), J4 (7.5, 41.5), J5 (24.5, 41.5) | Front edge, right-angle, under camera overhang |
| J7 1×4 UART flash | Top | (2.0, 11.0) | Left edge, right-angle for USB-TTL |

## Antenna Keepout

- Rule Area / Keepout on F.Cu + B.Cu: X = 4→28 mm, Y = 36→46 mm
- No copper pours or tracks under the ESP32-CAM antenna overhang
- Keeps Wi-Fi video range at 50+ m LOS

## Trace Width Net Classes (KiCad → Board Setup → Net Classes)

| Net Class | Members | Width | Clearance |
|-----------|---------|-------|-----------|
| Power_HighCurrent | VBAT, V_MOTOR, M1_A, M1_B | 1.5 mm | 0.3 mm |
| Power_5V | +5V_MAIN, +5V_ESP | 0.8 mm | 0.25 mm |
| Default | Signals | 0.25 mm | 0.25 mm |

- Flood F.Cu and B.Cu with GND pour outside antenna keepout
- 0.3 mm stitching vias around RZ7889 and MP1584EN ground pads

## DIY Home-Etch Generation

Run `python3 kicad/generate_rc_pcb.py` to produce `FPV_RC_Carrier_46x32.kicad_pcb`. The script optimizes for single-sided DIY etching:

- 0.8–1.5 mm traces, 0.5 mm min isolation gaps
- Bottom copper (B.Cu) main routing + four 0.8 mm top-layer jumpers
- Open in KiCad PCB Editor → Plot → Print: **B.Cu + Edge.Cuts only**, **Accurate 1:1 scale**, **B&W**, **Mirror unchecked**
- Verify 2.54 mm header pins and RZ7889 SOIC-8 pads align on printed paper before etching
- Etch ferric chloride, drill 0.9–1.0 mm header holes, 2.2 mm mounting holes
- Solder four top-side jumpers, then modules

## Bring-Up Verification (Before Plugging in ESP32-CAM)

1. **Power-to-GND short check** (continuity mode, unpowered): VBAT→GND, +5V_ESP→GND, M1_A/B→GND must all read >1 kΩ or OL (brief cap-charge chirp OK)
2. **5V regulator output** (battery connected, ESP32-CAM unplugged): 4.90–5.15 V at empty ESP32-CAM header; GPIO 12 reads 0 V
3. **Manual H-bridge/horn trigger** (3.3 V jumper tap on GPIO sockets 14, 15, 13, 12, 2): motor spins F/R, steering L/R, horn sounds
4. **Seat ESP32-CAM** (motors disconnected): Wi-Fi AP `RC_FPV_CAR` appears in < 5 s, camera stream at `http://192.168.4.1:81/stream`, no brownout resets
5. **Full-load stall test** (wheels in air): full throttle → reverse → steer L/R + horn simultaneously; 5V rail never < 4.75 V, H-bridge < 60 °C