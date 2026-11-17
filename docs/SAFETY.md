# Safety Checklist — Supercar RC Car

> Read before first power-on. Li-ion batteries and high-current motors can cause fire or injury if mishandled.

## Battery Safety (2S 18650 Li-ion)

| Hazard | Prevention |
|--------|------------|
| Over-discharge (< 2.5 V/cell) | Always use BMS board. Firmware low-battery warning at 6.5 V. Never leave car on unattended. |
| Over-charge (> 4.25 V/cell) | Use proper Li-ion charger. Never charge unattended. |
| Short circuit | Inspect all wiring before first power-on. No exposed conductors near battery terminals. |
| Physical damage | Secure battery in cradle. No sharp edges near cells. |
| Fire | Keep fire extinguisher nearby. Charge on non-flammable surface. |

**Never:** Charge Li-ion cells below 2.5 V, short battery terminals, puncture cells, or leave charging unattended.

## Electrical Safety

| Hazard | Prevention |
|--------|------------|
| Brownout / crash | Use dedicated 5V buck (MP1584EN), not L298N regulator. 470 µF cap at ESP32-CAM 5V pin. |
| GPIO 12 boot lockout | GPIO 12 must be LOW/floating at boot. No external pull-up. |
| Shoot-through (H-bridge) | Firmware deadzone prevents simultaneous FWD+REV. Hardware: RZ7889 has internal shoot-through protection. |
| Motor inductive spikes | 100 nF caps across motor terminals (C5–C11). Flyback diodes on relay approach. |

## Mechanical Safety

| Hazard | Prevention |
|--------|------------|
| Steering stall burnout | SG92R servo limited to ±45°. PTC polyfuse (500 mA) recommended in series. |
| Wheel detachment | M2.5 set-screws tight on rear rims. E-clips on front axles. |
| Chassis failure under 500 g | PETG, 4 walls, 40% gyroid infill. Check geometry check passed before printing. |

## Pre-Flight Checklist (Every Session)

```
[ ] Battery voltage > 6.5 V (check telemetry before driving)
[ ] BMS board installed and functional
[ ] All wiring secure, no exposed conductors
[ ] No mechanical binding (wheels spin free, steering centers)
[ ] ESP32-CAM firmware flashed (v2 with watchdog + failsafe)
[ ] Fail-safe tested: disconnect WS → motors stop within 250 ms
[ ] Operating area clear of people, pets, obstacles
[ ] Fire extinguisher accessible
[ ] Car on ground (not elevated) for high-speed testing
```

## Emergency Procedures

| Situation | Action |
|-----------|--------|
| Smoke or burning smell | Disconnect battery immediately. Do not reconnect until fault found. |
| Li-ion fire | Use Class D fire extinguisher or sand. Do NOT use water. |
| Car out of control | Disconnect WS client → fail-safe stops motors within 250 ms. |
| Motor stall / smoke | Disconnect battery. Check for mechanical binding. |
| ESP32-CAM brownout loop | Disconnect battery. Verify 5V buck output. Check for shorts. |

## Disclaimer

This is a hobby/educational project. Not a toy. Not suitable for children without adult supervision. Build and operate at your own risk.