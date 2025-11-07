from .http_sensor import HttpSensor
from .sensor_description import SensorDescription, ConnectionType
from fpf_sensor_service.scripts_base import FieldDescription, FieldType, ValidHttpEndpointRule


class HttpHaoshi101PhSensor(HttpSensor):
    @staticmethod
    def get_description() -> SensorDescription:
        return SensorDescription(
            script_class_id='a7552f08-427e-43f7-b07e-850db607db81',
            model='Haoshi101',
            connection=ConnectionType.HTTP,
            parameter='pH;pH-Wert',
            unit='pH',
            tags={},
            fields=[
                FieldDescription(
                    id='',
                    name='http',
                    description='',
                    type=FieldType.STRING,
                    rules=[
                        ValidHttpEndpointRule(),
                    ]
                ),
            ]
        )
