from attr import dataclass

from fpf_sensor_service.scripts_base import ScriptDescription


@dataclass
class ActionScriptDescription(ScriptDescription):
    name: str
    description: str
    action_values: list[str]
