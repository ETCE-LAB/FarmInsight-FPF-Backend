from . import MeasurementResult
from .http_sensor import HttpSensor
from .sensor_description import SensorDescription, ConnectionType, FieldDescription, FieldType, ValidHttpEndpointRule
import requests

class ShellySSensor(HttpSensor):
    @staticmethod
    def get_description() -> SensorDescription:
        return SensorDescription(
            sensor_class_id='63cd9dc2-ac79-4720-9f66-7ba902cdd541',
            model='Shelly S Smartplug',
            connection=ConnectionType.HTTP,
            parameter='Ampere;Ampere',
            unit='ampere',
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

