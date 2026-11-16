# ESP32-CAM Firmware Guide

Source: `super car.pdf` firmware sections. Flash `firmware/FPV_Car_DFPlayer_AutoResume.ino` to the AI-Thinker ESP32-CAM.

## Required Libraries (Arduino Library Manager)

- `ESPAsyncWebServer` & `AsyncTCP` (ESP32Async / mathieucarbou)
- `ArduinoJson` v7.x
- Board package: ESP32 v3.x; Board: **AI Thinker ESP32-CAM**

## Architecture

- **Port 80** — AsyncWebSocket `/ws`: joystick, steering, horn, lights, volume, music commands
- **Port 81** — Dedicated MJPEG camera stream (`/stream`)
- **LEDC Timer 0 / Channel 0** — claimed by OV2640 camera (20 MHz XCLK). Motors/servo/speaker use Timer 1 & 2 only.
- **Wi-Fi SoftAP** — `RC_FPV_CAR` / `12345678`, modem sleep disabled
- **Failsafe** — 250 ms packet timeout stops wheels (music keeps playing)
- **Auto-resume** — music restarts 1.5 s after horn release

## GPIO Assignment

| Pin | Function | PWM Timer | Note |
|-----|----------|-----------|------|
| GPIO 14 | M1_FWD (N20 forward) | Timer 1, Ch 2, 8-bit | RZ7889 BI |
| GPIO 15 | M1_REV (N20 reverse) | Timer 1, Ch 3, 8-bit | RZ7889 FI |
| GPIO 13 | SERVO (SG92R) | Timer 2, Ch 4, 16-bit | 50 Hz, 1.0–2.0 ms |
| GPIO 12 | HORN_TRIG | Digital | GPIO 12 LOW/floating at boot |
| GPIO 16 | DF_TX (JQ_RX) | UART2 TX | 1 kΩ resistor to DFPlayer RX |
| GPIO 4 | LIGHTS | Digital | Headlights + onboard flash |
| GPIO 2 | TAILLIGHT | Digital | Brake/reverse |

## WebSocket Protocol

JSON over `ws://192.168.4.1/ws`:

```json
{"T": 210, "S": 0, "H": 0, "L": 1, "V": 25, "M": "play"}
```

| Key | Type | Range | Meaning |
|-----|------|-------|---------|
| T | int | -255…255 | Throttle (rear motor) |
| S | int | -45…45 | Steering angle (SG92R) |
| H | int | 0/1 | Horn trigger (edge-detected) |
| L | int | 0/1 | Headlights toggle |
| V | int | 0…30 | Speaker volume |
| M | string | play/pause/next/prev/engine | Music command |

Camera stream: `http://192.168.4.1:81/stream`

## DFPlayer / JQ6500 UART Driver (no external library)

10-byte DFPlayer packets or 6-byte JQ6500 packets sent over `HardwareSerial dfSerial(2)` on GPIO 16.

DFPlayer commands:
- `0x12` play track `/mp3/NNNN.mp3`
- `0x06` set volume 0–30
- `0x0E` pause
- `0x0D` resume

JQ6500 commands:
- `7E 04 03 [hi] [lo] EF` play track
- `7E 03 06 [vol] EF` set volume

## Auto-Resume State Machine

```
Horn pressed (H:1)  → play track 0001.mp3, cancel pending resume
Horn released (H:0) → if music was active, schedule resume in 1500 ms
Timer expires       → dfPlayTrack(currentMusicTrack)
```

Music is **not** auto-started if it was paused before the horn.

## Flashing

1. Connect USB-TTL to J7 header: TX→GPIO3, RX→GPIO1, GND→GND
2. Jumper GPIO 0 → GND (flash mode)
3. Upload via Arduino IDE (AI Thinker ESP32-CAM, 115200 baud)
4. Remove GPIO 0 jumper, reset

## Testing

1. Power on with MicroSD in DFPlayer (`/mp3/0001.mp3` horn, `0002.mp3` engine, `0003.mp3+` music)
2. Connect to WS, send `{"V":25,"M":"play"}` → music plays, video on :81 doesn't stutter
3. Send `{"H":1}` → horn over music; release → music resumes after 1.5 s
4. Drive: `{"T":150,"S":-20}` → forward + left steer; taillights reverse on throttle < -12
5. Disconnect phone → car stops within 250 ms (failsafe)