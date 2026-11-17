# Troubleshooting Guide

> Top failure modes for the Supercar ESP32-CAM FPV RC car, with symptoms, causes, and fixes.
> Keep this handy during bring-up and field testing.

## How to Use

Match your symptom to the section below. Check the simplest cause first. Use a multimeter for electrical checks and the WebSocket telemetry (`{"C":"get"}`) for runtime diagnostics.

---

## 1. ESP32-CAM Won't Boot / Boot Loop

| Symptom | Possible Cause | Fix |
|---------|---------------|-----|
| Repeated reboots, "Brownout detector was triggered" | 5V rail droops under motor/Wi-Fi load | Verify MP1584EN outputs 4.90–5.15 V. Add 470 µF cap at ESP32-CAM 5V pin. Use dedicated buck, not L298N 5V. |
| "flash read err, 1000" on Serial | GPIO 12 pulled HIGH at boot | Remove pull-up from GPIO 12. GPIO 12 must be LOW/floating at boot. |
| Constant reboot, no Serial output | GPIO 0 held LOW | Remove GPIO 0→GND jumper after flashing. |
| Camera init failed | Camera ribbon not seated | Reseat OV2640 FPC. Check camera pin definitions match AI-Thinker. |
| Wi-Fi AP doesn't appear | Brownout or crash | Check Serial for crash dump. Verify 5V rail under load. |

**Quick check:** Multimeter at ESP32-CAM 5V pin (ESP32-CAM unplugged, battery connected) must read 4.90–5.15 V steady.

---

## 2. Motors Don't Spin

| Symptom | Possible Cause | Fix |
|---------|---------------|-----|
| No movement, WS connected | ENA jumper missing (L298N) or PWM not attached | Verify RZ7889 VCC = VBAT (7.4V). Check GPIO 14/15 PWM output with oscilloscope/multimeter. |
| Motor spins one direction only | H-bridge input wired wrong | Swap M1_A/M1_B or check GPIO 14/15 mapping. |
| Motor jitters, doesn't turn | Insufficient voltage / current | Verify battery > 6.5 V. Check RZ7889 not overheating (>60°C). |
| Motor spins but wheels don't | Axle coupler slipping | Tighten 3 mm brass coupler grub screws. |
| Wheels turn but car doesn't move | Tire not gripped to rim | Stretch TPU tire fully over rim bead groove. |

**Quick check:** With ESP32-CAM unplugged, tap GPIO 14 then GPIO 15 with a 3.3V jumper. Motor should spin forward then reverse.

---

## 3. Steering Doesn't Work

| Symptom | Possible Cause | Fix |
|---------|---------------|-----|
| Servo doesn't move | PWM on wrong pin / servo not powered | Verify GPIO 13 = SERVO_PWM. Check J3 5V and GND. |
| Steering binds at full lock | Servo travel exceeds mechanical limits | Reduce servo_min/max_duty in firmware config. Check C-hub kingpin holes aren't blocked. |
| Steering jitters under load | Servo stall at mechanical stop | Add PTC polyfuse (500 mA) in series. Limit servo travel to ±40°. |
| Wheels don't turn with servo | Tie-rod disconnected | Reconnect tie-rod ball joints to steering arms. |

**Quick check:** Send `{"S":-45}` then `{"S":45}` over WS. Servo should move left then right.

---

## 4. No Video Stream

| Symptom | Possible Cause | Fix |
|---------|---------------|-----|
| `http://192.168.4.1:81/stream` won't load | Camera init failed or port conflict | Check Serial for "Camera init failed". Verify Port 81 not blocked. |
| Video freezes / low FPS | Wi-Fi interference or PWM timer conflict | Move motor/servo PWM to LEDC Timer 1 & 2 (never Timer 0). Reduce JPEG quality. |
| Video works but no WS control | WebSocket not connected | Check WS URL `ws://<ip>:81/ws` — note: WS is on Port 80, video on Port 81! |

**Quick check:** Connect phone to `RC_FPV_CAR` AP, open `http://192.168.4.1:81/stream` in browser.

---

## 5. Audio / Horn Issues

| Symptom | Possible Cause | Fix |
|---------|---------------|-----|
| No sound from speaker | DFPlayer not initialized or wrong track file | Verify `/mp3/0001.mp3` exists on MicroSD. Check DFPlayer VCC = 5V. |
| Horn works but no music | Music track missing or wrong folder | Verify `/mp3/0003.mp3`+ exists. Check FAT32 format on SD card. |
| Music cuts out during motor load | Power sag on audio rail | Verify C2/C3 220 µF caps on 5V_SERVO_AUDIO rail. |
| Horn doesn't stop | GPIO 12 stuck HIGH | Check AO3400 gate resistor. Verify GPIO 12 not pulled up. |

**Quick check:** Send `{"M":"play"}` → should hear music. Send `{"H":1}` → should hear horn over music.

---

## 6. Battery / Power Issues

| Symptom | Possible Cause | Fix |
|---------|---------------|-----|
| Battery voltage reads 0 in telemetry | ADC divider not wired | Verify GPIO 34 connected to voltage divider on battery pack. |
| Car stops after 250 ms | Failsafe triggered (normal on disconnect) | Reconnect WS client. Increase `failsafe_ms` if needed. |
| 5V rail drops below 4.75 V under load | Buck converter undersized | Verify MP1584EN can handle 3A peak. Add bulk capacitance. |
| Battery drains quickly | Motor stalled or short | Check for mechanical binding. Verify no VCC→GND shorts. |

**Quick check:** Telemetry `{"C":"get"}` returns battery voltage. 2S Li-ion: 8.4 V full, 6.5 V low cutoff.

---

## 7. Wi-Fi / Connection Issues

| Symptom | Possible Cause | Fix |
|---------|---------------|-----|
| Can't connect to `RC_FPV_CAR` AP | AP not broadcasting or out of range | Move closer. Check Serial for AP start message. |
| WS connects then drops | Wi-Fi modem sleep or interference | `WiFi.setSleep(false)` is set. Try different Wi-Fi channel. |
| mDNS `supercar.local` not found | mDNS not supported on phone | Use IP address directly (check Serial for AP IP). |

**Quick check:** Serial monitor shows AP IP address. Phone Wi-Fi settings show `RC_FPV_CAR` connected.

---

## 8. Overheating

| Symptom | Possible Cause | Fix |
|---------|---------------|-----|
| RZ7889 > 60 °C | Motor stalled or excessive current | Check for mechanical binding. Reduce throttle max. |
| MP1584EN hot | Output overloaded | Verify total 5V load < 3A. Add heatsink if needed. |
| ESP32-CAM hot | Brownout / continuous transmit | Verify 5V rail. Reduce camera frame rate or JPEG quality. |

**Quick check:** Touch components after 2 min of full-throttle operation. None should be too hot to touch (>60 °C).

---

## 9. Bring-Up Checklist (Before First Power-On)

```
[ ] No VCC→GND shorts (multimeter continuity, all rails >1 kΩ)
[ ] 5V rail: 4.90–5.15 V at ESP32-CAM header (ESP32-CAM unplugged)
[ ] GPIO 12 reads 0 V at boot (no pull-up)
[ ] GPIO 0 not jumpered to GND (unless flashing)
[ ] Motor wires secured, no exposed conductors
[ ] Battery connector polarity correct (VBAT+, GND-)
[ ] Antenna wire soldered (17.3 cm for 433 MHz, or ESP32-CAM PCB antenna clear)
[ ] Wheels off ground for first test (chassis on box)
[ ] Fire extinguisher nearby (Li-ion safety)
```

---

## 10. Debug Commands (WebSocket)

Send these over `ws://<ip>:80/ws`:

| Command | Purpose |
|---------|---------|
| `{"C":"get"}` | Get telemetry (battery V, RSSI, uptime, config) |
| `{"T":100,"S":0}` | Drive forward at 100/255 throttle |
| `{"T":-100,"S":0}` | Drive reverse |
| `{"S":-45}` | Full left steering |
| `{"S":45}` | Full right steering |
| `{"H":1}` then `{"H":0}` | Horn press + release |
| `{"V":30}` | Max volume |
| `{"M":"play"}` | Start music |
| `{"M":"engine"}` | Engine rev sound |
| `{"L":1}` | Headlights on |

Expected telemetry response:
```json
{"V":7.4,"RSSI":-45,"UPTIME":123456,"MOTOR_DEADZONE":12,"AUDIO_VOL":22,"FAILSAFE_MS":250}
```

---

## Still Stuck?

1. Check Serial Monitor (115200 baud) for error messages
2. Re-read `docs/FIRMWARE_GUIDE.md` flashing section
3. Verify PCB against `docs/PINOUT.md` netlist
4. Check FreeCAD geometry check passed (0 invalid shapes)
5. Create an issue with: symptom, steps tried, Serial output, photos of PCB