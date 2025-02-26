import json

import requests

from .typed_sensor import TypedSensor
from .sensor_description import SensorDescription, ConnectionType, FieldDescription, FieldType, ValidHttpEndpointRule


class HttpA0221AULevelSensor(TypedSensor):
    http_endpoint = None

    def init_additional_information(self):
        additional_information = json.loads(self.sensor_config.additionalInformation)
        self.http_endpoint = additional_information['http']

    @staticmethod
    def get_description() -> SensorDescription:
        return SensorDescription(
            sensor_class_id='c7fa5c6e-cb40-4f63-9d76-8a556d755b85',
            model='A0221AU',
            connection=ConnectionType.HTTP,
            parameter='level;füllstand',
            unit='l',
            tags={
                'info': 'expects specifically configured sensor calculation.'
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
        response = requests.get(self.http_endpoint)
        response.raise_for_status()
        return response.json().get("value")
