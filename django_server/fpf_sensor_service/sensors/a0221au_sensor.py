import json

import requests

from . import MeasurementResult
from .typed_sensor import TypedSensor
from .sensor_description import SensorDescription, ConnectionType, FieldDescription, FieldType, ValidHttpEndpointRule
from .http_sensor import HttpSensor

class HttpA0221AULevelSensor(HttpSensor):
    @staticmethod
    def get_description() -> SensorDescription:
        return SensorDescription(
            sensor_class_id='c40d2db9-c2d5-416a-9bae-6464720ff397',
            model='A0221AU',
            connection=ConnectionType.HTTP,
            parameter='level;füllstand',
            unit='l',
            tags={
                'info': 'expects specifically configured sensor calculation;Erwartet speziell konfigurierte Sensor Berechnung'
            },
            fields=[
                FieldDescription(
                    name='http',
                    type=FieldType.STRING,
                    rules=[
                        ValidHttpEndpointRule(
                            regex = r"^(https?:\/\/)?([a-zA-Z0-9.-]+)(:[0-9]{1,5})?(\/[^\s]*)?$"
                        ),
                    ]
                ),
            ]
        )

    def get_measurement(self)-> MeasurementResult:
        response = requests.get(self.http_endpoint)
        response.raise_for_status()
        return MeasurementResult(value=response.json().get("value"))
