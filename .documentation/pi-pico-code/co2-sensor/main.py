from machine import Pin, I2C
import network
import socket
import time
import ujson
import secrets

# === CONFIG ===
SENSOR_I2C_ADDRESS = 0x74  # Based on DIP switch
I2C_SDA = 0
I2C_SCL = 1

# === INIT I2C ===
i2c = I2C(0, scl=Pin(I2C_SCL), sda=Pin(I2C_SDA), freq=100000)


# === Wi-Fi Connect ===
# Function to connect to WiFi
def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(secrets.SSID, secrets.PASSWORD)

    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('Waiting for connection...')
        time.sleep(1)

    if wlan.status() != 3:
        raise RuntimeError('Network connection failed')
    else:
        print('Connected to WiFi')
        status = wlan.ifconfig()
        print('IP address:', status[0])
    return wlan


# === Read Gas Sensor ===
def read_gas_percentage():
    try:
        command = bytes([0xFF, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79])
        i2c.writeto(SENSOR_I2C_ADDRESS, command)
        time.sleep(0.2)
        data = i2c.readfrom(SENSOR_I2C_ADDRESS, 9)

        print("Raw response:", [hex(b) for b in data])

        if data[0] == 0xFF and data[1] == 0x86:
            voltage_mv = (data[2] << 8) | data[3]
            voltage = voltage_mv / 1000.0

            sensitivity = 0.003  # V/ppm, adjust from datasheet
            zero_voltage = 0.009
            print(voltage)
            ppm = (voltage - zero_voltage) / sensitivity
            return max(0, ppm)
        else:
            print("Unexpected header:", data[0], data[1])
    except Exception as e:
        print("Sensor read error:", e)
    return None


# === HTTP Server ===
def serve():
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    print("Server listening on http://%s" % addr[0])

    while True:
        client, _ = s.accept()
        try:
            req = client.recv(1024).decode()
            print("Request:", req)
            if "GET /measurements" in req and "type=gas" in req:
                value = read_gas_percentage()
                if value is not None:
                    response = ujson.dumps({"sensor": "CO", "value": value})
                else:
                    response = ujson.dumps({"error": "Sensor read failed"})
                client.send("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n")
                client.send(response)
            else:
                client.send("HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\n\r\n404 Not Found")
        except Exception as e:
            print("Client error:", e)
        finally:
            client.close()


# === RUN ===
# Initial connection
wlan = connect_to_wifi()

i2c = I2C(0, scl=Pin(1), sda=Pin(0))
devices = i2c.scan()

if devices:
    print("I2C devices found:", [hex(d) for d in devices])
else:
    print("No I2C devices found")

serve()