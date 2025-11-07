from fpf_sensor_service.scripts_base import TypedScript, ScriptType
from .action_script_description import ActionScriptDescription


class ActionScript(TypedScript):
    @staticmethod
    def get_script_type() -> ScriptType:
        return ScriptType.ACTION

    def init_additional_information(self):
        pass

    @staticmethod
    def get_description() -> ActionScriptDescription:
        pass

    def run(self, payload=None) -> any:
        """
        :param payload: The action value
        """
        pass
