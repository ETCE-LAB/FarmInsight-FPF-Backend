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

    def enqueue_chained_actions(self, action: Action):
        # maybe we should be first creating all the serializers at once, and then save once, when they're all valid but ...
        serializer = ActionQueueSerializer(data={
            "actionId": str(action.nextAction),
            "actionTriggerId": str(self.trigger.id),
            "value": self.trigger.actionValue,
        }, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            logger.info(f"Queued by timeOfDay trigger {self.trigger.description} with value {self.trigger.actionValue}",
                        extra={'action_id': self.trigger.action.id})
