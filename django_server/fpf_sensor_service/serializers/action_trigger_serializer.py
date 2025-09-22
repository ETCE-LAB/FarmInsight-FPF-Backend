from rest_framework import serializers
from fpf_sensor_service.models import ActionTrigger, Action, ActionQueue


class ActionTriggerSerializer(serializers.ModelSerializer):
    actionId = serializers.PrimaryKeyRelatedField(
        source='action',
        queryset=Action.objects.all()
    )
    lastTriggered = serializers.SerializerMethodField()

    class Meta:
        model = ActionTrigger
        read_only_fields = ['id',
                            'actionId'
                            ]
        fields = ['id',
                  'type',
                  'actionValueType',
                  'actionValue',
                  'triggerLogic',
                  'isActive',
                  'description',
                  'actionId',
                  'lastTriggered'
                  ]

    def get_lastTriggered(self, obj):
        latest_entry = ActionQueue.objects.filter(
            trigger__id=obj.id
        ).order_by('-createdAt').first()

        if latest_entry:
            return latest_entry.createdAt

        return None


class ActionTriggerTechnicalKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = ActionTrigger
        fields = ['description', 'actionValueType', 'actionValue']
