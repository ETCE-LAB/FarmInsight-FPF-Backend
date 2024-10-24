from django.apps import AppConfig
import logging


class SensorAppConfig(AppConfig):
    name = 'fpf_sensor_service'

    def ready(self):
        """
        On Django server start, start the scheduler
        """
        from fpf_sensor_service.scheduler import start_scheduler

        try:
            logging.info("Starting APScheduler via AppConfig...")
            start_scheduler()
        except Exception as e:
            logging.error(f"Failed to start APScheduler: {e}")
