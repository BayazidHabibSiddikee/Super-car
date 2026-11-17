# Changelog — Supercar ESP32-CAM FPV RC Car

## [v1.0] — 2026-11-17

### Initial production-quality release

Derived from `super car.pdf` (53-page engineering guide) and rebuilt as a version-tracked, quality-engineered project.

### Firmware (v2)
- Preferences-based persistent configuration (NVS, survives reboot/reflash)
- ESP32 Task Watchdog (10 s, auto-reset on hang)
- ArduinoOTA wireless updates + mDNS (`supercar.local`)
- Battery voltage monitoring on GPIO 34 (ADC1_CH6, 2S Li-ion)
- Wi-Fi reconnection with exponential backoff
- Status LED heartbeat (GPIO 4, deferred when headlights active)
- Telemetry JSON every 500 ms (battery V, RSSI, uptime, config)
- Bounds-checked JSON parsing with error logging
- Software-tracked lights state (GPIO 4 shared with status LED)
- Config request via `{"C":"get"}` telemetry push
- Horn auto-resume: music restarts 1.5 s after horn release
- 250 ms failsafe: stops wheels on control loss

### Web App (controller.html)
- Reconnection overlay with exponential backoff + attempt counter
- Telemetry dashboard: battery voltage, RSSI, uptime, failsafe, volume
- Battery low warning (red indicator)
- Connection status indicators (dot + text)
- FPS counter for FPV stream
- Offline video retry indicator
- Virtual joystick (drive + steer, 20 Hz rate limit)
- Horn, lights, music (play/pause/next/prev/engine), volume controls

### PCB (KiCad generator, 46 × 32 mm)
- Ground pour zone on B.Cu (net GND)
- 6 test points: TP_VBAT, TP_GND, TP_5V, TP_FWD, TP_REV, TP_SERVO
- Silkscreen labels for all connectors and key components
- Antenna keepout rule area on both copper layers
- C1 470 µF decoupling adjacent to ESP32-CAM 5V/GND
- Corrected RZ7889 SOIC-8 pinout (Pins 1,4 = GND; Pins 5,6 = VBAT)
- J4/J5 LED connectors, J7 UART pinout documented
- Single-sided DIY-etchable: 0.8–1.5 mm tracks, 4 top-layer jumpers

### FreeCAD (parametric macros)
- rc_gearboxes.py: Rear N20 + MR63ZZ gearbox, front SG92R + C-hub steering, Ackermann knuckles
- complete_chassis_v2.py: Full 500 g chassis, upper deck, battery cradle, nose bumper
- body_shell.py: Snap-on aerodynamic body shell with wheel arches, camera viewport, spoiler
- wheels_tires.py: PETG rims + TPU chevron treaded tires
- Parameter validation on all scripts (raises on bad dimensions)
- Geometry check integration (checkGeometry() pass/fail report)
- All scripts pass py_compile syntax validation

### Documentation
- README.md — project overview, quick start, repo layout
- DESIGN_QUALITY_ROADMAP.md — quality dimensions, progress tracking
- BUILD_ROADMAP.md — 9-phase execution path with mermaid diagram
- HARDWARE_ARCHITECTURE.md — system topology, pin budget, critical rules
- PINOUT.md — ESP32-CAM → PCB netlist, boot-pin protection checklist
- BOM.md — complete bill of materials with part numbers and LCSC refs
- PCB_GUIDE.md — component placement, trace classes, bring-up verification
- FIRMWARE_GUIDE.md — architecture, GPIO table, WS protocol, flashing, testing
- FREECAD_GUIDE.md — print settings, assembly verification
- MOBILE_APP.md — web app interface specification
- TROUBLESHOOTING.md — top 10 failure modes with symptoms/causes/fixes
- ASSEMBLY.md — 4-phase assembly guide (mechanical, electronics, bring-up, calibration)
- SAFETY.md — Li-ion, electrical, mechanical safety + emergency procedures
- CHANGELOG.md — this file
- .editorconfig — consistent coding style

### Repository Structure
```
supercar/
├── README.md
├── CHANGELOG.md
├── .editorconfig
├── .gitignore
├── docs/                 # 13 markdown documentation files
├── firmware/             # FPV_Car_DFPlayer_AutoResume.ino (v2)
├── freecad/              # 4 Python macros + README
├── kicad/                # generate_rc_pcb.py
├── mobile_app/           # controller.html
└── mermaid/              # build_path.mmd
```