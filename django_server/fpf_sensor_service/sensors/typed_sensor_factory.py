from typing import Type

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

    def get_available_sensor_types(self) -> list[SensorDescription]:
        return [
            sensor_class.get_description() for sensor_class in self.registry.values()
        ]

    def get_typed_sensor(self, sensor_model: SensorConfig) -> TypedSensor:
        return self.registry[str(sensor_model.sensorClassId)](sensor_model)

    def get_typed_sensor_class(self, sensor_class_id: str) -> Type[TypedSensor]:
        print(self.registry)
        return self.registry[sensor_class_id]
