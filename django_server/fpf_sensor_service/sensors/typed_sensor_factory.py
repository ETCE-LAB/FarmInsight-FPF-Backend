from typing import Type

from fpf_sensor_service.sensors.typed_sensor import TypedSensor
from fpf_sensor_service.models import SensorConfig
from fpf_sensor_service.serializers.sensor_description_serializer import SensorDescriptionSerializer


class TypedSensorFactory:
    registry = {}

    def __init__(self, **kwargs):
        for sensor_class in TypedSensor.__subclasses__():
            description = sensor_class.get_description()
            if description.id in self.registry:
                raise Exception("Multiple typed sensors with the same id detected!!")

            self.registry[description.id] = sensor_class

    def get_available_sensor_types(self) -> list[dict[str, any]]:
        return [
            SensorDescriptionSerializer(sensor_class.get_description()).data for class_id, sensor_class in self.registry.items()
        ]

    def get_typed_sensor(self, sensor_model: SensorConfig) -> TypedSensor:
        return self.registry[sensor_model.sensorClassId](sensor_model)

    def get_typed_sensor_class(self, sensor_class_id: str) -> Type[TypedSensor]:
        return self.registry[sensor_class_id]
