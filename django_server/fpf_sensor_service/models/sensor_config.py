from django.db import models


class SensorConfig(models.Model):
    """
    The ID is provided by the backend!
    """
    id = models.UUIDField(primary_key=True, editable=False)
    intervalSeconds = models.IntegerField(blank=False)
    sensorClassId = models.UUIDField()
    isActive = models.BooleanField(default=True)
    additionalInformation = models.TextField(blank=True)

    def __str__(self):
        return f'ID: {self.id} class: {self.sensorClassId} interval seconds: {self.intervalSeconds} additional: {self.additionalInformation}'