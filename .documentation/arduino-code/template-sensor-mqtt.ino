#include <WiFiNINA.h>
#include <PubSubClient.h>

// WLAN Access
const char ssid[] = "ssid";
const char pass[] = "pw";

// MQTT Broker config
const char* mqtt_server = "192.168.1.100"; // use IP or hostname
const int mqtt_port = 1883;

// Sensor configuration
const char* sensor_uuid = "your-sensor-uuid-here";  // replace with actual UUID
const float delta_threshold = 0.5;                  // minimum change to trigger MQTT publish

float lastTemperature = NAN;

// IP Config
IPAddress local_IP(1, 1, 1, 1);
IPAddress gateway(1, 1, 1, 1);
IPAddress subnet(255, 255, 255, 192);
IPAddress dns(8, 8, 8, 8);

WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);
WiFiServer server(80);

// ========== Sensor Logic ==========
float measureTemperature() {
  return 23.00 + random(-10, 10) * 0.1;  // Simulated data for now
}

float measurePH() {
  return 6.5;
}

// ========== MQTT Logic ==========
void mqttReconnect() {
  while (!mqttClient.connected()) {
    Serial.print("[MQTT] Attempting connection...");
    String clientId = "arduino-" + String(sensor_uuid);

    if (mqttClient.connect(clientId.c_str())) {
      Serial.println("connected");
      // No subscriptions needed for now
    } else {
      Serial.print("failed, rc=");
      Serial.print(mqttClient.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void publishIfDeltaExceeded(float newValue) {
  if (isnan(lastTemperature) || abs(newValue - lastTemperature) >= delta_threshold) {
    lastTemperature = newValue;

    String topic = "sensor/" + String(sensor_uuid);
    String payload = "{\"measuredAt\":\"" + String(millis()) + "\",\"value\":" + String(newValue, 2) + "}";

    mqttClient.publish(topic.c_str(), payload.c_str());
    Serial.println("[MQTT] Published: " + payload);
  }
}

// ========== HTTP Logic ==========
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

  if (type == "temperature") {
    float temp = measureTemperature();
    json = "{\"sensor\":\"temperature\",\"value\":" + String(temp, 2) + "}";
    sendJSONResponse(client, json);
  } else if (type == "ph") {
    float ph = measurePH();
    json = "{\"sensor\":\"ph\",\"value\":" + String(ph, 2) + "}";
    sendJSONResponse(client, json);
  } else {
    send404(client);
  }
}

// ========== WiFi ==========
void connectToWifi() {
  if (WiFi.status() == WL_NO_MODULE) {
    Serial.println("WiFi module not found");
    while (true);
  }

  WiFi.config(local_IP, gateway, subnet, dns);
  while (WiFi.begin(ssid, pass) != WL_CONNECTED) {
    Serial.println("Connecting to WiFi...");
    delay(10000);
  }

  Serial.println("WiFi connected. IP address: " + WiFi.localIP().toString());
  server.begin();
}

// ========== Setup and Loop ==========
void setup() {
  Serial.begin(9600);
  connectToWifi();

  mqttClient.setServer(mqtt_server, mqtt_port);
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    connectToWifi();
  }

  if (!mqttClient.connected()) {
    mqttReconnect();
  }
  mqttClient.loop();

  // Periodically measure & publish if changed
  static unsigned long lastMeasurementTime = 0;
  const unsigned long interval = 5000;

  if (millis() - lastMeasurementTime > interval) {
    lastMeasurementTime = millis();
    float newTemp = measureTemperature();
    publishIfDeltaExceeded(newTemp);
  }

  // Handle HTTP
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
