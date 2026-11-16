# Hardware Architecture

Extracted from `super car.pdf`. Single-chip ESP32-CAM design with isolated power rails to prevent camera brownouts under motor/servo load.

## System Topology

```
+---------------------------+
|   2S 18650 Li-ion + BMS   |  7.4V–8.4V
+------------+--------------+
             |
      +------v------+
      |   SW1 Slide |  Main power switch (SS-12D00G3, SPDT 3A)
      +------+------+
             |
      +------v------+     +--------------------------+
      |  D1: SS34   |---->|  VBAT (7.4V) net         |  Reverse-polarity Schottky
      +------+------+     +--------------------------+
             |
   +---------+---------+---------+
   |                         |
+--v--+                   +---v----+
| MP1584EN|               | RZ7889 |  N20 rear motor drive (M1_A / M1_B)
| 5V Buck |               +---+----+
+--+--+                   |   |   
   |  +5V_MAIN            +---v----+
   |                      | J2 JST |  N20 motor connector
   |                      +--------+
   |
+--v--+     +--------------------------+
| C1 470uF| |  ESP32-CAM (plugs on top)|
+--+--+   |  GPIO14  → M1_FWD (PWM)    |
   |      |  GPIO15  → M1_REV (PWM)    |
   |      |  GPIO13  → SERVO_PWM       |
   |      |  GPIO12  → HORN_TRIG       |
   |      |  GPIO16  → JQ_RX (UART2 TX)|
   |      |  GPIO4   → HEADLIGHTS      |
   |      |  GPIO2   → TAILLIGHTS      |
   |      |  GPIO1/3 → UART flash      |
   |      |  GPIO0   → BOOT jumper     |
   |      +--------------------------+
   |
+--v--+
| C2/C3 |  +5V_SERVO_AUDIO (isolated peripheral rail)
+--+--+   |
   |      +--v--+      +--v--+
   |      | SG92R|      | JQ6500-16P |  Onboard 8 MB SPI flash audio
   |      +--+--+      +--+--+       (horn.mp3, engine.mp3, music)
   |         |           |
   |         |     +-----v-----+
   |         |     | MH-M18 BT |  Bluetooth A2DP → phone streams music
   |         |     +-----+-----+
   |         |           |
   |         +----+------+------+
   |              |      |
   |         +----v--+ +--v--+
   |         | HXJ8002| | AO3400|  3W Class-D mixer amp + speaker
   |         +--+-----+ +--+--+
   |            |         |
   |         +--v----+   |
   |         | Speaker|   |
   |         | 3W 4Ω  |   |
   |         +--------+   |
   +-----------------------+
```

## Critical Rules (from PDF)

1. **Never power ESP32-CAM from L298N 5V regulator** — Wi-Fi + motor current spikes >350 mA cause endless brownout reboots. Use a dedicated 5V buck (MP1584EN) with 470 µF cap at the ESP32-CAM 5V pin.
2. **GPIO 12 boot hazard** — sets internal flash voltage at boot. Must stay LOW/floating at startup. No external pull-up on GPIO 12.
3. **LEDC Timer 0 / Channel 0** is claimed by the OV2640 camera (20 MHz XCLK). Motors, servo, and speaker PWM must use LEDC_TIMER_1 / LEDC_TIMER_2, Channels 2–6.
4. **GPIO 1 and GPIO 3** left free for UART flashing; GPIO 0 for flash-mode selection.
5. **Common ground** — star-ground between battery, buck regulator, drivers, and ESP32-CAM.

## Pin Budget Verification (ESP32-CAM, camera active, SD disabled)

| ESP32-CAM Pin | Net | Function | Driver IC | Notes |
|---------------|-----|----------|-----------|-------|
| 5V | +5V_ESP | Buck output | MP1584EN | 470 µF + 100 nF bypass |
| GND | GND | Common ground | — | Solid pour |
| GPIO 14 | M1_FWD | N20 forward | RZ7889 Pin 2 | LEDC_TIMER_1 |
| GPIO 15 | M1_REV | N20 reverse | RZ7889 Pin 3 | 10 kΩ pull-down |
| GPIO 13 | SERVO_PWM | SG92R signal | Direct | 330 Ω series, 50 Hz |
| GPIO 12 | HORN_TRIG | Horn trigger | AO3400 → JQ6500 IO_1 | LOW/floating at boot |
| GPIO 16 | JQ_RX | JQ6500 serial RX | JQ6500 Pin 2 | Via 1 kΩ resistor |
| GPIO 4 | LIGHTS | Headlights | AO3400 → LEDs | Onboard flash + bumper LEDs |
| GPIO 2 | TAILLIGHTS | Brake/reverse | AO3400 → red LEDs | |
| GPIO 1 | U0TXD | UART flash | J7 header | Leave free |
| GPIO 3 | U0RXD | UART flash | J7 header | Leave free |
| GPIO 0 | IO0_BOOT | Flash mode | J7 header | Jumper to GND to flash |