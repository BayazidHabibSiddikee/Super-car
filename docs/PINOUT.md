# ESP32-CAM → KiCarrier PCB Netlist

Source: `super car.pdf` KiCad schematic section. AI-Thinker ESP32-CAM plugs into two 1×8 2.54 mm female headers on the top (F.Cu) of the carrier PCB.

## Header Pin Mapping

### Left Row (X = 4.57 mm, Y = 18.0 → 35.78 mm)

| Header Pin | ESP32-CAM GPIO | KiCad Net | Connected To | Net ID |
|------------|----------------|-----------|--------------|--------|
| L1 | 5V | +5V_ESP | Buck output + C1 470 µF | 4 |
| L2 | GND | GND | Ground plane | 1 |
| L3 | GPIO 15 | M1_REV | RZ7889 Pin 3 (FI) | 6 |
| L4 | GPIO 14 | M1_FWD | RZ7889 Pin 2 (BI) | 5 |
| L5 | GPIO 13 | SERVO_PWM | J3 servo signal (330 Ω) | 7 |
| L6 | GPIO 12 | HORN_TRIG | AO3400 gate → JQ6500 IO_1 | 8 |
| L7 | GPIO 4 | LIGHTS | AO3400 → headlights | 10 |
| L8 | GPIO 2 | TAILLIGHTS | AO3400 → taillights | 11 |

### Right Row (X = 27.43 mm, Y = 18.0 → 35.78 mm)

| Header Pin | ESP32-CAM GPIO | KiCad Net | Connected To | Net ID |
|------------|----------------|-----------|--------------|--------|
| R1 | GND | GND | Ground plane | 1 |
| R2 | GPIO 16 | JQ_RX | JQ6500 Pin 2 (via 1 kΩ) | 9 |
| R3 | GND | GND | Ground plane | 1 |
| R4 | — | NC | — | 0 |
| R5 | — | NC | — | 0 |
| R6 | — | NC | — | 0 |
| R7 | GPIO 1 | TX_PROG | J7 UART flash header | — |
| R8 | GPIO 3 | RX_PROG | J7 UART flash header | — |

## Connector Netlist

| RefDes | Connector | Pins | Net | Net ID |
|--------|-----------|------|-----|--------|
| J1 | JST-XH 2-pin | 1 | VBAT (+7.4V) | 2 |
| J1 | JST-XH 2-pin | 2 | GND | 1 |
| J2 | JST-XH 2-pin | 1 | M1_A (N20 +) | 12 |
| J2 | JST-XH 2-pin | 2 | M1_B (N20 −) | 13 |
| J3 | 1×3 header | 1 | GND | 1 |
| J3 | 1×3 header | 2 | +5V_MAIN | 3 |
| J3 | 1×3 header | 3 | SERVO_PWM | 7 |
| J4/J5 | JST-XH 2-pin | 1 | LIGHTS / TAILLIGHTS | 10/11 |
| J4/J5 | JST-XH 2-pin | 2 | GND | 1 |
| J6 | JST-XH 2-pin | 1 | SPK_P | 15 |
| J6 | JST-XH 2-pin | 2 | SPK_N | 16 |
| J7 | 1×4 header | 1–4 | TX, RX, GND, GPIO0 | programming |

## Peripheral IC Nets

| RefDes | IC | Pin | Net | Net ID |
|--------|----|-----|-----|--------|
| U1 | MP1584EN | VOUT | +5V_MAIN | 3 |
| U1 | MP1584EN | FB | R1/R2 divider | — |
| U2 | RZ7889 | VDD (Pins 5,6) | VBAT | 2 |
| U2 | RZ7889 | OUT1/OUT2 | M1_A / M1_B | 12/13 |
| Q1 | AO3400 | Gate | LIGHTS (via 100 Ω) | 10 |
| Q2 | AO3400 | Gate | TAILLIGHTS (via 100 Ω) | 11 |
| Q3 | AO3400 | Gate | HORN_TRIG (via 1 kΩ) | 8 |
| MOD2 | JQ6500-16P | Pin 2 RX | JQ_RX | 9 |
| MOD2 | JQ6500-16P | Pin 9 IO_1 | HORN_TRIG | 8 |
| MOD2 | JQ6500-16P | Pin 6 SPK_1 | SPK_P | 15 |
| MOD2 | JQ6500-16P | Pin 8 SPK_2 | SPK_N | 16 |
| MOD2 | JQ6500-16P | Pin 1 VCC | +5V_MAIN | 3 |
| MOD2 | JQ6500-16P | Pin 7/10 GND | GND | 1 |

## Nets Table (for KiCad)

```
1: GND
2: VBAT
3: +5V_MAIN
4: +5V_ESP
5: M1_FWD
6: M1_REV
7: SERVO_PWM
8: HORN_TRIG
9: JQ_RX
10: LIGHTS
11: TAILLIGHTS
12: M1_A
13: M1_B
14: AUDIO_MIX
15: SPK_P
16: SPK_N
```

## Boot-Pin Protection Checklist

- [ ] GPIO 12 (HORN_TRIG): 10 kΩ pull-down to GND on PCB; no external pull-up
- [ ] GPIO 14/15 (motor inputs): 10 kΩ pull-downs
- [ ] GPIO 2 (TAILLIGHTS): LOW at boot
- [ ] GPIO 0: jumper pad to GND on J7 header for flashing
- [ ] GPIO 1/3: reserved for UART, no motors/sensors attached