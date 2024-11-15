from fpf_sensor_service.sensors.typed_sensor import TypedSensor
from fpf_sensor_service.models import SensorConfig


class TypedSensorFactory:
    registry = {}

    def __init__(self, **kwargs):
        for sensor_class in TypedSensor.__subclasses__():
            connection_type = sensor_class.get_connection_type()
            if connection_type in self.registry:
                raise Exception("Multiple typed sensors for same connection_type detected!!")

            self.registry[connection_type] = sensor_class

    def get_available_sensor_types(self):
        return {
            connection_type: sensor_class.get_required_fields() for connection_type, sensor_class in self.registry
        }

    def get_typed_sensor(self, sensor_model: SensorConfig) -> TypedSensor:
        return self.registry[sensor_model.sensorConnectionType](sensor_model)
