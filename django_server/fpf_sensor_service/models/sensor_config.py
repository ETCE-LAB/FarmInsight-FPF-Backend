import uuid
from django.db import models


class SensorConfig(models.Model):
    """
    SensorConfig model with the id as a GUID and the intervall as an Integer
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    intervalSeconds = models.IntegerField()
