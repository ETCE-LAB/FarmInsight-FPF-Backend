import json

import requests

from fpf_sensor_service.models import SensorMeasurement
from .typed_sensor import TypedSensor, SensorType
from .sensor_description import SensorDescription, ConnectionType, FieldDescription, FieldType, ValidHttpEndpointRule


class Camera(TypedSensor):
    def init_additional_information(self):
        additional_information = json.loads(self.sensor_config.additionalInformation)
        self.snapshot_url =additional_information['snapshotUrl']

    @staticmethod
    def get_description() -> SensorDescription:
        # this doesn't really get used, outside the id for now
        return SensorDescription(
            sensor_class_id='cacacaca-caca-caca-caca-cacacacacaca',
            model='',
            connection=ConnectionType.HTTP,
            parameter='',
            unit='',
            tags={},
            fields=[
                FieldDescription(
                    name='snapshotUrl',
                    type=FieldType.STRING,
                    rules=[
                        ValidHttpEndpointRule(),
                    ]
                ),
            ]
        )

    @staticmethod
    def get_type() -> SensorType:
        return SensorType.Camera

    def get_measurement(self, payload=None) -> SensorMeasurement:
        raise NotImplementedError()

    def get_image(self):
        response = requests.get(self.snapshot_url, stream=True)
        return response.raw
