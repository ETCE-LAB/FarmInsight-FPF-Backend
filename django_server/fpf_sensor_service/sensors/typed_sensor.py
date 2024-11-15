from abc import ABC, abstractmethod

from fpf_sensor_service.models import SensorConfig


class TypedSensor(ABC):
    def __init__(self, sensor_config: SensorConfig):
        self.sensor_config = sensor_config

    @staticmethod
    @abstractmethod
    def get_connection_type():
        pass

    @staticmethod
    @abstractmethod
    def get_required_fields():
        pass

    @abstractmethod
    def get_measurement(self):
        pass
