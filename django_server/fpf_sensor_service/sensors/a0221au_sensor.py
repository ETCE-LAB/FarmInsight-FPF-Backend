import json

import requests

from fpf_sensor_service.sensors.typed_sensor import TypedSensor, SensorDescription, ConnectionType, FieldDescription, \
    FieldType, ValidHttpEndpointRule


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
                'info': 'make sure the sensor is correctly configured.'
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
