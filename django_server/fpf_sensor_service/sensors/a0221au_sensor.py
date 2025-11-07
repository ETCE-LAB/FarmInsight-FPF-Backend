import requests

from fpf_sensor_service.scripts_base import FieldDescription, FieldType, ValidHttpEndpointRule
from .sensor_description import SensorDescription, ConnectionType
from .http_sensor import HttpSensor
from . import MeasurementResult


class HttpA0221AULevelSensor(HttpSensor):
    @staticmethod
    def get_description() -> SensorDescription:
        return SensorDescription(
            script_class_id='c40d2db9-c2d5-416a-9bae-6464720ff397',
            model='A0221AU',
            connection=ConnectionType.HTTP,
            parameter='level;füllstand',
            unit='l',
            tags={
                'info': 'expects specifically configured sensor calculation;Erwartet speziell konfigurierte Sensor Berechnung'
            },
            fields=[
                FieldDescription(
                    id='http',
                    name='http',
                    description='The http endpoint of the sensor;Der HTTP Endpunkt des Sensors',
                    type=FieldType.STRING,
                    rules=[
                        ValidHttpEndpointRule(),
                    ]
                ),
            ]
        )

    def run(self, payload=None) -> any:
        response = requests.get(self.http_endpoint)
        response.raise_for_status()
        return MeasurementResult(value=response.json().get("value"))
