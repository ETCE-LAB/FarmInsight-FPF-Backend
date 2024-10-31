from rest_framework import serializers
from fpf_sensor_service.models.sensor_config import SensorConfig


class SensorConfigSerializer(serializers.ModelSerializer):

    class Meta:
        model = SensorConfig
        fields = ['id', 'intervalSeconds']

    def validate_intervalSeconds(self, value):
        """Ensure intervalSeconds is greater than 0."""
        if value <= 0:
            raise serializers.ValidationError("intervalSeconds must be greater than 0.")
        return value

    def validate(self, data):
        """Ensure intervalSeconds is present in the input data."""
        if 'intervalSeconds' not in data:
            raise serializers.ValidationError({"intervalSeconds": "This field is required."})
        return data
