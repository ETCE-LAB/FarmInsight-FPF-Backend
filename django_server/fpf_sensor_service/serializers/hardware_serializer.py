from rest_framework import serializers
from fpf_sensor_service.models import Hardware, Action


class HardwareSerializer(serializers.ModelSerializer):
    canBeDeleted = serializers.SerializerMethodField(method_name='can_be_deleted')

    class Meta:
        model = Hardware
        read_only_fields = ('id',)
        fields = '__all__'

    def can_be_deleted(self, obj):
        return Action.objects.filter(hardware=obj).count() == 0