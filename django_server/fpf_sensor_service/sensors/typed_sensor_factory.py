from typing import Type

from fpf_sensor_service.scripts_base import TypedScript, ScriptType
from fpf_sensor_service.sensors.typed_sensor import SensorDescription
from fpf_sensor_service.models import SensorConfig


def all_subclasses(cls):
    # Required to also handle deeper subclasses!
    return set(cls.__subclasses__()).union(
        [s for c in cls.__subclasses__() for s in all_subclasses(c)])


class TypedSensorFactory:
    registry = None

    # lazy initializing the registry. The factory is usually used as a file wide variable so it is created once at load
    # and avoids doing this reflection loop every call. BUT this can create issues with load order since we have scripts
    # in multiple modules it can happen that some end up missed.
    # So I changed it to lazy initialize on first use, that way we only pay the cost once but are sure to have every
    # module already loaded and not risk inconsistencies.
    def init(self):
        if self.registry is None:
            self.registry = {}
            for sensor_class in all_subclasses(TypedScript):
                if sensor_class.get_script_type() in [ScriptType.SENSOR, ScriptType.CAMERA]:
                    description = sensor_class.get_description()
                    if not description:
                        continue

                    if description.script_class_id in self.registry:
                        raise Exception("Multiple typed sensors with the same id detected!!")

                    self.registry[description.script_class_id] = sensor_class

    def get_registry(self):
        self.init()
        return self.registry

    # We want the camera to be in the registry so the serializer can find it for serialisation, even though rn we don't use it yet for the frontend
    # but this way we are preparing for different camera approaches later and also having it be in line with the sensors
    def get_available_sensor_types(self) -> list[SensorDescription]:
        self.init()
        return [
            sensor_class.get_description() for sensor_class in self.registry.values() if sensor_class.get_script_type() == ScriptType.SENSOR
        ]

    def get_typed_sensor(self, sensor_model: SensorConfig) -> TypedScript:
        self.init()
        return self.registry[str(sensor_model.sensorClassId)](sensor_model)

    def get_typed_sensor_class(self, script_class_id: str) -> Type[TypedScript]:
        self.init()
        return self.registry[script_class_id]
