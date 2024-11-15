from fpf_sensor_service.sensors.typed_sensor import TypedSensor
from fpf_sensor_service.utils import SensorConnectionTypes


class PicoConnectedSensor(TypedSensor):
    @staticmethod
    def get_connection_type():
        return SensorConnectionTypes.PicoConnection

    @staticmethod
    def get_required_fields():
        return {
            'Url': {
                'type': 'string',
                'format': 'ipv4',  # TODO: consider other ways like regex
            }
        }

    def get_measurement(self):
        pass
