/*
 * FPV_Car_DFPlayer_AutoResume.ino
 * Supercar — ESP32-CAM FPV RC Car Firmware
 * Source: super car.pdf (final firmware iteration)
 *
 * Features:
 *  - Port 80 AsyncWebSocket: T/S/H/L/V/M control packets
 *  - Port 81 dedicated MJPEG camera stream
 *  - LEDC Timer 1 & 2 for motor/servo PWM (Timer 0 reserved for OV2640 XCLK)
 *  - UART2 on GPIO 16 -> DFPlayer Mini / JQ6500-16P sound module
 *  - Horn on GPIO 12 with 1.5 s auto-resume background music
 *  - 250 ms Wi-Fi failsafe: stops wheels if control drops
 *
 * Flash: AI-Thinker ESP32-CAM, GPIO 0 -> GND during upload, 115200 baud
 */

#include "esp_camera.h"
#include "esp_http_server.h"
#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <ArduinoJson.h>

// ==========================================
// 1. HARDWARE PIN DEFINITIONS (AI-THINKER)
// ==========================================
#define PIN_M1_FWD     14   // RZ7889 BI (Rear Motor Forward)
#define PIN_M1_REV     15   // RZ7889 FI (Rear Motor Reverse)
#define PIN_SERVO      13   // SG92R Steering Servo Signal
#define PIN_HORN_TRIG 12    // AO3400 MOSFET -> DFPlayer IO_1 (Hardware Horn Backup)
#define PIN_DF_TX      16   // HardwareSerial(2) TX -> 1k Resistor -> DFPlayer RX
#define PIN_LIGHTS      4   // Front Headlights + Onboard Flash LED
#define PIN_TAILLIGHT   2   // Rear Brake / Reverse Taillights

// AI-Thinker OV2640 Camera Pinout
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

// ==========================================
// 2. PWM & SERVO CALIBRATION
// ==========================================
const int PWM_FREQ_MOTOR = 1000; // 1 kHz PWM for RZ7889
const int PWM_FREQ_SERVO = 50;    // 50 Hz PWM for SG92R

// 16-bit duty values for 50 Hz (20 ms period): 1.0 ms = 3277, 1.5 ms = 4915, 2.0 ms = 6553
const int SERVO_MIN_DUTY = 3400; // Full Left limit (prevents C-hub binding)
const int SERVO_MAX_DUTY = 6400; // Full Right limit

// ==========================================
// 3. SERVER, AUDIO & AUTO-RESUME STATE
// ==========================================
AsyncWebServer server(80);
AsyncWebSocket ws("/ws");
httpd_handle_t stream_httpd = NULL;

HardwareSerial dfSerial(2);                  // UART2 TX-only on GPIO 16

unsigned long lastPacketTime = 0;
const unsigned long FAILSAFE_TIMEOUT_MS = 250;

int currentVolume = 22;                // 0 to 30
int currentMusicTrack = 3;             // Music tracks start at 0003.mp3
const int MAX_TRACKS = 10;             // Update to match total MP3s on SD card

bool isMusicPlaying = false;           // User's intended music playback state
bool lastHornState = false;
bool pendingMusicResume = false;
unsigned long sfxEndTimestamp = 0;
const unsigned long MUSIC_RESUME_DELAY_MS = 1500; // 1.5 seconds after horn stops

// ==========================================
// 4. DFPLAYER MINI BINARY UART DRIVER
// ==========================================
void sendDFCommand(uint8_t cmd, uint8_t param1, uint8_t param2) {
  uint16_t checksum = -(0xFF + 0x06 + cmd + 0x00 + param1 + param2);
  uint8_t packet[10] = {
     0x7E, 0xFF, 0x06, cmd, 0x00,
     param1, param2,
     (uint8_t)(checksum >> 8), (uint8_t)(checksum & 0xFF),
     0xEF
  };
  dfSerial.write(packet, 10);
}

void dfPlayTrack(uint16_t trackNum) {
  // Command 0x12 plays /mp3/0001.mp3 .. /mp3/9999.mp3
  sendDFCommand(0x12, (uint8_t)(trackNum >> 8), (uint8_t)(trackNum & 0xFF));
}

void dfSetVolume(uint8_t vol) {
  vol = constrain(vol, 0, 30);
  currentVolume = vol;
  sendDFCommand(0x06, 0x00, vol);
}

void dfPause() {
  sendDFCommand(0x0E, 0x00, 0x00);
}

// ==========================================
// 5. MOTOR & STEERING ACTUATORS
// ==========================================
void setMotorSpeed(int speed) {
  speed = constrain(speed, -255, 255);
  if (speed > 12) {
    ledcWrite(PIN_M1_FWD, speed);
    ledcWrite(PIN_M1_REV, 0);
    digitalWrite(PIN_TAILLIGHT, LOW);
  } else if (speed < -12) {
    ledcWrite(PIN_M1_FWD, 0);
    ledcWrite(PIN_M1_REV, abs(speed));
    digitalWrite(PIN_TAILLIGHT, HIGH); // Reverse light ON
  } else {
    ledcWrite(PIN_M1_FWD, 0);
    ledcWrite(PIN_M1_REV, 0);
    digitalWrite(PIN_TAILLIGHT, HIGH); // Brake light ON when stopped
  }
}

void setSteeringAngle(int angle) {
  angle = constrain(angle, -45, 45);
  uint32_t duty = map(angle, -45, 45, SERVO_MIN_DUTY, SERVO_MAX_DUTY);
  ledcWrite(PIN_SERVO, duty);
}

// ==========================================
// 6. WEBSOCKET PACKET HANDLER (PORT 80)
// Supported JSON keys:
//    "T": -255..255 (Throttle)
//    "S": -45..45    (Steering angle)
//    "H": 0 or 1     (Horn trigger)
//    "L": 0 or 1     (Headlights toggle)
//    "V": 0..30      (Speaker Volume)
//    "M": "play" | "pause" | "next" | "prev" | "engine"
// ==========================================
void onWsEvent(AsyncWebSocket *server, AsyncWebSocketClient *client,
               AwsEventType type, void *arg, uint8_t *data, size_t len) {
  if (type == WS_EVT_DATA) {
    AwsFrameInfo *info = (AwsFrameInfo *)arg;
    if (info->final && info->index == 0 && info->len == len && info->opcode == WS_TEXT) {
      JsonDocument doc;
      DeserializationError err = deserializeJson(doc, data, len);
      if (!err) {
        lastPacketTime = millis();

        // 1. Driving Controls
        if (!doc["T"].isNull()) setMotorSpeed(doc["T"].as<int>());
        if (!doc["S"].isNull()) setSteeringAngle(doc["S"].as<int>());

        // 2. Headlights
        if (!doc["L"].isNull()) {
          digitalWrite(PIN_LIGHTS, doc["L"].as<int>() ? HIGH : LOW);
        }

        // 3. Horn Trigger with 1.5s Auto-Resume Scheduling
        if (!doc["H"].isNull()) {
          bool hornNow = (doc["H"].as<int>() == 1);

          if (hornNow && !lastHornState) {
            // Horn just pressed: play horn track and cancel any pending resume
            dfPlayTrack(1); // /mp3/0001.mp3 (Car Horn)
            pendingMusicResume = false;
          } else if (!hornNow && lastHornState) {
            // Horn just released: schedule music resume 1.5 s from now if music was active
            if (isMusicPlaying) {
              sfxEndTimestamp = millis();
              pendingMusicResume = true;
            }
          }
          lastHornState = hornNow;
        }

        // 4. Volume Control
        if (!doc["V"].isNull()) {
          dfSetVolume(doc["V"].as<int>());
        }

        // 5. Music & Engine Sound Commands
        if (!doc["M"].isNull()) {
          String cmd = doc["M"].as<String>();
          if (cmd == "play") {
            isMusicPlaying = true;
            pendingMusicResume = false;
            dfPlayTrack(currentMusicTrack);
          } else if (cmd == "pause") {
            isMusicPlaying = false;
            pendingMusicResume = false;
            dfPause();
          } else if (cmd == "next") {
            currentMusicTrack++;
            if (currentMusicTrack > MAX_TRACKS) currentMusicTrack = 3;
            isMusicPlaying = true;
            pendingMusicResume = false;
            dfPlayTrack(currentMusicTrack);
          } else if (cmd == "prev") {
            currentMusicTrack--;
            if (currentMusicTrack < 3) currentMusicTrack = MAX_TRACKS;
            isMusicPlaying = true;
            pendingMusicResume = false;
            dfPlayTrack(currentMusicTrack);
          } else if (cmd == "engine") {
            dfPlayTrack(2); // /mp3/0002.mp3 (Engine Rev)
            if (isMusicPlaying) {
              sfxEndTimestamp = millis();
              pendingMusicResume = true;
            }
          }
        }
      }
    }
  } else if (type == WS_EVT_DISCONNECT) {
    setMotorSpeed(0);
    setSteeringAngle(0);
    if (lastHornState && isMusicPlaying) {
      sfxEndTimestamp = millis();
      pendingMusicResume = true;
    }
    lastHornState = false;
  }
}

// ==========================================
// 7. DEDICATED MJPEG STREAM SERVER (PORT 81)
// ==========================================
static esp_err_t stream_handler(httpd_req_t *req) {
  camera_fb_t *fb = NULL;
  esp_err_t res = ESP_OK;
  char part_buf[64];

  res = httpd_resp_set_type(req, "multipart/x-mixed-replace;boundary=frame");
  if (res != ESP_OK) return res;

  while (true) {
    fb = esp_camera_fb_get();
    if (!fb) {
      res = ESP_FAIL;
    } else {
      size_t hlen = snprintf(part_buf, 64,
        "Content-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n", fb->len);
      res = httpd_resp_send_chunk(req, "--frame\r\n", 9);
      if (res == ESP_OK) res = httpd_resp_send_chunk(req, part_buf, hlen);
      if (res == ESP_OK) res = httpd_resp_send_chunk(req, (const char *)fb->buf, fb->len);
      if (res == ESP_OK) res = httpd_resp_send_chunk(req, "\r\n", 2);
      esp_camera_fb_return(fb);
    }
    if (res != ESP_OK) break;
  }
  return res;
}

void startCameraServer() {
  httpd_config_t config = HTTPD_DEFAULT_CONFIG();
  config.server_port = 81;
  httpd_uri_t stream_uri = {
     .uri = "/stream", .method = HTTP_GET, .handler = stream_handler, .user_ctx = NULL
  };
  if (httpd_start(&stream_httpd, &config) == ESP_OK) {
     httpd_register_uri_handler(stream_httpd, &stream_uri);
  }
}

// ==========================================
// 8. SETUP & NON-BLOCKING MAIN LOOP
// ==========================================
void setup() {
  Serial.begin(115200);

  // Safe Boot State for GPIOs
  pinMode(PIN_HORN_TRIG, OUTPUT);
  pinMode(PIN_LIGHTS, OUTPUT);
  pinMode(PIN_TAILLIGHT, OUTPUT);
  digitalWrite(PIN_HORN_TRIG, LOW);
  digitalWrite(PIN_LIGHTS, LOW);
  digitalWrite(PIN_TAILLIGHT, HIGH);

  // Initialize DFPlayer UART2 (RX = -1 unused, TX = GPIO 16)
  dfSerial.begin(9600, SERIAL_8N1, -1, PIN_DF_TX);
  delay(500); // Wait for DFPlayer Mini cold boot
  dfSetVolume(currentVolume);

  // Initialize Camera FIRST (Claims LEDC Timer 0 / Channel 0)
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer    = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;    config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;    config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;    config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;    config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = FRAMESIZE_VGA;      // 640x480 smooth FPV stream
  config.jpeg_quality = 14;
  config.fb_count = 2;
  config.grab_mode = CAMERA_GRAB_LATEST;

  if (esp_camera_init(&config) != ESP_OK) {
    Serial.println("Camera init failed!");
  }

  // Attach Motor & Servo PWM AFTER Camera (ESP32 Arduino Core v3.x API)
  ledcAttach(PIN_M1_FWD, PWM_FREQ_MOTOR, 8);
  ledcAttach(PIN_M1_REV, PWM_FREQ_MOTOR, 8);
  ledcAttach(PIN_SERVO, PWM_FREQ_SERVO, 16);

  setMotorSpeed(0);
  setSteeringAngle(0);

  // Start Wi-Fi SoftAP
  WiFi.softAP("RC_FPV_CAR", "12345678");
  WiFi.setSleep(false); // Disable Wi-Fi modem sleep for instant steering response

  ws.onEvent(onWsEvent);
  server.addHandler(&ws);
  server.begin();
  startCameraServer();
}

void loop() {
  ws.cleanupClients();

  // 1. Auto-Resume Background Music 1.5 s After Horn Release
  if (pendingMusicResume && !lastHornState) {
    if (millis() - sfxEndTimestamp >= MUSIC_RESUME_DELAY_MS) {
      pendingMusicResume = false;
      if (isMusicPlaying) {
        dfPlayTrack(currentMusicTrack);
      }
    }
  }

  // 2. Motor Failsafe (Stops wheels if Wi-Fi drops > 250 ms)
  //    Music continues playing smoothly without interruption
  if (millis() - lastPacketTime > FAILSAFE_TIMEOUT_MS) {
    setMotorSpeed(0);
    if (lastHornState && isMusicPlaying) {
      sfxEndTimestamp = millis();
      pendingMusicResume = true;
    }
    lastHornState = false;
  }

  delay(10);
}