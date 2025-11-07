from rest_framework import serializers

from fpf_sensor_service.sensors.sensor_description import ConnectionType, SensorDescription
from fpf_sensor_service.scripts_base import IntRangeRuleInclusive
from .description_field_serializer import FieldDescriptionSerializer, EnumField


class IntRangeRuleSerializer(serializers.Serializer):
    class Meta:
        model = IntRangeRuleInclusive
        fields = '__all__'


class SensorDescriptionSerializer(serializers.Serializer):
    sensorClassId = serializers.CharField(source='script_class_id')
    model = serializers.CharField()
    connection = EnumField(enum_class=ConnectionType)
    parameter = serializers.CharField()
    unit = serializers.CharField()
    tags = serializers.DictField(child=serializers.CharField())
    fields = FieldDescriptionSerializer(many=True)

    def create(self, validated_data):
        return SensorDescription(**validated_data)

    def update(self, instance, validated_data):
        return SensorDescription(**validated_data)