import uuid
from django.db import models
from fpf_sensor_service.utils import ListableEnum


class SensorConnectionTypes(ListableEnum):
    PinConnection = 'PinConnection'
    PicoConnection = 'PicoConnection'
    FarmbotApiConnection = 'FarmbotApiConnection'


class SensorConfig(models.Model):
    """
    SensorConfig model with the id as a GUID and the intervall as an Integer
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    intervalSeconds = models.IntegerField(required=True)
    sensorConnectionType = models.CharField(required=True, choices=SensorConnectionTypes.list())
