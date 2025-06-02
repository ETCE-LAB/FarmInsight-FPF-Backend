#include <Wire.h>
#include <WiFiNINA.h>
#include <Adafruit_TSL2591.h>

// WiFi Credentials
const char ssid[] = "SSID";
const char pass[] = "PW";

// Static IP Configuration (Optional)
IPAddress local_IP(1, 1, 1, 1);     // IP-Adresse des Arduino 214
IPAddress gateway(1, 1, 1, 1);        // Gateway (Router-IP)
IPAddress subnet(255, 255, 255, 192);      // Subnetzmaske
IPAddress dns(8, 8, 8, 8);                 // DNS-Server (Google DNS als Beispiel)

int status = WL_IDLE_STATUS; // WiFi Status
WiFiServer server(80);       // HTTP Server auf Port 80

Adafruit_TSL2591 tsl = Adafruit_TSL2591(2591); // TSL2591 Sensor

unsigned long lastWiFiCheck = 0;
const unsigned long wifiCheckInterval = 3600000; // 1 hour

// Read Sensor values
String getSensorData(String type) {
  uint16_t broadband = tsl.getFullLuminosity() & 0xFFFF; // Gesamte Lichtintensität
  uint16_t infrared = tsl.getFullLuminosity() >> 16;     // Infrarotwert
  float lux = tsl.calculateLux(broadband, infrared);

  if (type == "lux") {
    return "{\"lux\": " + String(lux, 2) + "}";
  } else if (type == "sumlight") {
    return "{\"sumlight\": " + String(broadband) + "}";
  } else if (type == "infrared") {
    return "{\"infrared\": " + String(infrared) + "}";
  } else {
    return "{\"error\": \"Invalid type\"}";
  }
}

// Send HTTP Answer
void sendResponse(WiFiClient &client, String data) {
  client.println("HTTP/1.1 200 OK");
  client.println("Content-Type: application/json");
  client.println("Connection: close");
  client.println();
  client.println(data);
}

// check Wifi and Reconnect Logic
void checkWiFiConnection() {
  status = WiFi.status();
  if (status == WL_CONNECTED) return;

  Serial.println("Reconnecting to WiFi...");
  while (status != WL_CONNECTED) {
    WiFi.begin(ssid, pass);
    Serial.print(".");
    delay(1000);
  }

  Serial.println("WiFi Reconnected!");
}

// Setup Function
void setup() {
  Serial.begin(9600);
  Wire.begin();
  
  // Setup für den TSL2591 Sensor
  tsl.setGain(TSL2591_GAIN_MED); // Empfindlichkeit des Sensors (niedrig, mittel, hoch)
  tsl.setTiming(TSL2591_INTEGRATIONTIME_100MS); // Messzeit, hier auf 100ms eingestellt

  // WiFi Verbindung herstellen
  Serial.println("Connecting to WiFi...");
  WiFi.config(local_IP, gateway, subnet);
  checkWiFiConnection();

  Serial.println("WiFi Connected! IP: " + WiFi.localIP().toString());
  server.begin();

  // start tsl sensor
  while (!tsl.begin()) {
    Serial.println("TSL2591 could not be initialized, please check cabels and connection!");
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

    // Handling Endpoints and requests
    if (request.startsWith("GET /measurements/lux")) {
      sendResponse(client, getSensorData("lux"));
    } else if (request.startsWith("GET /measurements/sumlight")) {
      sendResponse(client, getSensorData("sumlight"));
    } else if (request.startsWith("GET /measurements/infrared")) {
      sendResponse(client, getSensorData("infrared"));
    } else {
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
