import json
import uuid

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from fpf_sensor_service.models.sensor_config import SensorConfig
from fpf_sensor_service.sensors import typed_sensor_factory
from fpf_sensor_service.sensors.typed_sensor import FieldType, IntRangeRuleInclusive
from fpf_sensor_service.utils import is_uuid


class JSONStringField(serializers.Field):
    def to_representation(self, obj):
        if isinstance(obj, str) and obj:
            return json.loads(obj)
        return {}

    def to_internal_value(self, data):
        if isinstance(data, dict):
            return json.dumps(data)
        raise serializers.ValidationError("Invalid format. Must be a dictionary.")


class SensorConfigSerializer(serializers.ModelSerializer):
    additionalInformation = JSONStringField()

    class Meta:
        model = SensorConfig
        fields = ['id', 'intervalSeconds', 'sensorClassId', 'additionalInformation']

    def validate_intervalSeconds(self, value):
        """Ensure intervalSeconds is greater than 0."""
        if value <= 0:
            raise serializers.ValidationError("intervalSeconds must be greater than 0.")
        return value

    def validate_sensorClassId(self, value):
        if not str(value) in typed_sensor_factory.registry:
            raise serializers.ValidationError("selected sensor is not registered in FPF Backend.")

        return value

    def validate(self, data):
        sensor_description = typed_sensor_factory.get_typed_sensor_class(str(data['sensorClassId'])).get_description()
        for field in sensor_description.fields:
            additional_information = json.loads(data['additionalInformation'])
            if not field.name in additional_information:
                raise ValidationError({ field.name: 'required field is missing.'})

            value = additional_information[field.name]
            if field.type == FieldType.INTEGER:
                if isinstance(value, str):
                    try:
                        value = int(value)
                    except ValueError:
                        raise ValidationError({field.name: 'invalid integer number.'})

                if not isinstance(value, int):
                    raise ValidationError({field.name: 'invalid integer number.'})

            for rule in field.rules:
                if isinstance(rule, IntRangeRuleInclusive):
                    if value < rule.min or value > rule.max:
                        raise ValidationError({field.name: f'pin value out of range ({rule.min}, {rule.max}).'})
        return data
