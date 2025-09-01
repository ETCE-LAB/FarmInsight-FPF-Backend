import network
import socket
import time
import json
import gc
import sht31


sensor = sht31.SHT31(scl_pin=1 , sda_pin=0)

# Function to connect to WiFi
def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect("DIGIT-RasPi", "r6HYUaJ19kRQQT9E5EGw")
    
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

# Initial connection
wlan = connect_to_wifi()

# Set up the socket
def bind_socket():
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    s.settimeout(10)  # Set a timeout for socket operations
    print('Listening on', addr)
    return s

s = bind_socket()

# Serve HTTP requests
while True:
    try:
        gc.collect()
        # Reconnect to WiFi if disconnected
        if wlan.status() != 3:
            wlan = connect_to_wifi()
            try:
                s.close()
            finally:
                s = None

        if s is None:
            s = bind_socket()

        cl, addr = s.accept()
        cl.settimeout(5)  # Set timeout for client socket operations
        print('Client connected from', addr)

        try:
            request = cl.recv(1024).decode('utf-8')
            print('Request:', request)

            if 'GET /measurements/temperature' in request:
                try:
                    _, temperature = sensor.measure()  # °C
                    response = {"value": temperature}
                except Exception as e:
                    print('Error reading temperature:', e)
                    response = {"error": "Failed to read temperature"}
            elif 'GET /measurements/humidity' in request:
                try:
                    humidity, _ = sensor.measure()  # %
                    response = {"value": humidity}
                except Exception as e:
                    print('Error reading humidity:', e)
                    response = {"error": "Failed to read humidity"}
            else:
                response = {"error": "Invalid endpoint"}

            cl.send('HTTP/1.0 200 OK\r\nContent-type: application/json\r\n\r\n')
            cl.send(json.dumps(response))
        except OSError as e:
            print("Error during request processing:", e)
        finally:
            cl.close()

    except OSError as e:
        print('Socket accept failed with:', e)

    except Exception as e:
        print('General error:', e)
