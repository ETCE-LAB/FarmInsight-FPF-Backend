import json
from datetime import datetime

from fpf_sensor_service.utils import get_logger
from fpf_sensor_service.serializers import ActionQueueSerializer
from fpf_sensor_service.triggers import BaseTriggerHandler


logger = get_logger()


class TimeOfDayTriggerHandler(BaseTriggerHandler):
    def should_trigger(self):
        try:
            logic = json.loads(self.trigger.triggerLogic)
            now = datetime.now().time()

            from_time = datetime.strptime(logic["from"], "%H:%M").time()
            to_time = datetime.strptime(logic["to"], "%H:%M").time()

            # Handle range that crosses midnight
            if from_time <= to_time:
                in_range = from_time <= now <= to_time
            else:
                # e.g., 23:00 to 03:00
                in_range = now >= from_time or now <= to_time

            return in_range
        except Exception as e:
            return False

    def enqueue_if_needed(self):
        from fpf_sensor_service.services import is_new_action
        if self.should_trigger() and self.trigger.action.isAutomated and self.trigger.action.isActive:
            if is_new_action(self.trigger.action.id, self.trigger.id):
                if self.trigger.action.nextAction is None:
                    serializer = ActionQueueSerializer(data={
                        "actionId": str(self.trigger.action.id),
                        "actionTriggerId": str(self.trigger.id),
                        "value": self.trigger.actionValue,
                    }, partial=True)
                    if serializer.is_valid(raise_exception=True):
                        serializer.save()
                        logger.info(f"Queued by timeOfDay trigger {self.trigger.description} with value {self.trigger.actionValue}", extra={'action_id': self.trigger.action.id})
                else:
                    BaseTriggerHandler.enqueue_chained_actions(self.trigger, self.trigger.action, None, self.trigger.actionValue.split(";"), 0, 'timeOfDay')
