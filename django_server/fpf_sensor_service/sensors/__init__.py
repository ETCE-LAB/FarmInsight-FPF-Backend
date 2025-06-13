from .typed_sensor import TypedSensor
from .typed_sensor_factory import TypedSensorFactory

"""
ONLY Sensor classes imported here will be visible to the program and count as supported.
To disable any Sensor just comment out the line by putting a # in front of it
"""


from .dht22_sensors import PinDHT22HumiditySensor, PinDHT22TemperatureSensor, HttpDHT22HumiditySensor, HttpDHT22TemperatureSensor
from .haoshi101_sensors import HttpHaoshi101PhSensor
from .measurement_result import MeasurementResult
from .weather_station_sensors import HttpWeatherStationAirTemperatureSensor
from .http_sensor import HttpSensor
from .mqtt_sensors import MqttSensor
from .shelly_s_sensors import MQTTShellySSensor, ShellySSensor
from .http_mqtt_sensors import HttpMqttSensor
