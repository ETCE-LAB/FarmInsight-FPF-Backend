from fpf_sensor_service.models import ActionTrigger, Action
from fpf_sensor_service.serializers import ActionQueueSerializer
from fpf_sensor_service.utils import get_logger


logger = get_logger()


class BaseTriggerHandler:
    def __init__(self, trigger: ActionTrigger):
        self.trigger = trigger

    def should_trigger(self, *args, **kwargs):
        raise NotImplementedError("Must override should_trigger in subclass.")

    def enqueue_if_needed(self, *args, **kwargs):
        raise NotImplementedError("Must override enqueue in subclass.")

    @staticmethod
    def enqueue_chained_actions(trigger: ActionTrigger, action: Action, depends_on: str|None, trigger_values: [str], index: int, trigger_type: str) -> [dict]:
        # maybe we should be first creating all the serializers at once, and then save once, when they're all valid but ...
        serializer = ActionQueueSerializer(data={
            "actionId": str(action.id),
            "actionTriggerId": str(trigger.id),
            "value": trigger_values[index],
            "dependsOn": depends_on,
        }, partial=True)
        if serializer.is_valid(raise_exception=True):
            entry = serializer.save()
            logger.info(f"Queued by {trigger_type} trigger {trigger.description.split(';')[0]} with value {trigger_values[index]}",
                        extra={'action_id': trigger.action.id})
            if action.nextAction:
                return [serializer.data] + BaseTriggerHandler.enqueue_chained_actions(trigger, action.nextAction, str(entry.id), trigger_values, index+1, trigger_type)
            else:
                return [serializer.data]