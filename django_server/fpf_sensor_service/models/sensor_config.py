import uuid
from django.db import models


class SensorConfig(models.Model):
    """
    The ID is provided by the backend!
    """
    id = models.UUIDField(primary_key=True, editable=False)
    intervalSeconds = models.IntegerField(blank=False)
    sensorClassId = models.UUIDField()
    additionalInformation = models.TextField(blank=True)
