from enum import Enum

from rest_framework import serializers

from fpf_sensor_service.sensors.typed_sensor import FieldType, ConnectionType, SensorDescription, IntRangeRuleInclusive
from fpf_sensor_service.utils import is_named_tuple


class EnumField(serializers.ChoiceField):
    def __init__(self, enum_class: Enum, **kwargs):
        self.enum_class = enum_class
        choices = [(tag.name, tag.value) for tag in enum_class]
        super().__init__(choices=choices, **kwargs)

    def to_representation(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        return obj

    def to_internal_value(self, data):
        try:
            return self.enum_class(data)
        except ValueError:
            self.fail('invalid_choice', input=data)


class IntRangeRuleSerializer(serializers.Serializer):
    class Meta:
        model = IntRangeRuleInclusive
        fields = '__all__'


class FieldDescriptionSerializer(serializers.Serializer):
    name = serializers.CharField()
    type = EnumField(enum_class=FieldType)
    rules = serializers.SerializerMethodField()

    def get_rules(self, obj):
        data = []
        for rule in obj.rules:
            if is_named_tuple(rule):
                payload = { 'name': type(rule).__name__ }
                for name, value in rule._asdict().items():
                    payload[name] = value # UNSAFE FOR LISTS!! gotta unroll these too ig
                data.append(payload)

        return data


class SensorDescriptionSerializer(serializers.Serializer):
    sensorClassId = serializers.CharField(source="sensor_class_id")
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