/*
  =======================
  Sensor HTTP Server (Arduino)
  =======================

  This sketch sets up a Wi-Fi-enabled HTTP server that listens on port 80 
  and serves sensor measurements based on query parameters.

  Supported endpoint:
    GET /measurements?type=<sensor_type>

  Supported sensor types:
    - nitrogen
    - phosphorous
    - potassium

  Example endpoint:
    http://<device-ip>/measurements?type=temperature

  The server responds with a JSON object:
    {
      "value": <measured_value>
    }

  Wi-Fi credentials and static IP must be configured before upload.
*/

#include <WiFiNINA.h>
#include <Adafruit_ADS1X15.h>
#include <SoftwareSerial.h>
#include <Wire.h>

// WiFi Credentials
const char ssid[] = "ssid";
const char pass[] = "pw";
int status = WL_IDLE_STATUS;

// Static IP configuration
IPAddress local_IP(1, 1, 1, 1);
IPAddress gateway(1, 1, 1, 1);
IPAddress subnet(255, 255, 255, 192);
IPAddress dns(8, 8, 8, 8);

// WiFi Server
WiFiServer server(80);

// RS485 Pins
#define RE 8
#define DE 7

// Modbus RTU requests
const byte nitro[] = {0x01, 0x03, 0x00, 0x1e, 0x00, 0x01, 0xe4, 0x0c};
const byte phos[]  = {0x01, 0x03, 0x00, 0x1f, 0x00, 0x01, 0xb5, 0xcc};
const byte pota[]  = {0x01, 0x03, 0x00, 0x20, 0x00, 0x01, 0x85, 0xc0};

byte values[11];
SoftwareSerial mod(2, 3);

// ===== Sensor Functions ===== //
byte readNPK(const byte* command) {
  digitalWrite(DE, HIGH);
  digitalWrite(RE, HIGH);
  delay(10);

  byte result = 0;
  if (mod.write(command, 8) == 8) {
    digitalWrite(DE, LOW);
    digitalWrite(RE, LOW);
    delay(10);
    for (byte i = 0; i < 7; i++) {
      while (!mod.available());
      values[i] = mod.read();
    }
    result = values[4];
  }
  return result;
}

byte nitrogen()    { return readNPK(nitro); }
byte phosphorous() { return readNPK(phos); }
byte potassium()   { return readNPK(pota); }

// ===== HTTP Response ===== //
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

// ===== WiFi Functions ===== //
void connectToWifi() {
  if (WiFi.status() == WL_NO_MODULE) {
    Serial.println("WLAN-Module not found!");
    while (true);
  }

  WiFi.config(local_IP, gateway, subnet);
  while (status != WL_CONNECTED) {
    Serial.print("Connecting to: ");
    Serial.println(ssid);
    status = WiFi.begin(ssid, pass);
    delay(10000);
  }

  Serial.println("WiFi connected!");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  server.begin();
}

void reconnectToWiFi() {
  Serial.println("Reconnecting to WiFi...");
  WiFi.disconnect();
  WiFi.begin(ssid, pass);

  unsigned long startTime = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - startTime < 30000) {
    Serial.print(".");
    delay(1000);
  }

  if (WiFi.status() == WL_CONNECTED)
    Serial.println("\nWiFi Reconnected!");
  else
    Serial.println("\nFailed to reconnect.");
}

// ===== Request Helpers ===== //
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

  if (type == "nitrogen") {
    byte val = nitrogen();
    json = "{\"sensor\":\"nitrogen\",\"value\":" + String(val) + "}";
    sendJSONResponse(client, json);
  } else if (type == "phosphorous") {
    byte val = phosphorous();
    json = "{\"sensor\":\"phosphorous\",\"value\":" + String(val) + "}";
    sendJSONResponse(client, json);
  } else if (type == "potassium") {
    byte val = potassium();
    json = "{\"sensor\":\"potassium\",\"value\":" + String(val) + "}";
    sendJSONResponse(client, json);
  } else {
    send404(client);
  }
}

// ===== Setup and Loop ===== //
void setup() {
  Serial.begin(9600);
  mod.begin(9600);
  pinMode(RE, OUTPUT);
  pinMode(DE, OUTPUT);

  connectToWifi();
}

void loop() {
  if (WiFi.status() != WL_CONNECTED)
    reconnectToWiFi();

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
