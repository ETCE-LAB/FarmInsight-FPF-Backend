from fpf_sensor_service.triggers import BaseTriggerHandler


class ManualTriggerHandler(BaseTriggerHandler):
    def should_trigger(self):
        # Manual triggers are always ready when created
        return True

    def enqueue_if_needed(self):
        pass
