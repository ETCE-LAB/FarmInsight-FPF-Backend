import json
import requests

from fpf_sensor_service.sensors.typed_sensor import TypedSensor, SensorDescription, ConnectionType, FieldDescription, \
    FieldType, IntRangeRuleInclusive, ValidHttpEndpointRule

from adafruit_blinka.microcontroller.bcm283x.pin import Pin
from adafruit_dht import DHT22


class PinDHT22HumiditySensor(TypedSensor):
    pin = None

    def init_additional_information(self):
        additional_information = json.loads(self.sensor_config.additionalInformation)
        self.pin = additional_information['pin']

    @staticmethod
    def get_description() -> SensorDescription:
        return SensorDescription(
            sensor_class_id='7711013a-d9f6-4990-9d9b-7222ff98ca9f',
            model='DHT22',
            connection=ConnectionType.PIN,
            parameter='humidity;feuchtigkeit',
            unit='%',
            tags={
                'info': 'minimum interval 3 seconds.'
            },
            fields=[
                FieldDescription(
                    name='pin',
                    type=FieldType.INTEGER,
                    rules=[
                        IntRangeRuleInclusive(
                            min=1,
                            max=40
                        ),
                    ]
                ),
            ]
        )

    def get_measurement(self):
        dht_device = None
        try:
            dht_device = DHT22(Pin(self.pin))
            value = dht_device.humidity
            dht_device.exit()
        except Exception as e:
            if dht_device is not None:
                dht_device.exit()
            raise e

        return value


class PinDHT22TemperatureSensor(TypedSensor):
    pin = None

    def init_additional_information(self):
        additional_information = json.loads(self.sensor_config.additionalInformation)
        self.pin = additional_information['pin']

    @staticmethod
    def get_description() -> SensorDescription:
        return SensorDescription(
            sensor_class_id='5464114a-443f-4c56-a864-abc415b3d3a2',
            model='DHT22',
            connection=ConnectionType.PIN,
            parameter='temperature;temperatur',
            unit='°C',
            tags={
                'info': 'minimum interval 3 seconds.'
            },
            fields=[
                FieldDescription(
                    name='pin',
                    type=FieldType.INTEGER,
                    rules=[
                        IntRangeRuleInclusive(
                            min=1,
                            max=40
                        ),
                    ]
                ),
            ]
        )

    def get_measurement(self):
        dht_device = None
        try:
            dht_device = DHT22(Pin(self.pin))
            value = dht_device.temperature
            dht_device.exit()
        except Exception as e:
            if dht_device is not None:
                dht_device.exit()
            raise e
        return value


class HttpDHT22HumiditySensor(TypedSensor):
    http_endpoint = None

    def init_additional_information(self):
        additional_information = json.loads(self.sensor_config.additionalInformation)
        self.http_endpoint = additional_information['http']

    @staticmethod
    def get_description() -> SensorDescription:
        return SensorDescription(
            sensor_class_id='c7fa5c6e-cb40-4f63-9d76-8a556d755b85',
            model='DHT22',
            connection=ConnectionType.HTTP,
            parameter='humidity;feuchtigkeit',
            unit='%',
            tags={
                'info': 'minimum interval 3 seconds.'
            },
            fields=[
                FieldDescription(
                    name='http',
                    type=FieldType.STRING,
                    rules=[
                        ValidHttpEndpointRule(
                            regex="^(https?:\/\/)?([a-zA-Z0-9.-]+)(:[0-9]{1,5})?(\/[^\s]*)?$"
                        ),
                    ]
                ),
            ]
        )

    def get_measurement(self):
        try:
            response = requests.get(self.http_endpoint)
            response.raise_for_status()
            return response.json().get("value")

        except requests.exceptions.RequestException as e:
            print(f"Failed to get measurement: {e}")
            return None


class HttpDHT22TemperatureSensor(TypedSensor):
    http_endpoint = None

    def init_additional_information(self):
        additional_information = json.loads(self.sensor_config.additionalInformation)
        self.http_endpoint = additional_information['http']

    @staticmethod
    def get_description() -> SensorDescription:
        return SensorDescription(
            sensor_class_id='fd45e455-57b5-4495-b326-a0cafdc3aa39',
            model='DHT22',
            connection=ConnectionType.HTTP,
            parameter='temperature;temperatur',
            unit='°C',
            tags={
                'info': 'minimum interval 3 seconds.'
            },
            fields=[
                FieldDescription(
                    name='http',
                    type=FieldType.STRING,
                    rules=[
                        ValidHttpEndpointRule(
                            regex="^(https?:\/\/)?([a-zA-Z0-9.-]+)(:[0-9]{1,5})?(\/[^\s]*)?$"
                        ),
                    ]
                ),
            ]
        )

    def get_measurement(self):
        try:
            response = requests.get(self.http_endpoint)
            response.raise_for_status()
            return response.json().get("value")
