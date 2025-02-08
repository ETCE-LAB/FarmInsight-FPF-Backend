from abc import ABC, abstractmethod

from fpf_sensor_service.models import SensorConfig
from .sensor_description import SensorDescription


class TypedSensor(ABC):
    def __init__(self, sensor_config: SensorConfig):
        self.sensor_config = sensor_config
        self.init_additional_information()

    @abstractmethod
    def init_additional_information(self):
        pass

    @staticmethod
    @abstractmethod
    def get_description() -> SensorDescription:
        pass

    @abstractmethod
    def get_measurement(self):
        pass
