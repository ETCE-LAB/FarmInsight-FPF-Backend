#include <WiFiNINA.h>
#include <Adafruit_ADS1X15.h>

float latestDistance = 0.0;
unsigned long lastReadTime = 0;

// Enter WLAN Access Credentials
const char ssid[] = "ssid";
const char pass[] = "pw";

const float BASE_CM = 30.0;
const float HEIGHT_CM = 60.0;

// Enter the static network information
IPAddress local_IP(1, 1, 1, 1);
IPAddress gateway(1, 1, 1, 1);
IPAddress subnet(255, 255, 255, 0);
IPAddress dns(8, 8, 8, 8);

// Status of connection
int status = WL_IDLE_STATUS;

// Declare an array named 'data' with 4 elements, all initialized to 0
// This array will store the bytes received from the distance sensor
unsigned char data[4] = {};

// Declare a floating-point variable to store the measured distance
float distance;

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

float calculateVolume(float distance_cm) {
  if (distance_cm < BASE_CM || distance_cm > HEIGHT_CM) {
    Serial.println("Out of range (too close or overflow)");
    return 0.0;
  }

  float water_height = HEIGHT_CM - distance_cm;
  float volume_cm3 = 65.0 * 45.0 * water_height;
  float volume_liters = volume_cm3 / 1000.0;

  Serial.print("Distance: ");
  Serial.print(distance_cm);
  Serial.print(" cm → Volume: ");
  Serial.print(volume_liters, 2);
  Serial.println(" liters");

  return volume_liters;
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

  // WLAN connect with retries if not possible
  while (status != WL_CONNECTED) {
    Serial.print("Connected with: ");
    Serial.println(ssid);
    status = WiFi.begin(ssid, pass);

    delay(10000);
  }

  // Print connection details
  Serial.println("Wifi Connected!");
  Serial.print("IP-Adresse: ");
  Serial.println(WiFi.localIP());

  // Start the server
  server.begin();

}

void loop() {
  // Continuously update distance


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
