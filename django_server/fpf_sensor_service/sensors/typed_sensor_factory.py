from typing import Type

from fpf_sensor_service.sensors.typed_sensor import TypedSensor, SensorDescription
from fpf_sensor_service.models import SensorConfig
from fpf_sensor_service.serializers.sensor_description_serializer import SensorDescriptionSerializer


class TypedSensorFactory:
    def __init__(self, **kwargs):
        self.registry = {}
        for sensor_class in TypedSensor.__subclasses__():
            description = sensor_class.get_description()
            if description.id in self.registry:
                raise Exception("Multiple typed sensors with the same id detected!!")

            self.registry[description.id] = sensor_class

    def get_available_sensor_types(self) -> list[SensorDescription]:
        return [
            sensor_class.get_description() for sensor_class in self.registry.values()
        ]

    def get_typed_sensor(self, sensor_model: SensorConfig) -> TypedSensor:
        return self.registry[str(sensor_model.sensorClassId)](sensor_model)

    def get_typed_sensor_class(self, sensor_class_id: str) -> Type[TypedSensor]:
        return self.registry[sensor_class_id]
