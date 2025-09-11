from typing import Type

from fpf_sensor_service.sensors import SensorType
from fpf_sensor_service.sensors.typed_sensor import TypedSensor, SensorDescription
from fpf_sensor_service.models import SensorConfig


def all_subclasses(cls):
    # Required to also handle deeper subclasses!
    return set(cls.__subclasses__()).union(
        [s for c in cls.__subclasses__() for s in all_subclasses(c)])


class TypedSensorFactory:
    registry = None

    def __init__(self, **kwargs):
        if self.registry is None:
            self.registry = {}
            for sensor_class in all_subclasses(TypedSensor):
                description = sensor_class.get_description()
                if description.sensor_class_id in self.registry:
                    raise Exception("Multiple typed sensors with the same id detected!!")

                self.registry[description.sensor_class_id] = sensor_class

    # We want the camera to be in the registry so the serializer can find it for serialisation, even though rn we don't use it yet for the frontend
    # but this way we are preparing for different camera approaches later and also having it be in line with the sensors
    def get_available_sensor_types(self) -> list[SensorDescription]:
        return [
            sensor_class.get_description() for sensor_class in self.registry.values() if sensor_class.get_type() == SensorType.Sensor
        ]

    def get_typed_sensor(self, sensor_model: SensorConfig) -> TypedSensor:
        return self.registry[str(sensor_model.sensorClassId)](sensor_model)

    def get_typed_sensor_class(self, sensor_class_id: str) -> Type[TypedSensor]:
        return self.registry[sensor_class_id]
