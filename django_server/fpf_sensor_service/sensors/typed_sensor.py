from abc import ABC, abstractmethod

from fpf_sensor_service.models import SensorConfig, SensorMeasurement
from .sensor_description import SensorDescription
from fpf_sensor_service.utils import ListableEnum


class SensorType(ListableEnum):
    Sensor = 'sensor'
    Camera = 'camera'


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

    @staticmethod
    def get_type() -> SensorType:
        return SensorType.Sensor

    @abstractmethod
    def get_measurement(self, payload=None) -> SensorMeasurement:
        pass
