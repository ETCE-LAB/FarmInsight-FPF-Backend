from rest_framework import serializers

from fpf_sensor_service.action_scripts.action_script_description import ActionScriptDescription
from .description_field_serializer import FieldDescriptionSerializer


class ActionScriptDescriptionSerializer(serializers.Serializer):
    action_script_class_id = serializers.CharField(source='script_class_id')
    name = serializers.CharField()
    description = serializers.CharField()
    has_action_value = serializers.BooleanField()
    action_values = serializers.ListField(
        child=serializers.CharField()
    )
    fields = FieldDescriptionSerializer(many=True)

    def create(self, validated_data):
        return ActionScriptDescription(**validated_data)

    def update(self, instance, validated_data):
        return ActionScriptDescription(**validated_data)

