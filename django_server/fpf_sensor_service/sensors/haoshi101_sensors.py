from .http_sensor import HttpSensor
import json
import requests

from .measurement_result import MeasurementResult
from .typed_sensor import TypedSensor
from .sensor_description import SensorDescription, ConnectionType, FieldDescription, FieldType, ValidHttpEndpointRule


class HttpHaoshi101PhSensor(HttpSensor):
    @staticmethod
    def get_description() -> SensorDescription:
        return SensorDescription(
            sensor_class_id='a7552f08-427e-43f7-b07e-850db607db81',
            model='Haoshi101',
            connection=ConnectionType.HTTP,
            parameter='pH;pH-Wert',
            unit='pH',
            tags={},
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
