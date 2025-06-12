#include <WiFiNINA.h>
#include <Adafruit_ADS1X15.h>

// WiFi Credentials
const char ssid[] = "ssid";
const char pass[] = "pw";

// Static IP Configuration (Optional)
IPAddress local_IP(1, 1, 1, 1);     // IP-Adresse des Arduino
IPAddress gateway(1, 1, 1, 1);        // Gateway (Router-IP)
IPAddress subnet(255, 255, 255, 192);       // Subnetzmaske
IPAddress dns(8, 8, 8, 8);                // DNS-Server (Google DNS als Beispiel)

int status = WL_IDLE_STATUS; // WiFi Status

WiFiServer server(80);

// Create an ADS1115 object
Adafruit_ADS1115 ads;

// Setting gain for ADS1115
adsGain_t gain = GAIN_TWOTHIRDS;

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

String getSensorData() {
    // Perform the measurement
  int16_t adc1 = ads.readADC_SingleEnded(1);
  float voltage = ads1115_to_voltage(adc1, gain);

  float neutralVoltage = 1.5;
  float acidVoltage = 2.05;

  float slope = (6.8 - 4.0) / ((neutralVoltage - 1.5) / 3.0 - (acidVoltage - 1.5) / 3.0);
  float intercept = 6.8 - slope * (neutralVoltage - 1.5) / 3.0;
  float phValue = slope * (voltage - 1.5) / 3.0 + intercept;
  
  return "{\"value\": " + String(phValue, 2) + "}";
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
void reconnectWiFiConnection() {
  if (WiFi.status() == WL_CONNECTED) return;

  WiFi.disconnect();
  WiFi.config(local_IP, gateway, subnet);
  while (status != WL_CONNECTED) {
    status = WiFi.begin(ssid, pass);
    delay(10000);
  }

  if (!server) {
    server.begin();
  }
}

// Setup Function
void setup() {
  reconnectWiFiConnection();

  // Initialize ADS1115
  while (!ads.begin()) {
    delay(2000);
  }
  ads.setGain(gain);
}

// restart the arduino from code
int requests_until_reboot = 24; // since we know typically 1 value per day, this is once daily
void(* resetFunc) (void) = 0;

// Main Loop
void loop() {
  reconnectWiFiConnection();

  WiFiClient client = server.available();
  if (client) {
    while (client.connected() && !client.available()) delay(1);
    String request = client.readStringUntil('\r');
  
    if (request.startsWith("GET /measurements/ph")) {
      sendResponse(client, getSensorData());
      requests_until_reboot -= 1;
      if (requests_until_reboot <= 0) {
        resetFunc();
      }
    } else {
      client.println("HTTP/1.1 404 Not Found");
      client.println("Content-Type: text/plain");
      client.println("Connection: close");
      client.println();
      client.println("404 Not Found");
    }

    client.stop();
  }
}
