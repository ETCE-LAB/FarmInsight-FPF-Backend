from django.db import models


class SensorConfig(models.Model):
    """
    SensorConfig model with the sensorId as a GUID and the intervall as an Integer
    """
    sensorId = models.CharField(primary_key=True, max_length=36)
    intervallSeconds = models.IntegerField()


class SensorMeasurement(models.Model):
    """
    SensorMeasurement model with the sensorId as a GUID, the measuredAt as a autofilled Date and the value as a float
    """
    sensorId = models.CharField(max_length=36)
    measuredAt = models.DateTimeField(auto_now_add=True)
    value = models.FloatField()
