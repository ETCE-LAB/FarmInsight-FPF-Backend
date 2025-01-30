#include <WiFiNINA.h>
#include <Adafruit_ADS1X15.h>

// Enter WLAN Access Credentials
const char ssid[] = "SSID";
const char pass[] = "PASSWORD";

// Enter the static network information
IPAddress local_IP(0, 0, 0, 0);
IPAddress gateway(0, 0, 0, 0);
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

// Perform measurement
float measure() {
  // Check if there is any data available to read from Serial1 (the distance sensor)
  if (Serial1.available()) {
    // Read one byte from Serial1 and check if it is 0xFF
    // 0xFF is used here as a start byte to indicate the beginning of a data frame
    if (Serial1.read() == 0xFF) {
      // If the start byte is detected, store it in data[0]
      data[0] = 0xFF;

      // Wait until at least 3 more bytes are available to read
      // These bytes contain the distance measurement and checksum
      while (Serial1.available() < 3);

      // Read the next three bytes and store them in the data array
      data[1] = Serial1.read(); // High byte of distance
      data[2] = Serial1.read(); // Low byte of distance
      data[3] = Serial1.read(); // Checksum byte

      // Calculate the checksum by adding the first three bytes and masking with 0x00FF
      // The checksum helps verify that the data received is correct
      int sum = (data[0] + data[1] + data[2]) & 0x00FF;

      // Compare the calculated checksum with the received checksum (data[3])
      if (sum == data[3]) {
        // If the checksum is correct, calculate the distance
        // (data[1] << 8) shifts the high byte to its proper position
        // Adding data[2] combines both bytes to form the full distance value
        distance = (data[1] << 8) + data[2];

        // Check if the distance is greater than 30 (to filter out very close objects)
        if (distance > 30) {
          // If the distance is valid, print it to the Serial Monitor
          // The distance is divided by 10 to convert it to centimeters
          Serial.print("distance=");
          Serial.print(distance / 10);
          Serial.println("cm");

          return (distance / 10);
        } else {
          // If the distance is too close, print a warning message
          Serial.println("Below the lower limit");
        }
      } else {
        // If the checksum does not match, print an error message
        // This indicates that the data received may be corrupted
        Serial.println("ERROR");
      }
    }
  }
}

void setup() {
  Serial.begin(9600);
  while (!Serial) {
    ; // Wait till serial connection is created
  }

  Serial.println("WiFi-Verbindung wird aufgebaut...");

  // check WLAN-module exists
  if (WiFi.status() == WL_NO_MODULE) {
    Serial.println("WLAN-Modul nicht gefunden!");
    while (true); // Endlosschleife, da kein WLAN-Modul vorhanden
  }

  // apply WLAN config
  WiFi.config(local_IP, gateway, subnet);

  // WLAN connect with retries if not possible
  while (status != WL_CONNECTED) {
    Serial.print("Verbinden mit: ");
    Serial.println(ssid);
    status = WiFi.begin(ssid, pass);

    delay(10000);
  }

  // Print connection details
  Serial.println("WLAN verbunden!");
  Serial.print("IP-Adresse: ");
  Serial.println(WiFi.localIP());

  // Start the server
  server.begin();

}

void loop() {
  // Check if a client is connected
  WiFiClient client = server.available();
  if (client) {
    Serial.println("New client connected");

    // Wait for the client to send a request
    while (client.connected() && !client.available()) {
      delay(1);
    }

    // Read the request
    String request = client.readStringUntil('\r');
    Serial.print("Request: ");
    Serial.println(request);

    // Parse the request
    if (request.startsWith("GET /measurements/distance")) {

      // Create JSON response
      String jsonResponse = "{";
      jsonResponse += "\"sensor_id\": 1,";
      jsonResponse += "\"value\": " + String(measure(), 2);
      jsonResponse += "}";

      // Send HTTP response
      client.println("HTTP/1.1 200 OK");
      client.println("Content-Type: application/json");
      client.println("Connection: close");
      client.println();
      client.println(jsonResponse);

      Serial.println("Response sent");
    } else {
      // Handle unknown request
      client.println("HTTP/1.1 404 Not Found");
      client.println("Content-Type: text/plain");
      client.println("Connection: close");
      client.println();
      client.println("404 Not Found");
    }

    // Close the connection
    client.stop();
    Serial.println("Client disconnected");
  }
}
