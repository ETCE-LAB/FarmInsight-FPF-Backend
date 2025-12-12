/*
	The sensor we use is the A02YYUW Waterproof Ultrasonic Sensor https://wiki.dfrobot.com/_A02YYUW_Waterproof_Ultrasonic_Sensor_SKU_SEN0311
	
	The sensor comes with a UART cable and 4 pin cables.
	https://content.arduino.cc/assets/Pinout-NANO33IoT_latest.pdf
	Red		-> 3V3 or 5V
	Black 	-> Ground pin
	Blue 	-> TX
	Green 	-> RX
*/

#include <WiFiNINA.h>
#include <Adafruit_ADS1X15.h>

// Enter WLAN Access Credentials
const char ssid[] = "SSID";
const char pw[] = "pass";

// Enter the static network information
IPAddress local_IP(139, 174, 57, xx);
IPAddress gateway(1, 1, 1, 1);
IPAddress subnet(255, 255, 255, 0);

// Status of connection
int status = WL_IDLE_STATUS;

// Declare an array named 'data' with 4 elements, all initialized to 0
// This array will store the bytes received from the distance sensor
unsigned char data[4] = {};

// Wi-Fi server object
WiFiServer server(80);


float readDistance(unsigned long timeout = 1000) {
  unsigned long startTime = millis();
  float distance_cm = 0.0;

  while (Serial1.available()) {
    Serial1.read();
  }

  while (millis() - startTime < timeout) {
    if (Serial1.available()) {
      if (Serial1.read() == 0xFF) {
        data[0] = 0xFF;

        unsigned long waitStart = millis();
        while (Serial1.available() < 3) {
          if (millis() - waitStart > 100) {
            Serial.println("Timeout waiting for rest of packet");
            return 0.0;
          }
        }

        data[1] = Serial1.read();
        data[2] = Serial1.read();
        data[3] = Serial1.read();

        int sum = (data[0] + data[1] + data[2]) & 0x00FF;

        if (sum == data[3]) {
          float dist = ((data[1] << 8) + data[2]) / 10.0;
          return dist;
        } else {
          Serial.println("Checksum error");
        }
      }
    }
  }

  Serial.println("Timeout: no valid data");
  return 0.0;
}

const float MAX_DIST_CM = 78.0;
const float MIN_DIST_CM = 3.0;
const float WATER_FULL_L = 210;

float calculateVolume(float distance_cm) {
  // -1.574 * 10^-5 * x^3 + 0.01306 * x^2 - 3.617 * x + 210

  if (distance_cm > MAX_DIST_CM) { // shouldn't happen if sensor is installed correctly inside the container
    return 0.0;
  } else if (distance_cm < MIN_DIST_CM) { // Overflow should prevent this from ever happening but better to catch it
    return WATER_FULL_L;
  }

  // -1.574 * 10^-5 * d^3 + 0.01306 * d^2 - 3.617 * d + 210
  float d = distance_cm;
  float volume_liters = -1.574 * 0.00001 * d * d * d + 0.01306 * d * d - 3.617 * d + 210;

  if (volume_liters < 0) {
    volume_liters = 0.0;
  }

  Serial.print("Distance: ");
  Serial.print(distance_cm);
  Serial.print(" cm → Volume: ");
  Serial.print(volume_liters, 2);
  Serial.println(" liters");

  return volume_liters;
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
  if (server.status() != 1) {
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

void setup() {
  Serial1.begin(9600);
  Serial.begin(9600);

  // check WLAN-module exists
  if (WiFi.status() == WL_NO_MODULE) {
    Serial.println("WIFI-module not found!");
    while (true); 
  }

  // apply WLAN config
  WiFi.config(local_IP, gateway, subnet);
  checkWiFiConnection();

  // Print connection details
  Serial.print("IP-Adresse: ");
  Serial.println(WiFi.localIP());

  server.begin();
}

void loop() {
  checkWiFiConnection();
  checkServerStatus();

  WiFiClient client = server.available();
  if (client) {
    Serial.println("New client connected");
    while (client.connected() && !client.available()) {
      delay(1);
    }

    String request = client.readStringUntil('\r');
    Serial.print("Request: ");
    Serial.println(request);

    if (request.startsWith("GET /measurements/distance")) {
      float distance = readDistance();
      float volume = calculateVolume(distance);

      String jsonResponse = "{";
      jsonResponse += "\"sensor\": \"ultrasonic-sensor\",";
      jsonResponse += "\"distance\": " + String(distance, 1) + ",";
      jsonResponse += "\"value\": " + String(volume, 2);
      jsonResponse += "}";

      client.println("HTTP/1.1 200 OK");
      client.println("Content-Type: application/json");
      client.println("Connection: close");
      client.println();
      client.println(jsonResponse);

      Serial.println("Response sent");
    } else {
      client.println("HTTP/1.1 404 Not Found");
      client.println("Content-Type: text/plain");
      client.println("Connection: close");
      client.println();
      client.println("404 Not Found");
    }

    client.stop();
    Serial.println("Client disconnected");
  }
}
