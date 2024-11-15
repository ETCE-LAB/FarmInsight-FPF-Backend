import uuid
from django.db import models
from fpf_sensor_service.utils import ListableEnum


class SensorConnectionTypes(ListableEnum):
    PinConnection = 'PinConnection'
    PicoConnection = 'PicoConnection'
    FarmbotApiConnection = 'FarmbotApiConnection'


class SensorConfig(models.Model):
    """
    SensorConfig model with the id as a GUID and the interval as an Integer
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    intervalSeconds = models.IntegerField(blank=False)
    sensorConnectionType = models.CharField(max_length=256, blank=False)
    additionalInformation = models.CharField(blank=True, max_length=1024)
