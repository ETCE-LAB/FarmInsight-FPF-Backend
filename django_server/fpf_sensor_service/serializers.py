from rest_framework import serializers
from .models import SensorConfig


class SensorConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorConfig
        fields = ['sensorId', 'intervallSeconds']
