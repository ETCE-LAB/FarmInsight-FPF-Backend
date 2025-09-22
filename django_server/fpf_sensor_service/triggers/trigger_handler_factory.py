from fpf_sensor_service.models import ActionTrigger
from .base_trigger_handlers import BaseTriggerHandler
from .interval_trigger_handler import IntervalTriggerHandler
from .manual_trigger_handler import ManualTriggerHandler
from .measurement_trigger_handler import MeasurementTriggerHandler
from .time_of_day_trigger_handler import TimeOfDayTriggerHandler


class TriggerHandlerFactory:
    handlers = {
        "manual": ManualTriggerHandler,
        "timeOfDay": TimeOfDayTriggerHandler,
        "sensorValue": MeasurementTriggerHandler,
        "interval": IntervalTriggerHandler,
    }

    @staticmethod
    def get_handler(trigger: ActionTrigger) -> BaseTriggerHandler:
        handler_class = TriggerHandlerFactory.handlers.get(trigger.type)
        if not handler_class:
            raise NotImplementedError(f"No handler found for trigger type: {trigger.type}")
        return handler_class(trigger)
