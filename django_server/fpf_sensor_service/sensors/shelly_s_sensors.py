import json
from . import MeasurementResult, TypedSensor
from .http_sensor import HttpSensor
from .sensor_description import SensorDescription, ConnectionType, FieldDescription, FieldType, ValidHttpEndpointRule
import requests

from ..models import SensorMeasurement


class ShellySSensor(HttpSensor):
    @staticmethod
    def get_description() -> SensorDescription:
        return SensorDescription(
            sensor_class_id='63cd9dc2-ac79-4720-9f66-7ba902cdd541',
            model='Shelly S Smartplug',
            connection=ConnectionType.HTTP,
            parameter='watt;Watt',
            unit='W',
            tags={},
            fields=[
                FieldDescription(
                    name='http',
                    type=FieldType.STRING,
                    rules=[
                        ValidHttpEndpointRule(),
                    ]
                ),
            ]
        )

    def get_measurement(self) -> MeasurementResult:
        response = requests.get(self.http_endpoint, timeout=10)
        response.raise_for_status()
        return MeasurementResult(value=response.json().get("apower"))


class MQTTShellySSensor(TypedSensor):
    mqtt_topic = None

    def init_additional_information(self):
        additional_information = json.loads(self.sensor_config.additionalInformation)
        self.mqtt_topic = additional_information['mqtt_topic']

    @staticmethod
    def get_description() -> SensorDescription:
        return SensorDescription(
            sensor_class_id='400e3ea5-02e7-45ac-9c88-e3676fb67669',
            model='Shelly S Smartplug',
            connection=ConnectionType.MQTT,
            parameter='kilowatthours;Kilowattstunden',
            unit='kwh',
            tags={},
            fields=[
                FieldDescription(
                    name='mqtt_topic',
                    type=FieldType.STRING,
                    rules=[]
                ),
            ]
        )

    def get_measurement(self, payload) -> MeasurementResult:
        value = payload["params"]["switch:0"]["aenergy"]["total"]

        return MeasurementResult(value=value / 1000)

