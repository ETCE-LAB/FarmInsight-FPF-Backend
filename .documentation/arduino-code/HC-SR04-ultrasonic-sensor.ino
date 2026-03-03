/*
  =======================
  Sensor HTTP Server (Arduino)
  =======================

  Supported endpoint:
    GET /measurements?type=<sensor_type>

  Added sensor type:
    - distance  (HC-SR04, returns cm)

  Example:
    http://<device-ip>/measurements?type=distance

  Response:
    {
      "sensor": "distance",
      "value": 42.13
    }
*/

#include <WiFiNINA.h>

// WLAN-Access data
const char* ssid = "ssid";
const char* password = "pw";

// Manual static IP config
//IPAddress local_IP(1, 1, 1, 1);
IPAddress gateway(1, 1, 1, 1);
IPAddress subnet(255, 255, 255, 255);


// Wi-Fi server object
WiFiServer server(80);

// WiFi status
int status = WL_IDLE_STATUS;

// ========== HC-SR04 Pins ========== //
const int trigPin = 9;
const int echoPin = 10;

// ========== Sensor Functions ========== //

// Single measurement in cm. Returns NAN on timeout/invalid.
float measureDistanceOnceCM() {
  // Trigger pulse
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);

  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  // pulseIn timeout in microseconds (e.g., 30ms ~ ~5m distance max)
  unsigned long duration = pulseIn(echoPin, HIGH, 30000UL);

  if (duration == 0) {
    return NAN; // timeout => no echo
  }

  // distance (cm) = (duration_us * speed_of_sound_cm_per_us) / 2
  // speed of sound ~ 343 m/s => 0.0343 cm/us
  float distance = (float)duration * 0.0343f / 2.0f;

  // basic sanity range for HC-SR04
  if (distance < 2.0f || distance > 400.0f) {
    return NAN;
  }

  return distance;
}

// Measure 3 times, average valid readings. If none valid => NAN.
float measureDistanceAvgCM(int n = 3) {
  float sum = 0.0f;
  int valid = 0;

  for (int i = 0; i < n; i++) {
    float d = measureDistanceOnceCM();
    if (!isnan(d)) {
      sum += d;
      valid++;
    }
    delay(60); // short pause between pings (avoid crosstalk)
  }

  if (valid == 0) return NAN;
  return sum / valid;
}
float clampFloat(float x, float lo, float hi) {
  if (x < lo) return lo;
  if (x > hi) return hi;
  return x;
}

// d_cm = measured distance sensor -> water surface
float distanceToPercent(float d_cm) {
  const float SENSOR_HEIGHT_CM = 40.0;  // sensor above bottom
  const float MAX_WATER_CM     = 30.0;  // max water height

  float waterHeight = SENSOR_HEIGHT_CM - d_cm;           // h = 40 - d
  waterHeight = clampFloat(waterHeight, 0.0, MAX_WATER_CM);

  float pct = (waterHeight / MAX_WATER_CM) * 100.0;
  return clampFloat(pct, 0.0, 100.0);
}

// ========== HTTP Response Helpers ========== //
void sendJSONResponse(WiFiClient& client, String json) {
  client.println("HTTP/1.1 200 OK");
  client.println("Content-Type: application/json");
  client.println("Connection: close");
  client.println();
  client.println(json);
}

void send404(WiFiClient& client) {
  client.println("HTTP/1.1 404 Not Found");
  client.println("Content-Type: text/plain");
  client.println("Connection: close");
  client.println();
  client.println("404 Not Found");
}

// Optional: send a 500 if sensor failed (still JSON)
void send500(WiFiClient& client, String msg) {
  client.println("HTTP/1.1 500 Internal Server Error");
  client.println("Content-Type: application/json");
  client.println("Connection: close");
  client.println();
  client.println("{\"error\":\"" + msg + "\"}");
}

// ========== Wi-Fi Functions ========== //
void connectToWifi() {

  if (WiFi.status() == WL_NO_MODULE) {
    Serial.println("WLAN-Module not found!");
    while (true);
  }

  //WiFi.config(local_IP, gateway, subnet, dns);

  while (status != WL_CONNECTED) {
    Serial.print("Verbinden mit: ");
    Serial.println(ssid);
    status = WiFi.begin(ssid, password);
    delay(10000); // Delay for retry
  }

  Serial.println("WLAN verbunden!");
  Serial.print("IP-Adresse: ");
  Serial.println(WiFi.localIP());

  server.begin();
}

void reconnectToWiFi() {
  Serial.println("Reconnecting to WiFi...");
  WiFi.disconnect();
  WiFi.begin(ssid, password);

  unsigned long startTime = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - startTime < 30000) {
    Serial.print(".");
    delay(1000);
  }

  Serial.println(WiFi.status() == WL_CONNECTED ? "\nWiFi Reconnected!" : "\nFailed to reconnect.");
}

// ========== Request Handling ========== //
String getQueryParam(String request, String param) {
  int idx = request.indexOf(param + "=");
  if (idx == -1) return "";

  int start = idx + param.length() + 1;
  int end = request.indexOf('&', start);
  if (end == -1) end = request.indexOf(' ', start);

  return request.substring(start, end);
}

void handleMeasurementRequest(WiFiClient& client, String request) {
  String type = getQueryParam(request, "type");
  String json;

  if (type == "distance") {
    float d = measureDistanceAvgCM(3);
    float pct = distanceToPercent(d);

    if (isnan(d)) {
      send500(client, "distance_measurement_failed");
      return;
    }

    json = "{\"sensor\":\"water_level\",\"value\":" + String(pct, 1) + "}";
    sendJSONResponse(client, json);

  } else {
    send404(client);
  }
}

void setup() {
  Serial.begin(9600);

  // HC-SR04 pin setup
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  connectToWifi();
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) reconnectToWiFi();

  WiFiClient client = server.available();
  if (client) {
    while (client.connected() && !client.available()) {
      delay(1);
    }

    String request = client.readStringUntil('\r');
    request.trim();
    Serial.println("Request: " + request);

    if (request.startsWith("GET /measurements")) {
      handleMeasurementRequest(client, request);
    } else {
      send404(client);
    }

    client.stop();
  }
}
