from fpf_sensor_service.sensors.typed_sensor import TypedSensor
from fpf_sensor_service.utils import SensorConnectionTypes


class PinConnectedSensor(TypedSensor):
    @staticmethod
    def get_connection_type():
        return SensorConnectionTypes.PinConnection

    @staticmethod
    def get_required_fields():
        return {
            'Pin': {
                'Type': 'number',
            }
        }

    def get_measurement(self):
        pass
