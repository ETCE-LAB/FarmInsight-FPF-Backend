from rest_framework import serializers
from fpf_sensor_service.models import Action, Hardware, ActionQueue
from .hardware_serializer import HardwareSerializer
from .action_trigger_serializer import ActionTriggerSerializer


class ActionSerializer(serializers.ModelSerializer):
    """
    Provides data to the frontend rendering
    """
    hardwareId = serializers.PrimaryKeyRelatedField(
        source='hardware',
        queryset=Hardware.objects.all(),
        required=False,
        allow_null=True
    )
    hardware = HardwareSerializer(read_only=True)

    trigger = ActionTriggerSerializer(many=True, source='triggers', read_only=True, required=False)
    actionScriptName = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Action
        fields = [
            'id',
            'name',
            'actionClassId',
            'actionScriptName',
            'isActive',
            'isAutomated',
            'maximumDurationSeconds',
            'additionalInformation',
            'hardwareId',
            'hardware',
            'trigger',
            'status',
            'orderIndex',
        ]

    def get_status(self, obj):
        latest_entry = ActionQueue.objects.filter(
            action__id=obj.id
        ).order_by('-endedAt', '-createdAt').first()

        if latest_entry:
            trigger = latest_entry.trigger
            # Auto mode: use isAutomated on the action
            if obj.isAutomated and trigger.type != 'manual':
                return None  # In auto mode, we return no manual trigger ID
            return str(trigger.id)
        return None

    def get_actionScriptName(self, obj):
        # ...wtf
        from fpf_sensor_service.services.action_queue_services import typed_action_script_factory
        try:
            description = typed_action_script_factory.get_typed_action_script_class(str(obj.actionClassId)).get_description()
            return description.name
        except Exception as e:
            return f"Unknown ({str(e)})"


class ActionTechnicalKeySerializer(serializers.ModelSerializer):
    hardware = HardwareSerializer(read_only=True)

    class Meta:
        model = Action
        fields = [
            'name',
            'isActive',
            'isAutomated',
            'hardware',
        ]
