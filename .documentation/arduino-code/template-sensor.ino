/*
  =======================
  Sensor HTTP Server (Arduino)
  =======================

  This sketch sets up a Wi-Fi-enabled HTTP server that listens on port 80
  and serves sensor measurements based on query parameters.

  Supported endpoint:
    GET /measurements?type=<sensor_type>

  Example sensor types:
    - temperature
    - ph

  Example endpoint:
    http://<device-ip>/measurements?type=temperature

  The server responds with a JSON object:
    {
      "sensor": <sensor_name>,
      "value": <measured_value>
    }

  Wi-Fi credentials and static IP must be configured before upload.
*/


#include <WiFiNINA.h>
#include <Adafruit_ADS1X15.h>

// WLAN-Access data
const char ssid[] = "ssid";
const char pass[] = "pw";

// Manual static IP config
IPAddress local_IP(1, 1, 1, 1);
IPAddress gateway(1, 1, 1, 1);
IPAddress subnet(255, 255, 255, 192);
IPAddress dns(8, 8, 8, 8);

// Wi-Fi server object
WiFiServer server(80);


// ========== Sensor Placeholder Functions ========== //
float measureTemperature() {
  // Replace with actual sensor logic
  return 23.45;
}

float measurePH() {
  // Replace with actual sensor logic
  return 6.7;
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

// ========== Wi-Fi Functions ========== //
void connectToWifi(){

  if (WiFi.status() == WL_NO_MODULE) {
    Serial.println("WLAN-Module not found!");
    while (true);
  }

  WiFi.config(local_IP, gateway, subnet);

  while (status != WL_CONNECTED) {
    Serial.print("Verbinden mit: ");
    Serial.println(ssid);
    status = WiFi.begin(ssid, pass);
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
  WiFi.begin(ssid, pass);

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

// TODO: Edit this function for your sensors
void handleMeasurementRequest(WiFiClient& client, String request) {
  String type = getQueryParam(request, "type");
  String json;

  if (type == "temperature") {
    json = "{\"sensor\":\"temperature\",\"value\":" + String(measureTemperature(), 2) + "}";
    sendJSONResponse(client, json);

  } else if (type == "ph") {
    json = "{\"sensor\":\"ph\",\"value\":" + String(measurePH(), 2) + "}";
    sendJSONResponse(client, json);

  } else {
    send404(client);
  }
}

void setup() {
  Serial.begin(9600);
  connectToWifi();

  // TODO: Optionally add setup sensor logic

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