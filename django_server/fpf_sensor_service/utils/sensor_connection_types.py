from .enum_utils import ListableEnum


class SensorConnectionTypes(ListableEnum):
    PinConnection = 'PinConnection'
    PicoConnection = 'PicoConnection'
    FarmbotApiConnection = 'FarmbotApiConnection'
