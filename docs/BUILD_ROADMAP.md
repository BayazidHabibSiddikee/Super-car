# Build Roadmap — Execution Path

> This is the dependency-ordered path to build the ESP32-CAM FPV RC car.  
> Phase N must complete before Phase N+1 begins.  
> Source: `super car.pdf` (53 pages), extracted into this repo.

```mermaid
flowchart TD
    %% Phase 0 — Project setup
    P0[("Phase 0: Project Scaffold")] --> P1
    P0:::phase0

    %% Phase 1 — Mechanical
    P1[("Phase 1: FreeCAD Mechanical Design")] --> P2
    P1:::phase1
    P1 --> P1a[Rear N20 + MR63ZZ gearbox<br/>Enzo_FPV_v2.py]
    P1 --> P1b[Front SG92R + Ackermann C-hub<br/>Enzo_FPV_v2.py]
    P1 --> P1c[Modular Enzo shell + glass + audio<br/>Enzo_FPV_v2.py]
    P1 --> P1d[Master print plate - 15 parts<br/>FPV_RC_Direct_Print_Plate.py]

    %% Phase 2 — PCB
    P2[("Phase 2: KiCad Carrier PCB<br/>46 × 32 mm")] --> P3
    P2:::phase2
    P2 --> P2a[MP1584EN 5V buck + brownout protection]
    P2 --> P2b[RZ7889 SOIC-8 H-bridge for N20]
    P2 --> P2c[HXJ8002 3W Class-D amp + audio mixer]
    P2 --> P2d[AO3400 MOSFETs: horn, headlights, taillights]
    P2 --> P2e[JQ6500-16P onboard flash + MH-M18 Bluetooth]
    P2 --> P2f[ESP32-CAM 1×8 headers + UART flash header]

    %% Phase 3 — Electronics assembly
    P3[("Phase 3: Populate PCB &<br/>Wire Harness")] --> P4
    P3:::phase3
    P3 --> P3a[SMD reflow / hand-solder 0805 passives]
    P3 --> P3b[Through-hole JST-XH connectors + headers]
    P3 --> P3c[Multimeter smoke test: no VCC→GND short]
    P3 --> P3d[Verify 4.90–5.15V on ESP32-CAM 5V rail]

    %% Phase 4 — Firmware
    P4[("Phase 4: ESP32-CAM Arduino Firmware")] --> P5
    P4:::phase4
    P4 --> P4a[Port 80 AsyncWebSocket: T/S/H/L/V/M commands]
    P4 --> P4b[Port 81 MJPEG camera stream (LEDC Timer 0)]
    P4 --> P4c[Motor/servo PWM on LEDC Timer 1 & 2<br/>never Timer 0]
    P4 --> P4d[DFPlayer/JQ6500 UART on GPIO 16 + horn on GPIO 12]
    P4 --> P4e[250 ms failsafe: stop wheels on Wi-Fi drop]
    P4 --> P4f[1.5 s auto-resume music after horn]

    %% Phase 5 — Audio architecture A
    P5[("Phase 5: Architecture A Audio<br/>Phone Music + Onboard Horn")] --> P6
    P5:::phase5
    P5 --> P5a[MH-M18 Bluetooth A2DP → phone streams music]
    P5 --> P5b[JQ6500-16P 8 MB SPI flash → drag-and-drop horn/engine MP3]
    P5 --> P5c[10 kΩ + 1 µF passive mixer into HXJ8002 IN-]
    P5 --> P5d[10 Ω ferrite + 100 µF/100 nF on MH-M18 5V rail]

    %% Phase 6 — Mechanical assembly
    P6[("Phase 6: Chassis Assembly<br/>Print & Assemble")] --> P7
    P6:::phase6
    P6 --> P6a[Print PETG chassis, 4 walls, 40% gyroid]
    P6 --> P6b[Press MR63ZZ bearings, N20 + 3 mm steel axle]
    P6 --> P6c[SG92R servo + M2 kingpin steering knuckles]
    P6 --> P6d[Snap-on body shell + TPU tires]
    P6 --> P6e[2S 18650 battery + BMS in lower cradle]

    %% Phase 7 — Bring-up & test
    P7[("Phase 7: Bring-Up &<br/>Smoke Test")] --> P8
    P7:::phase7
    P7 --> P7a[Continuity: no power-to-ground shorts]
    P7 --> P7b[Tap GPIOs 14/15/13/12/2: motor/servo/horn]
    P7 --> P7c[Seat ESP32-CAM: Wi-Fi AP + video stream boots]
    P7 --> P7d[Full-load stall test: 5V > 4.75 V, < 60 °C]

    %% Phase 8 — Drive
    P8[("Phase 8: Field Test &<br/>Commercial Validation")] --> P9
    P8:::phase8
    P8 --> P8a[Phone connects: joystick + horn + lights + music]
    P8 --> P8b[FPV video 20+ FPS at 50 m LOS]
    P8 --> P8c[500 g payload run: no axle flex, no servo stall]

    %% Phase 9 — Production
    P9[("Phase 9: Production Kit<br/>BOM + Gerbers + Docs")]:::phase9

    classDef phase0 fill:#e1f5e1,stroke:#2e7d32,stroke-width:2px
    classDef phase1 fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef phase2 fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef phase3 fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef phase4 fill:#e0f7fa,stroke:#00838f,stroke-width:2px
    classDef phase5 fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    classDef phase6 fill:#fffde7,stroke:#f57f17,stroke-width:2px
    classDef phase7 fill:#ffebee,stroke:#b71c1c,stroke-width:2px
    classDef phase8 fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef phase9 fill:#eceff1,stroke:#37474f,stroke-width:2px

    linkStyle default stroke-width:2px,fill:none,stroke:#666
```

## Phase Summary

| Phase | Deliverable | Exit Criteria |
|-------|-------------|---------------|
| 0 | Repo scaffold + docs | `git commit` clean, README present |
| 1 | 5 FreeCAD parts (STL) | Check Geometry = 0 invalid shapes |
| 2 | `FPV_RC_Carrier_46x32.kicad_pcb` | KiCad DRC = 0 errors, 0 airwires |
| 3 | Populated bare PCB | Multimeter: no shorts, 5V rail OK |
| 4 | Flash firmware | AP `RC_FPV_CAR` broadcasts, video on :81 |
| 5 | Audio mixed output | Phone music + horn overlap on one speaker |
| 6 | Assembled rolling chassis | 500 g payload, wheels turn free |
| 7 | Bring-up passed | Failsafe stops car in < 250 ms |
| 8 | End-to-end drive | Joystick steering + FPV + music + horn |
| 9 | Production package | Gerbers, BOM, assembly docs committed |

## Execution Command Template

At the end of each phase:

```bash
git add -A
git commit -m "feat(phase N): <milestone description>"
git push
```