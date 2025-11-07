from datetime import timedelta

from django.utils import timezone
from apscheduler.schedulers.background import BackgroundScheduler

from fpf_sensor_service.models import SensorConfig
from fpf_sensor_service.sensors import TypedSensorFactory
from fpf_sensor_service.sensors.sensor_description import ConnectionType
from fpf_sensor_service.utils import get_logger
from .auth_services import get_or_request_api_key, get_fpf_id
from .sensor_services import sensor_task
from .camera_services import camera_task
from .data_retention_services import DataRetentionScheduler
from .auto_trigger_scheduler_services import AutoTriggerScheduler
from fpf_sensor_service.triggers import MeasurementTriggerManager
from fpf_sensor_service.scripts_base import ScriptType


logger = get_logger()
'''
daemon=False is required in deployment to run correctly as a systemd service,
but it does not play nice with running it in the IDE during development. 
DO NOT OVERRIDE WHEN MERGING INTO DEPLOYMENT! 
'''
scheduler = BackgroundScheduler() # daemon=False)
typed_sensor_factory = TypedSensorFactory()


def reschedule_task(sensor_config: SensorConfig, instances: int):
    job_id = f"sensor_{sensor_config.id}"
    job = scheduler.get_job(job_id)
    if job:
        scheduler.remove_job(job_id)

    if sensor_config.isActive:
        add_scheduler_task(sensor_config, instances, 1)


def add_scheduler_task(sensor_config: SensorConfig, instances: int, i: int):
    sensor_class = typed_sensor_factory.get_typed_sensor_class(str(sensor_config.sensorClassId))
    sensor = sensor_class(sensor_config)

    # Don't add MQTT sensor tasks to the scheduler
    if sensor_class.get_script_type() == ScriptType.SENSOR and sensor.get_description().connection != ConnectionType.MQTT:
        scheduler.add_job(
            sensor_task,
            trigger='interval',
            seconds=sensor_config.intervalSeconds,
            args=[sensor],
            id=f"sensor_{sensor_config.id}",
            next_run_time=timezone.now() + timedelta(seconds=i),
            max_instances=instances+1  # "for this job" reads like this wouldn't help but let's try anyway
        )
    elif sensor_class.get_script_type() == ScriptType.CAMERA:
        scheduler.add_job(
            camera_task,
            trigger='interval',
            seconds=sensor_config.intervalSeconds,
            args=[sensor],
            id=f"sensor_{sensor_config.id}",
            next_run_time=timezone.now() + timedelta(seconds=i),
            max_instances=instances + 1  # "for this job" reads like this wouldn't help but let's try anyway
        )

def start_scheduler():
    """
    Get all sensor configurations from sqlite db and schedule jobs based on set intervals.
    """
    sensors = SensorConfig.objects.all()
    instances = len(sensors)
    logger.debug(f"Following sensors are configured: {sensors}", extra={'extra': {'fpfId': get_fpf_id(), 'api_key': get_or_request_api_key()}})
    i = 0
    for sensor in sensors:
        if sensor.isActive:
            i += 5
            add_scheduler_task(sensor, instances, i)
            logger.debug(f"Scheduled task every {sensor.intervalSeconds}s", extra={'extra': {'sensorId': sensor.id, 'api_key': get_or_request_api_key()}})
        else:
            logger.debug(f"Skipped scheduling task", extra={'extra': {'sensorId': sensor.id, 'api_key': get_or_request_api_key()}})

    scheduler.start()

    DataRetentionScheduler.get_instance().start()
    AutoTriggerScheduler.get_instance().start()
    MeasurementTriggerManager.build_trigger_mapping()


def stop_scheduler():
    """
    Stop the scheduler
    """
    scheduler.shutdown()
    logger.debug("APScheduler shutdown", extra={'extra': {'fpfId': get_fpf_id(), 'api_key': get_or_request_api_key()}})
