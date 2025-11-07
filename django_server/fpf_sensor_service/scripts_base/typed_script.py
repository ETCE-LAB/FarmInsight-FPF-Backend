from abc import ABC, abstractmethod

from django.db.models import Model

from fpf_sensor_service.utils import ListableEnum
from .script_description import ScriptDescription


class ScriptType(ListableEnum):
    ACTION = 'action'
    SENSOR = 'sensor'
    CAMERA = 'camera'
    PING = 'ping'


class TypedScript(ABC):
    def __init__(self, model: Model):
        self.model = model
        self.init_additional_information()

    '''
    The idea is for things to happen in order (action chains)
    for example: turn on camera, ping it to see if it's online, take image, turn camera off
    it'll be way easier if all scripts have the same base class to access them, but then to correctly use them 
    and avoid having the control flow too obscured and keeping the ability to easily pause/continue a chain. 
    '''
    @staticmethod
    @abstractmethod
    def get_script_type() -> ScriptType:
        pass

    @abstractmethod
    def init_additional_information(self):
        pass

    '''
    Important! Since every type of script will likely use a different ScriptDescription subclass for simplicity
    we would not be able to send all script types at once to the frontend with the same serializer.
    But since the frontend also needs to know the static parameters anyway this should not be a concern.
    Just to remember if we want to have all types of scripts to run each set through their own serializer.
    Unless we consider to unify those too but that doesn't seem worth it. 
    '''
    @staticmethod
    @abstractmethod
    def get_description() -> ScriptDescription:
        pass

    '''
    Actions return nothing.
    Sensors a MeasurementResult.
    Cameras an image.
    Pings a boolean.
    '''
    @abstractmethod
    def run(self, payload=None) -> any:
        pass
