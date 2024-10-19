from django.core.management.base import BaseCommand
from fpf_sensor_service.scheduler import start_scheduler


class Command(BaseCommand):
    """
    Used to manually start the APScheduler with "python manage.py scheduler"
    """
    help = 'Starts the APScheduler for sensor data collection manually'

    def handle(self, *args, **kwargs):
        start_scheduler()
        self.stdout.write(self.style.SUCCESS('APScheduler started manually'))
