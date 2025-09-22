from rest_framework import serializers
from fpf_sensor_service.models import ActionQueue, ActionTrigger, Action
from .action_trigger_serializer import ActionTriggerTechnicalKeySerializer
from .action_serializer import ActionTechnicalKeySerializer


class ActionQueueSerializer(serializers.ModelSerializer):
    actionId = serializers.PrimaryKeyRelatedField(
        source='action',
        queryset=Action.objects.all()
    )

    actionTriggerId = serializers.PrimaryKeyRelatedField(
        source='trigger',
        queryset=ActionTrigger.objects.all()
    )

    class Meta:
        model = ActionQueue
        read_only_fields = ['id', 'createdAt', 'actionId', 'actionTriggerId']
        fields = ['id', 'createdAt', 'startedAt', 'endedAt', 'value', 'actionId', 'actionTriggerId']


# This serializer contains more of the data from trigger and action to show in the frontend
class ActionQueueSerializerDescriptive(serializers.ModelSerializer):
    controllableAction = ActionTechnicalKeySerializer(source='action')
    actionTrigger = ActionTriggerTechnicalKeySerializer(source='trigger')

    class Meta:
        model = ActionQueue
        fields = ['id', 'createdAt', 'startedAt', 'endedAt', 'value', 'controllableAction', 'actionTrigger']
