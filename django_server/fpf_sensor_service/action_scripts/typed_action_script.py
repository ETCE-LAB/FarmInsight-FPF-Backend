from abc import ABC, abstractmethod

from .action_script_description import ActionScriptDescription
from fpf_sensor_service.models import Action


class ActionScript(ABC):
    def __init__(self, action: Action):
        self.action = action
        self.init_additional_information()

    @abstractmethod
    def init_additional_information(self):
        pass

    @staticmethod
    @abstractmethod
    def get_description() -> ActionScriptDescription:
        pass

    @abstractmethod
    def run(self, action_value):
        pass
