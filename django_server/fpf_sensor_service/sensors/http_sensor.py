import json

import requests

from .measurement_result import MeasurementResult
from .typed_sensor import TypedSensor
from .sensor_description import SensorDescription, ConnectionType, FieldDescription, FieldType, ValidHttpEndpointRule


class HttpSensor(TypedSensor):
    http_endpoint = None

    def init_additional_information(self):
        additional_information = json.loads(self.sensor_config.additionalInformation)
        self.http_endpoint = additional_information['http']

    @staticmethod
    def get_description() -> SensorDescription:
        return SensorDescription(
            sensor_class_id='d6d89f89-a5ae-48ed-9bd4-6e6645135f14',
            model='',
            connection=ConnectionType.HTTP,
            parameter='',
            unit='',
            tags={
                'info': 'model, parameter and unit have to be entered manually;Modell, Kennwert und Einheit müssen manuell eingetragen werden',
            },
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
        return MeasurementResult(value=response.json().get("value"))
