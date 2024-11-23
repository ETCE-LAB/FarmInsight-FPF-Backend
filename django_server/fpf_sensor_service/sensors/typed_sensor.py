from abc import ABC, abstractmethod
from enum import Enum
from typing import NamedTuple, List

from fpf_sensor_service.models import SensorConfig


class ConnectionType(Enum):
    PIN = 'Pin'
    PICO = 'Pico'
    FARMBOT = 'Farmbot'


class FieldType(Enum):
    INTEGER = 'int'
    FLOAT = 'float'
    STRING = 'str'
    SELECT = 'select'


class IntRangeRuleInclusive(NamedTuple):
    min: int
    max: int


class FieldDescription(NamedTuple):
    name: str
    type: FieldType
    rules: List[object]


class SensorDescription(NamedTuple):
    """
    When creating a sensor class generate a corresponding uuid like so:

    import uuid
    uuid.uuid4()

    !!! NEVER CHANGE OR DELETE THESE, the DB will store them to identify the class !!!
    """
    id: str
    name: str
    connection: ConnectionType
    parameter: str
    tags: dict[str, str]
    fields: List[FieldDescription]


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
