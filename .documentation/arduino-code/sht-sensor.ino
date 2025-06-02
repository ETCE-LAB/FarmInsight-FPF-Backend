#include <Wire.h>
#include <WiFiNINA.h>
#include <Adafruit_SHT31.h>

// WiFi Credentials
const char ssid[] = "ssid";
const char pass[] = "pw";

// Static IP Configuration (Optional)
IPAddress local_IP(1, 1, 1, 1);     // IP-Adresse des Arduino 214
IPAddress gateway(1, 1, 1, 1);        // Gateway (Router-IP)
IPAddress subnet(255, 255, 255, 192);       // Subnetzmaske
IPAddress dns(8, 8, 8, 8);                // DNS-Server (Google DNS als Beispiel)

int status = WL_IDLE_STATUS; // WiFi Status
Adafruit_SHT31 sht31 = Adafruit_SHT31();
WiFiServer server(80);

// Function to read sensor data
String getSensorData(int type) {
  float value = (type == 1) ? sht31.readTemperature() : sht31.readHumidity();
  return "{\"value\": " + String(value, 2) + "}";
}

// Send HTTP Response
void sendResponse(WiFiClient &client, String data) {
  client.println("HTTP/1.1 200 OK");
  client.println("Content-Type: application/json");
  client.println("Connection: close");
  client.println();
  client.println(data);
}

// WiFi Reconnection
void checkWiFiConnection() {
  status = WiFi.status();
  if (status == WL_CONNECTED) return;
  
  Serial.println("Reconnecting to WiFi...");
  while (status != WL_CONNECTED) {
    status = WiFi.begin(ssid, pass);
    delay(10000);
  }
  if (!server) {
    server.begin();
  }
  
  Serial.println("WiFi Reconnected!");
}

// Setup Function
void setup() {
  Serial.begin(9600);
  Wire.begin();

  WiFi.config(local_IP, gateway, subnet);
  checkWiFiConnection();
  Serial.println("WiFi Connected! IP: " + WiFi.localIP().toString());

  while(!sht31.begin(0x44)) {
    Serial.println("SHT could not be initialized, please check cabels and connection!");
    delay(2000);
  }
}

// Main Loop
void loop() {
  checkWiFiConnection();

  WiFiClient client = server.available();
  if (client) {
	Serial.println("New client connected");
  
    while (client.connected() && !client.available()) delay(1);
    String request = client.readStringUntil('\r');
	Serial.println("Request: " + request);
  
    if (request.startsWith("GET /measurements/humidity")) sendResponse(client, getSensorData(0));
    else if (request.startsWith("GET /measurements/temperature")) sendResponse(client, getSensorData(1));
    else {
      client.println("HTTP/1.1 404 Not Found");
      client.println("Content-Type: text/plain");
      client.println("Connection: close");
      client.println();
      client.println("{\"error\": \"404 Not Found\"}");
    }

    client.stop();
	Serial.println("Client disconnected");
  }
}
