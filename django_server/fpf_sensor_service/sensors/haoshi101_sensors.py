import json
import requests

from .typed_sensor import TypedSensor
from .sensor_description import SensorDescription, ConnectionType, FieldDescription, FieldType, ValidHttpEndpointRule


class HttpHaoshi101PhSensor(TypedSensor):
    http_endpoint = None

    def init_additional_information(self):
        additional_information = json.loads(self.sensor_config.additionalInformation)
        self.http_endpoint = additional_information['http']

    @staticmethod
    def get_description() -> SensorDescription:
        return SensorDescription(
            sensor_class_id='a7552f08-427e-43f7-b07e-850db607db81',
            model='Haoshi101',
            connection=ConnectionType.HTTP,
            parameter='pH;pH',
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

    def get_measurement(self):
        response = requests.get(self.http_endpoint)
        response.raise_for_status()
        return response.json().get("value")
