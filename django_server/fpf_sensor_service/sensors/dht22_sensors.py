import json

from fpf_sensor_service.sensors.typed_sensor import TypedSensor, SensorDescription, ConnectionType, FieldDescription, \
    FieldType, IntRangeRuleInclusive

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
            parameter='humidity',
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
        dhtDevice = DHT22(Pin(self.pin))
        value = dhtDevice.humidity
        dhtDevice.exit()
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
            parameter='temperature',
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
        dhtDevice = DHT22(Pin(self.pin))
        value = dhtDevice.temperature
        dhtDevice.exit()
        return value
