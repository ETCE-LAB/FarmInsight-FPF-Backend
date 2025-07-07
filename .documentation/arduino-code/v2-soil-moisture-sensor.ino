#include <WiFiNINA.h>

// Wi-Fi credentials
char ssid[] = "ssid";         // Netzwerkname (SSID)
char pass[] = "pw";     // Passwort

// Static IP setup (adjust as needed)
IPAddress local_IP(1, 1, 1, 1);
IPAddress gateway(1, 1, 1, 1);
IPAddress subnet(255, 255, 255, 0);
IPAddress dns(8, 8, 8, 8);

// Wi-Fi server
WiFiServer server(80);

// Track WiFi status
int status = WL_IDLE_STATUS;

// ========== Sensor Pin ==========
const int SOIL_SENSOR_PIN = A0;

// ========== Sensor Functions ==========
float measureSoilMoisture() {
  int sensorValue = analogRead(SOIL_SENSOR_PIN);

  // Adjust these values after testing in water
  const int dryValue = 30;    // value you saw when dry
  const int wetValue = 800;   // guess for now, test in water later

  float percentage = map(sensorValue, dryValue, wetValue, 0, 100);
  percentage = constrain(percentage, 0, 100);
  return percentage;
}
// ========== HTTP Response Helpers ==========
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

// ========== Wi-Fi Functions ==========
void connectToWifi() {
  if (WiFi.status() == WL_NO_MODULE) {
    Serial.println("WiFi module not found");
    while (true);
  }

  WiFi.config(local_IP, gateway, subnet, dns);
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
  Serial.println(WiFi.status() == WL_CONNECTED ? "\nWiFi Reconnected!" : "\nFailed to reconnect.");
}

// ========== Request Handling ==========
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

  if (type == "soil") {
    json = "{\"sensor\":\"soil\",\"value\":" + String(measureSoilMoisture(), 1) + "}";
    sendJSONResponse(client, json);
  } else {
    send404(client);
  }
}

void setup() {
  Serial.begin(9600);
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
