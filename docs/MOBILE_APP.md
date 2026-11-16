# Mobile FPV Controller Web App (Pending)

> The PDF ends with an offer to provide the embedded HTML5/JS controller. This file reserves the slot and documents the expected interface so `mobile_app/controller.html` can be implemented next.

## Served By

ESP32-CAM AsyncWebServer on Port 80, same IP as WebSocket (`ws://192.168.4.1/ws`).

## Required UI Elements

| Element | Action | WS Message |
|---------|--------|------------|
| Virtual joystick (dual-axis) | Drive + steer | `{"T": -255..255, "S": -45..45}` every 50 ms |
| Horn button (momentary) | Play horn | `{"H": 1}` on press, `{"H": 0}` on release |
| Headlight toggle | Lights on/off | `{"L": 1}` / `{"L": 0}` |
| Volume slider | 0…30 | `{"V": n}` |
| Music buttons | Play/pause/next/prev/engine | `{"M": "play"\|"pause"\|"next"\|"prev"\|"engine"}` |
| MJPEG video `<img src="http://192.168.4.1:81/stream">` | Live FPV | — |
| Connection indicator | WS open/closed | visual |

## Design Constraints

- Video on Port 81, controls on Port 80 — prevents steering freeze during frame drops
- Single-page HTML/JS, no external CDN dependencies (works in SoftAP offline mode)
- Auto-reconnect WebSocket on disconnect
- Failsafe visual when WS drops > 250 ms

## Next Step

Create `mobile_app/controller.html` with vanilla JavaScript + HTML5 touch joystick, then embed it in the ESP32-CAM firmware as PROGMEM or serve from the AsyncWebServer file handler.