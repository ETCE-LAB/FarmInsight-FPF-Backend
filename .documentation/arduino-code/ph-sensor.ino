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

// Create an ADS1115 object
Adafruit_ADS1115 ads;

// Setting gain for ADS1115
adsGain_t gain = GAIN_TWOTHIRDS;

// Wi-Fi server object
WiFiServer server(80);

// Function to convert ADC reading to voltage
float ads1115_to_voltage(int16_t adcValue, adsGain_t gain) {
  float fsRange; // Full-scale range in volts based on gain
  float lsb;     // Least Significant Bit weight

  switch (gain) {
    case GAIN_TWOTHIRDS: fsRange = 6.144; break;
    case GAIN_ONE:        fsRange = 4.096; break;
    case GAIN_TWO:        fsRange = 2.048; break;
    case GAIN_FOUR:       fsRange = 1.024; break;
    case GAIN_EIGHT:      fsRange = 0.512; break;
    case GAIN_SIXTEEN:    fsRange = 0.256; break;
    default:              fsRange = 6.144; break; // Default to the largest range
  }

  lsb = fsRange / 32767.0; // Calculate the weight of each bit
  return adcValue * lsb;
}

void setup() {
  Serial.begin(9600);
  while (!Serial) {
    ; // Wait till serial connection is created
  }

  Serial.println("Serial Monitor started, Establishing WIfi...");

  // check WLAN-module exists
  if (WiFi.status() == WL_NO_MODULE) {
    Serial.println("WLAN-Modul nicht gefunden!");
    while (true); // Endlosschleife, da kein WLAN-Modul vorhanden
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
  Serial.println("Wifi connected!");
  Serial.print("IP-Adress: ");
  Serial.println(WiFi.localIP());

  // Start the server
  server.begin();

  // Initialize ADS1115
  if (!ads.begin()) {
    Serial.println("Failed to find ADS1115 chip");
    while (1);
  }
  ads.setGain(gain);
  Serial.println("ADS1115 initialized");
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
    if (request.startsWith("GET /measurements/ph")) {

      // Perform the measurement
      int16_t adc1 = ads.readADC_SingleEnded(1);
      float voltage = ads1115_to_voltage(adc1, gain);

      float neutralVoltage = 1.5;
      float acidVoltage = 2.05;

      float slope = (6.8 - 4.0) / ((neutralVoltage - 1.5) / 3.0 - (acidVoltage - 1.5) / 3.0);

      float intercept = 6.8 - slope * (neutralVoltage - 1.5) / 3.0;

      float phValue = slope * (voltage - 1.5) / 3.0 + intercept;

      // Create JSON response
      String jsonResponse = "{";
      jsonResponse += "\"sensor_id\": 1,";
      jsonResponse += "\"value\": " + String(phValue, 2);
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
