import network
import socket
import time
import json
from machine import Pin
import dht
import secrets

# GPIO Pin for DHT22
DHT_PIN = 10
sensor = dht.DHT22(Pin(DHT_PIN))

# Connect to WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(secrets.SSID, secrets.PASSWORD)

# Wait for connection
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

# Set up socket
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)
print('Listening on', addr)

# Serve HTTP requests
while True:
    try:
        cl, addr = s.accept()
        print('Client connected from', addr)
        request = cl.recv(1024).decode('utf-8')
        print('Request:', request)

        # Parse HTTP request
        if 'GET /measurements/temperature' in request:
            try:
                sensor.measure()
                temperature = sensor.temperature()  # °C
                response = {"value": temperature}
            except Exception as e:
                print('Error reading temperature:', e)
                response = {"error": "Failed to read temperature"}
        elif 'GET /measurements/humidity' in request:
            try:
                sensor.measure()
                humidity = sensor.humidity()  # %
                response = {"value": humidity}
            except Exception as e:
                print('Error reading humidity:', e)
                response = {"error": "Failed to read humidity"}
        else:
            response = {"error": "Invalid endpoint"}

        # Send HTTP response
        cl.send('HTTP/1.0 200 OK\r\nContent-type: application/json\r\n\r\n')
        cl.send(json.dumps(response))
        cl.close()

    except OSError as e:
        cl.close()
        print('Connection closed:', e)
