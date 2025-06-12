import json

import requests

from .measurement_result import MeasurementResult
from .typed_sensor import TypedSensor
from .sensor_description import SensorDescription, ConnectionType, FieldDescription, FieldType, ValidHttpEndpointRule


class HttpMqttSensor(TypedSensor):
    mqtt_topic = None
    http_endpoint = None

    def init_additional_information(self):
        additional_information = json.loads(self.sensor_config.additionalInformation)
        self.mqtt_topic = additional_information['mqtt_topic']
        self.http_endpoint = additional_information['http']

    @staticmethod
    def get_description() -> SensorDescription:
        return SensorDescription(
            sensor_class_id='f631c5fa-e9a0-4b0c-a9f6-75c6b6181f99',
            model='',
            connection=ConnectionType.HTTP_MQTT,
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
                FieldDescription(
                    name='mqtt_topic',
                    type=FieldType.STRING,
                    rules=[]
                ),
            ]
        )

    def get_measurement(self, payload=None) -> MeasurementResult:
        try:
            if payload is not None: # process mqtt
                value = payload['value']
                timestamp = payload.get('timestamp')
                if timestamp is not None:
                    return MeasurementResult(value=value, timestamp=timestamp)
                else:
                    return MeasurementResult(value=value)

            else: #process http
                response = requests.get(self.http_endpoint, timeout=10)
                response.raise_for_status()
                return MeasurementResult(value=response.json().get("value"))

        except Exception as e:
            raise e

