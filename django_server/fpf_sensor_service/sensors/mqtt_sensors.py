import json

from .measurement_result import MeasurementResult
from .typed_sensor import TypedSensor
from .sensor_description import SensorDescription, ConnectionType, FieldDescription, FieldType, ValidHttpEndpointRule


class MqttSensor(TypedSensor):
    mqtt_topic = None

    def init_additional_information(self):
        additional_information = json.loads(self.sensor_config.additionalInformation)
        self.mqtt_topic = additional_information['mqtt_topic']

    @staticmethod
    def get_description() -> SensorDescription:
        return SensorDescription(
            sensor_class_id='829e8233-b9c3-4f25-97fb-8852f54c8289',
            model='',
            connection=ConnectionType.MQTT,
            parameter='',
            unit='',
            tags={
                'info': 'model, parameter and unit have to be entered manually;Modell, Kennwert und Einheit müssen manuell eingetragen werden',
            },
            fields=[
                FieldDescription(
                    name='mqtt_topic',
                    type=FieldType.STRING,
                    rules=[]
                ),
            ]
        )

    def get_measurement(self, payload) -> MeasurementResult:
        try:
            value = payload['value']
            timestamp = payload.get('timestamp')
            if timestamp is not None:
                return MeasurementResult(value=value, timestamp=timestamp)
            else:
                return MeasurementResult(value=value)

        except (KeyError, json.JSONDecodeError) as e:
            raise ValueError(f"Invalid payload: {e}")

