from fpf_sensor_service.scripts_base import TypedScript, ScriptType
from .sensor_description import SensorDescription


class TypedSensor(TypedScript):
    def init_additional_information(self):
        pass

    @staticmethod
    def get_description() -> SensorDescription:
        pass

    @staticmethod
    def get_script_type() -> ScriptType:
        return ScriptType.SENSOR

    def run(self, payload=None) -> any:
        pass
