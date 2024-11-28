from .typed_sensor import TypedSensor
from .typed_sensor_factory import TypedSensorFactory

"""
ONLY Sensor classes imported here will be visible to the program and count as supported.
To disable any Sensor just comment out the line by putting a # in front of it
"""


from .dht22_sensors import PinDHT22HumiditySensor, PinDHT22TemperatureSensor



"""
THIS HAS TO BE AT THE BOTTOM OF THE FILE BELOW ALL THE SENSOR CLASS IMPORTS TO FUNCTION!!!
IT REPRESENTS A SINGLETON THAT SHOULD ALWAYS BE ACCESSED FROM HERE
"""
