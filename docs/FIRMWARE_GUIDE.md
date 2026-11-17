# ESP32-CAM Firmware Guide

Source: `super car.pdf` firmware sections + production quality upgrades (v2).
Flash `firmware/FPV_Car_DFPlayer_AutoResume.ino` to the AI-Thinker ESP32-CAM.

## Version

| Version | Key Changes |
|---------|-------------|
| v1 | Basic WS :80 + MJPEG :81, JQ6500 UART, horn auto-resume, 250 ms failsafe |
| v2 | Preferences config, watchdog, OTA, battery monitor, Wi-Fi reconnect, DFPlayer ACK, status LED, telemetry |

## Required Libraries (Arduino Library Manager)

- `ESPAsyncWebServer` & `AsyncTCP` (ESP32Async / mathieucarbou)
- `ArduinoJson` v7.x
- `Preferences` (built-in with ESP32 core)
- `esp_task_wdt` (built-in with ESP32 core)
- `ESPmDNS` (built-in with ESP32 core)
- `ArduinoOTA` (built-in with ESP32 core)
- Board package: ESP32 v3.x; Board: **AI Thinker ESP32-CAM**

## Architecture

- **Port 80** — AsyncWebSocket `/ws`: joystick, steering, horn, lights, volume, music commands + telemetry
- **Port 81** — Dedicated MJPEG camera stream (`/stream`)
- **LEDC Timer 0 / Channel 0** — claimed by OV2640 camera (20 MHz XCLK). Motors/servo/speaker use Timer 1 & 2 only.
- **Wi-Fi SoftAP** — `RC_FPV_CAR` / `12345678`, modem sleep disabled, mDNS `supercar.local`
- **Failsafe** — configurable packet timeout (default 250 ms) stops wheels (music keeps playing)
- **Auto-resume** — music restarts after configurable delay after horn release
- **Watchdog** — ESP32 Task Watchdog, 10 s timeout, auto-resets on hang
- **OTA** — ArduinoOTA over Wi-Fi for wireless firmware updates

## GPIO Assignment

| Pin | Function | PWM Timer | Note |
|-----|----------|-----------|------|
| GPIO 14 | M1_FWD (N20 forward) | Timer 1, Ch 2, 8-bit | RZ7889 BI |
| GPIO 15 | M1_REV (N20 reverse) | Timer 1, Ch 3, 8-bit | RZ7889 FI |
| GPIO 13 | SERVO (SG92R) | Timer 2, Ch 4, 16-bit | 50 Hz, 1.0–2.0 ms |
| GPIO 12 | HORN_TRIG | Digital | GPIO 12 LOW/floating at boot |
| GPIO 16 | DF_TX (JQ_RX) | UART2 TX | 1 kΩ resistor to DFPlayer RX |
| GPIO 4 | LIGHTS | Digital | Headlights + onboard flash (shared w/ status LED) |
| GPIO 2 | TAILLIGHT | Digital | Brake/reverse |
| GPIO 34 | BAT_ADC | Analog | Battery voltage divider (ADC1_CH6) |
| GPIO 1 & 3 | UART | Programming header | Kept free for flashing |
| GPIO 0 | IO0_BOOT | Flash mode | Jumper to GND to flash |

## Persistent Configuration (Preferences)

Config is stored in ESP32 NVS and persists across reboots/reflashes:

| Key | Type | Default | Meaning |
|-----|------|---------|---------|
| ap_ssid | string | "RC_FPV_CAR" | Wi-Fi AP SSID |
| ap_pass | string | "12345678" | Wi-Fi AP password |
| motor_deadzone | uint8 | 12 | Throttle deadzone (0-255) |
| servo_center | int16 | 4915 | Servo center duty (16-bit) |
| servo_min_duty | int16 | 3400 | Full left duty |
| servo_max_duty | int16 | 6400 | Full right duty |
| audio_volume | uint8 | 22 | Speaker volume (0-30) |
| auto_resume | bool | true | Resume music after horn |
| resume_delay_ms | uint16 | 1500 | Delay before music resume |
| failsafe_ms | uint16 | 250 | Failsafe timeout |

Volume changes auto-save to Preferences. Other values are edited in code and re-flashed.

## WebSocket Protocol

JSON over `ws://192.168.4.1/ws`:

```json
{"T": 210, "S": 0, "H": 0, "L": 1, "V": 25, "M": "play", "C": "get"}
```

| Key | Type | Range | Meaning |
|-----|------|-------|---------|
| T | int | -255…255 | Throttle (rear motor) |
| S | int | -45…45 | Steering angle (SG92R) |
| H | int | 0/1 | Horn trigger (edge-detected) |
| L | int | 0/1 | Headlights toggle |
| V | int | 0…30 | Speaker volume (persisted) |
| M | string | play/pause/next/prev/engine | Music command |
| C | string | "get" | Request telemetry JSON |

Telemetry is pushed automatically every 500 ms and on `{"C":"get"}`:

```json
{"V": 7.4, "RSSI": -45, "UPTIME": 123456, "MOTOR_DEADZONE": 12, "AUDIO_VOL": 22, "FAILSAFE_MS": 250}
```

Camera stream: `http://192.168.4.1:81/stream`

## DFPlayer / JQ6500 UART Driver

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
Horn released (H:0) → if music active, schedule resume in resume_delay_ms
Timer expires       → dfPlayTrack(currentMusicTrack)
```

Music is **not** auto-started if it was paused before the horn.

## Battery Monitoring

ADC on GPIO 34 reads voltage through a 100k/100k divider on the 2S Li-ion pack.
- Low threshold: 6.5 V (hardcoded in firmware)
- Telemetry reports voltage in volts
- Low battery prints warning to Serial

## Flashing

### USB (first time)
1. Connect USB-TTL to J7 header: TX→GPIO3, RX→GPIO1, GND→GND
2. Jumper GPIO 0 → GND (flash mode)
3. Upload via Arduino IDE (AI Thinker ESP32-CAM, 115200 baud)
4. Remove GPIO 0 jumper, reset

### OTA (wireless, after first flash)
- ArduinoOTA is available at `supercar.local` (mDNS)
- Re-upload firmware without USB cable

## Testing

1. Power on with MicroSD in DFPlayer (`/mp3/0001.mp3` horn, `0002.mp3` engine, `0003.mp3+` music)
2. Connect to WS, send `{"V":25,"M":"play"}` → music plays, video on :81 doesn't stutter
3. Send `{"H":1}` → horn over music; release → music resumes after 1.5 s
4. Drive: `{"T":150,"S":-20}` → forward + left steer; taillights reverse on throttle < -deadzone
5. Disconnect phone → car stops within failsafe_ms (failsafe)
6. Check telemetry: `{"C":"get"}` → returns battery V, RSSI, uptime, config
7. OTA: re-upload firmware via ArduinoOTA without USB cable