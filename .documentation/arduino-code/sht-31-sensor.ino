#include <Wire.h>
#include <WiFiNINA.h>
#include <Adafruit_SHT31.h>

// WiFi Credentials
const char ssid[] = "";
const char pw[] = "";

// Static IP Configuration (Optional)
IPAddress local_IP(139, 174, 57, xx);    
IPAddress gateway(1, 1, 1, 1);        // Gateway (Router-IP)
IPAddress subnet(255, 255, 255, 192);       // Subnetzmaske

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

void checkWiFiConnection() {
  status = WiFi.status();
  if (status == WL_CONNECTED) return;

  Serial.println("WiFI not connected");

  Serial.print("Connecting to WiFi..");
  while (status != WL_CONNECTED) {
    status = WiFi.begin(ssid, pw);
    Serial.print(".");
    delay(10000);
  }

  Serial.println();
  Serial.println("Connected to WiFi");
}

void checkServerStatus() {
  if (server.status() != 1 && status == WL_CONNECTED) {
    Serial.println("Server not listening");
    Serial.println("Starting server");
    
    server.begin();

    if (server.status() == 1) {
      Serial.println("Server start successful");
    } else {
      Serial.println("Server start failed");
    }
  }
}

// Setup Function
void setup() {
  Serial.begin(9600);
  delay(100);
  Wire.begin();

  WiFi.config(local_IP, gateway, subnet);
  checkWiFiConnection();
  Serial.println("WiFi Connected! IP: " + WiFi.localIP().toString());

  while(!sht31.begin(0x44)) {
    Serial.println("SHT could not be initialized, please check cabels and connection!");
    delay(2000);
  }

  server.begin();
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

  checkServerStatus();
}
