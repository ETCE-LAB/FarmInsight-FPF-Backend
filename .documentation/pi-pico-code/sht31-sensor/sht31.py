"""class interface to the sht31 using i2c

this is based off the circuit python version 
https://github.com/adafruit/Adafruit_CircuitPython_SHT4x"""

import machine
import struct
import time

_SHT4X_DEFAULT_ADDR = const(0x44)  # SHT4X I2C Address
_SHT4X_READSERIAL = const(0x89)  # Read Out of Serial Register
_SHT4X_SOFTRESET = const(0x94)  # Soft Reset

class SHT31:
    """i2c interafce for the DHT31 sensor
    """

    def __init__(self, scl_pin, sda_pin, freq=115200):
        """interface for SHT31

        Args:
            scl_pin (int): scl pin identifier
            sda_pin (int): sda pin identifier
            freq (int, optional): board frequency based off nodemcu baud rate. Defaults to 115200.
        """

        self.i2c = machine.I2C(0, scl=machine.Pin(scl_pin), sda=machine.Pin(sda_pin), freq=freq)
        print(self.i2c.scan())

    def measure(self) -> tuple(float, float):
        """reads hubitity (%) and temperature (C) and returns
        tuple with results.  First value is humidity (0-100 %) and second
        value is temperature (C)
        """
        # creating this so we can fill it in later.  Following the circuit python
        # example here https://github.com/adafruit/Adafruit_CircuitPython_SHT4x/blob/main/adafruit_sht4x.py
        buffer = bytearray(6)

        # filling in buffer from this standard 
        buffer[0] = 0x24  # !!! IMPORTANT - version dependent which value goes into the buffer, SHt40 for example uses different onesa

        # initiating i2c bus
        self.i2c.writeto(_SHT4X_DEFAULT_ADDR, buffer)

        # can adjust this in future
        time.sleep(1)

        # now going to read
        self.i2c.readfrom_into(_SHT4X_DEFAULT_ADDR, buffer)

        temp_data = buffer[0:2]
        temp_crc = buffer[2]
        humidity_data = buffer[3:5]
        humidity_crc = buffer[5]

        temperature = struct.unpack_from(">H", temp_data)[0]
        temperature = -45.0 + 175.0 * temperature / 65535.0

        # repeat above steps for humidity data
        humidity = struct.unpack_from(">H", humidity_data)[0]
        humidity = -6.0 + 125.0 * humidity / 65535.0
        humidity = max(min(humidity, 100), 0)

        return (humidity, temperature)
