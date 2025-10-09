from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound

from fpf_sensor_service.utils import get_logger
from fpf_sensor_service.models import ActionTrigger
from fpf_sensor_service.serializers import ActionTriggerSerializer, ActionQueueSerializer


logger = get_logger()


def create_action_trigger(action_trigger_data: dict) -> ActionTriggerSerializer:
    serializer = ActionTriggerSerializer(data=action_trigger_data, partial=True)
    if serializer.is_valid(raise_exception=True):
        trigger = ActionTrigger(**serializer.validated_data)
        trigger.id = action_trigger_data['id']
        trigger.save()
        return ActionTriggerSerializer(trigger)


def get_action_trigger(action_trigger_id):
    return get_object_or_404(ActionTrigger, pk=action_trigger_id)


def get_all_auto_timeOfDay_action_triggers(action_id=None):
    if not action_id:
        return ActionTrigger.objects.filter(isActive=True).exclude(type='timeOfDay')
    else:
        return ActionTrigger.objects.filter(
            isActive=True,
            action_id=action_id
        ).exclude(type='timeOfDay')


def get_all_auto_interval_triggers(action_id=None):
    if not action_id:
        return ActionTrigger.objects.filter(isActive=True).exclude(type='interval')
    else:
        return ActionTrigger.objects.filter(
            isActive=True,
            action_id=action_id
        ).exclude(type='interval')


def get_all_active_auto_triggers(action_id=None):
    if not action_id:
        return ActionTrigger.objects.filter(isActive=True).exclude(type='manual')
    else:
        return ActionTrigger.objects.filter(
            isActive=True,
            action_id=action_id
        ).exclude(type='manual')


def update_action_trigger(action_trigger_id, data) -> ActionTriggerSerializer:
    try:
        action_trigger = ActionTrigger.objects.get(id=action_trigger_id)
    except ActionTrigger.DoesNotExist:
        raise NotFound()

    data["actionId"] = action_trigger.action_id
    data["id"] = action_trigger_id
    serializer = ActionTriggerSerializer(action_trigger, data=data)

    if serializer.is_valid(raise_exception=True):
        serializer.save()
    return serializer


def create_manual_triggered_action_in_queue(action_id, trigger_id):
    """
    When the user manually selects a manual button in the frontend, the trigger will be activated and
    an entry in the action queue will be created. If no other actions for the same controllable actions are currently
    running.
    :param action_id:
    :param trigger_id:
    :return:
    """
    from fpf_sensor_service.services import process_action_queue, get_action_trigger

    trigger = get_action_trigger(trigger_id)
    if trigger.isActive: #and is_new_action(action_id, trigger.id): Disabled for now.
        # We would need to check all controllable actions with the same hardware in the active state and maybe the
        # user want to trigger a manual action more than once in case of network failure.

        serializer = ActionQueueSerializer(data={
            "actionId": action_id,
            "actionTriggerId": trigger_id,
            "value": trigger.actionValue,
        }, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            logger.info(f"Queued by manual trigger {trigger.description} with value {trigger.actionValue}", extra={'action_id': action_id})

    process_action_queue()
