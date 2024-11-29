from django.apps import AppConfig
from django.db import connections
from django.db.utils import OperationalError
from django.db.migrations.executor import MigrationExecutor
import threading
import time
import logging
import os


class SensorAppConfig(AppConfig):
    name = 'fpf_sensor_service'
    default_auto_field = 'django.db.models.BigAutoField'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log = logging.getLogger('fpf_sensor_service')

    def check_and_start_scheduler(self, max_retries=3, retry_interval=5):
        """
        :param max_retries: maximum amount of retries to connect to the database
        :param retry_interval: interval of the retry
        """
        retry_count = 0
        while retry_count < max_retries:
            try:
                if self.has_pending_migrations():
                    self.log.warning(f"Pending migrations detected. Retrying in {retry_interval} seconds...")
                    time.sleep(retry_interval)
                    retry_count += 1
                else:
                    self.log.info("Starting APScheduler...")
                    from fpf_sensor_service.services import start_scheduler
                    start_scheduler()
                    self.log.info("APScheduler started successfully.")
                    break
            except OperationalError as e:
                self.log.error(f"Database not ready yet: {e}")
                time.sleep(retry_interval)
                retry_count += 1
            except Exception as e:
                self.log.error(f"Error checking migrations: {e}")
                break
        if retry_count == max_retries:
            self.log.error("Max retries reached. Scheduler did not start.")

    def has_pending_migrations(self) -> bool:
        """
        Check if there are any pending migrations.
        :return: if there are pending migrations
        """
        try:
            executor = MigrationExecutor(connections['default'])
            targets = executor.loader.graph.leaf_nodes()
            pending = executor.migration_plan(targets) != []
            self.log.info(f"Pending migrations: {pending}")
            return pending
        except Exception as e:
            self.log.error(f"Error checking migrations: {e}")
            return True  # Assume pending if there's an error

    def ready(self):
        """
        Start a new thread to check for pending migrations and start the scheduler if ready
        """
        if os.environ.get('RUN_MAIN') == 'true':
            threading.Thread(target=self.check_and_start_scheduler, daemon=True).start()
