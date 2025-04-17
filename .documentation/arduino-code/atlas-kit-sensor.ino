#include <WiFi.h>
#include <iot_cmd.h>
#include <Ezo_i2c_util.h>
#include <Ezo_i2c.h> //include the EZO I2C library from https://github.com/Atlas-Scientific/Ezo_I2c_lib
#include <Wire.h>

// Replace with your network credentials
const char* ssid = "ssid";
const char* password = "pw";

// Static IP settings (optional)
IPAddress local_IP(1, 1, 1, 1);
IPAddress gateway(1, 1, 1, 1);
IPAddress subnet(255, 255, 255, 192);

// Enable pins (v1.5 kit)
const int EN_PH = 12;
const int EN_EC = 27;
const int EN_RTD = 15;
const int EN_AUX = 33;

// WiFi server
WiFiServer server(80);

// Atlas I2C sensor objects
Ezo_board PH(99, "PH");
Ezo_board EC(100, "EC");
Ezo_board RTD(102, "RTD");

void setup() {
  Serial.begin(115200);
  delay(3000);  // Give USB time to initialize

  Serial.println("Booting...");
  Serial.println("Enabling sensors...");

  pinMode(EN_PH, OUTPUT);
  pinMode(EN_EC, OUTPUT);
  pinMode(EN_RTD, OUTPUT);
  pinMode(EN_AUX, OUTPUT);

  digitalWrite(EN_PH, LOW);
  digitalWrite(EN_EC, LOW);
  digitalWrite(EN_RTD, HIGH);
  digitalWrite(EN_AUX, LOW);

  Wire.begin();
  Serial.println("I2C initialized.");

  Serial.print("Connecting to WiFi: ");
  Serial.println(ssid);

  WiFi.config(local_IP, gateway, subnet);
  WiFi.begin(ssid, password);

  unsigned long wifiStart = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - wifiStart < 15000) {
    delay(500);
    Serial.print(".");
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✅ WiFi connected!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n❌ Failed to connect to WiFi.");
  }

  server.begin();
  Serial.println("HTTP server started.");
}

// Send HTTP JSON response
void sendJSONResponse(WiFiClient& client, const String& json) {
  Serial.println("✅ Sending JSON: " + json);
  client.println("HTTP/1.1 200 OK");
  client.println("Content-Type: application/json");
  client.println("Connection: close");
  client.println();
  client.println(json);
}

// Send 404 response
void send404(WiFiClient& client) {
  Serial.println("❌ Sending 404 - invalid or failed request");
  client.println("HTTP/1.1 404 Not Found");
  client.println("Content-Type: text/plain");
  client.println("Connection: close");
  client.println();
  client.println("404 Not Found");
}

// Simple query param parser
String getQueryParam(const String& request, const String& param) {
  int idx = request.indexOf(param + "=");
  if (idx == -1) return "";

  int start = idx + param.length() + 1;
  int end = request.indexOf('&', start);
  if (end == -1) end = request.indexOf(' ', start);
  return request.substring(start, end);
}

// Generic measurement wrapper
float getSensorReading(Ezo_board& sensor) {
  Serial.println(String("Sending read command to ") + sensor.get_name());
  sensor.send_read_cmd();
  delay(1000);  // Wait for sensor response
  int result = sensor.receive_read_cmd();
  if (result == Ezo_board::SUCCESS) {
    float val = sensor.get_last_received_reading();
    Serial.println(String("Received value from ") + sensor.get_name() + ": " + String(val, 2));
    return val;
  } else {
    Serial.println(String("❌ Failed to read from ") + sensor.get_name() + " (code " + String(result) + ")");
    return NAN;
  }
}

// Handle /measurements?type=...
void handleMeasurementRequest(WiFiClient& client, const String& request) {
  String type = getQueryParam(request, "type");
  Serial.println("Parsed type: " + type);

  float value = NAN;

  if (type == "temperature") {
    value = getSensorReading(RTD);
  } else if (type == "ph") {
    value = getSensorReading(PH);
  } else if (type == "ec") {
    value = getSensorReading(EC);
  }

  if (!isnan(value)) {
    String json = "{\"sensor\":\"" + type + "\",\"value\":" + String(value, 2) + "}";
    sendJSONResponse(client, json);
  } else {
    send404(client);
  }
}

void loop() {
  WiFiClient client = server.available();
  if (client) {
    Serial.println("📡 Client connected");

    while (client.connected() && !client.available()) {
      delay(1);
    }

    String request = client.readStringUntil('\r');
    request.trim();
    Serial.println("📥 HTTP Request: " + request);

    if (request.startsWith("GET /measurements")) {
      handleMeasurementRequest(client, request);
    } else {
      send404(client);
    }

    client.stop();
    Serial.println("🔌 Client disconnected\n");
  }
}

