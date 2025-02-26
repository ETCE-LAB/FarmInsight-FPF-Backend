import random
import requests
import time
from datetime import timedelta

from django.utils import timezone
from django_server import settings
from apscheduler.schedulers.background import BackgroundScheduler

from fpf_sensor_service.models import SensorConfig, SensorMeasurement, Configuration, ConfigurationKeys
from fpf_sensor_service.sensors import TypedSensor, TypedSensorFactory
from fpf_sensor_service.utils import get_logger


logger = get_logger()
'''
daemon=False is required in deployment to run correctly as a systemd service,
but it play nice with running it in the IDE during development. 
DO NOT OVERRIDE WHEN MERGING INTO DEPLOYMENT! 
'''
scheduler = BackgroundScheduler() # daemon=False)
typed_sensor_factory = TypedSensorFactory()


def request_api_key() -> str or None:
    fpf_config = Configuration.objects.filter(key=ConfigurationKeys.FPF_ID.value).first()
    if not fpf_config:
        logger.error('!!! FPF ID CONFIGURATION LOST, UNABLE TO PROCEED !!!')
        return None

    url = f"{settings.MEASUREMENTS_BASE_URL}/api/fpfs/{fpf_config.value}/api-key"
    response = requests.get(url)
    if response.status_code != 200:
        logger.error('!!! Request for new API Key failed !!!')
        return None
    else:
        api_key = Configuration.objects.filter(key=ConfigurationKeys.API_KEY.value).first()
        if api_key:
            return api_key.value


def get_or_request_api_key() -> str or None:
    api_key = Configuration.objects.filter(key=ConfigurationKeys.API_KEY.value).first()
    if not api_key:
        return request_api_key()
    return api_key.value


def send_measurements(sensor_id):
    """
    For given sensor, try to send all measurements to central app.
    If succeeded, delete entries from local database.
    :param sensor_id: GUID of sensor
    """
    measurements = SensorMeasurement.objects.filter(sensor_id=sensor_id)
    if measurements.exists():
        data = [
            {'measuredAt': m.measuredAt.isoformat(), 'value': m.value}
            for m in measurements
        ]

        url = f"{settings.MEASUREMENTS_BASE_URL}/api/measurements/{sensor_id}"

        api_key = get_or_request_api_key()
        if api_key is not None:
            response = requests.post(url, json=data, headers={
                'Authorization': f'ApiKey {api_key}'
            })

            if response.status_code == 201:
                measurements.delete()
            elif response.status_code == 403:
                request_api_key()
            else:
                logger.info('Error sending measurements, will retry.')


def task(sensor: TypedSensor):
    """
    Function to trigger the measurement of the sensor and to send existing measurements.
    Gets called at the configured interval for the sensor.
    :param sensor: Sensor of which values are to be processed.
    """
    logger.debug(f"Task triggered for sensor: {sensor.sensor_config.id}")
    try:
        if settings.GENERATE_MEASUREMENTS:
            value = random.uniform(20.0, 20.5)
        else:
            value = sensor.get_measurement()

        SensorMeasurement.objects.create(
            sensor_id=sensor.sensor_config.id,
            value=value
        )
        send_measurements(sensor.sensor_config.id)
        logger.debug(f"Task completed for sensor: {sensor.sensor_config.id}")
    except Exception as e:
        logger.error(f"Error processing sensor {sensor.sensor_config.id}: {e}")


def reschedule_task(sensor_config: SensorConfig):
    job_id = f"sensor_{sensor_config.id}"
    job = scheduler.get_job(job_id)
    if job:
        scheduler.remove_job(job_id)

    add_scheduler_task(sensor_config, 1)


def add_scheduler_task(sensor_config: SensorConfig, i):
    sensor_class = typed_sensor_factory.get_typed_sensor_class(str(sensor_config.sensorClassId))
    sensor = sensor_class(sensor_config)
    scheduler.add_job(
        task,
        trigger='interval',
        seconds=sensor_config.intervalSeconds,
        args=[sensor],
        id=f"sensor_{sensor_config.id}",
        next_run_time=timezone.now() + timedelta(seconds=i)
    )


def start_scheduler():
    """
    Get all sensor configurations from sqlite db and schedule jobs based on set intervals.
    """
    sensors = SensorConfig.objects.all()
    logger.debug(f"Following sensors are configured: {sensors}")
    i = 0
    for sensor in sensors:
        i += 5
        add_scheduler_task(sensor, i)
        logger.info(f"Scheduled task for sensor: {sensor.id} every {sensor.intervalSeconds}s")

    scheduler.start()


def stop_scheduler():
    """
    Stop the scheduler
    """
    scheduler.shutdown()
    logger.debug("APScheduler shutdown")
