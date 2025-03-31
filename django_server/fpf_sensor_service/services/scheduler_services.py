import random
import requests
from datetime import timedelta

from django.utils import timezone
from django_server import settings
from apscheduler.schedulers.background import BackgroundScheduler

from fpf_sensor_service.models import SensorConfig, SensorMeasurement, Configuration, ConfigurationKeys
from fpf_sensor_service.sensors import TypedSensor, TypedSensorFactory, MeasurementResult
from fpf_sensor_service.utils import get_logger


logger = get_logger()
'''
daemon=False is required in deployment to run correctly as a systemd service,
but it does not play nice with running it in the IDE during development. 
DO NOT OVERRIDE WHEN MERGING INTO DEPLOYMENT! 
'''
scheduler = BackgroundScheduler() # daemon=False)
typed_sensor_factory = TypedSensorFactory()


def get_fpf_id() -> str or None:
    fpf_config = Configuration.objects.filter(key=ConfigurationKeys.FPF_ID.value).first()
    if not fpf_config:
        logger.debug('!!! FPF ID CONFIGURATION LOST, UNABLE TO PROCEED !!!')
        return None
    return fpf_config.value


def request_api_key() -> str or None:
    fpf_id = get_fpf_id()
    if fpf_id is None:
        return None

    url = f"{settings.MEASUREMENTS_BASE_URL}/api/fpfs/{fpf_id}/api-key"
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
                logger.debug('Successfully sent measurements.', extra={'extra': {'fpfId': get_fpf_id(), 'sensorId': sensor_id, 'api_key': api_key}})
            elif response.status_code == 403:
                request_api_key()
            else:
                logger.error('Error sending measurements, will retry.', extra={'extra': {'fpfId': get_fpf_id(), 'sensorId': sensor_id, 'api_key': api_key}})


def task(sensor: TypedSensor):
    """
    Function to trigger the measurement of the sensor and to send existing measurements.
    Gets called at the configured interval for the sensor.
    :param sensor: Sensor of which values are to be processed.
    """
    logger.debug("Sensor task triggered", extra={'extra': {'fpfId': get_fpf_id(), 'sensorId': sensor.sensor_config.id, 'api_key': get_or_request_api_key()}})
    try:
        if settings.GENERATE_MEASUREMENTS:
            result = MeasurementResult(value=random.uniform(20.0, 20.5))
        else:
            result = sensor.get_measurement()

        SensorMeasurement.objects.create(
            sensor_id=sensor.sensor_config.id,
            value=result.value,
            measuredAt=result.timestamp
        )
        send_measurements(sensor.sensor_config.id)
        logger.debug("Sensor Task completed", extra={'extra': {'fpfId': get_fpf_id(), 'sensorId': sensor.sensor_config.id, 'api_key': get_or_request_api_key()}})
    except Exception as e:
        logger.error(f"Error processing sensor: {e}", extra={'extra': {'fpfId': get_fpf_id(), 'sensorId': sensor.sensor_config.id, 'api_key': get_or_request_api_key()}})


def reschedule_task(sensor_config: SensorConfig):
    job_id = f"sensor_{sensor_config.id}"
    job = scheduler.get_job(job_id)
    if job:
        scheduler.remove_job(job_id)

    if sensor_config.isActive:
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
    logger.debug(f"Following sensors are configured: {sensors}", extra={'extra': {'fpfId': get_fpf_id(), 'api_key': get_or_request_api_key()}})
    i = 0
    for sensor in sensors:
        if sensor.isActive:
            i += 5
            add_scheduler_task(sensor, i)
            logger.debug(f"Scheduled task every {sensor.intervalSeconds}s", extra={
                'extra': {'fpfId': get_fpf_id(), 'sensorId': sensor.id, 'api_key': get_or_request_api_key()}})
        else:
            logger.debug(f"Skipped scheduling task", extra={
                'extra': {'fpfId': get_fpf_id(), 'sensorId': sensor.id, 'api_key': get_or_request_api_key()}})

    scheduler.start()


def stop_scheduler():
    """
    Stop the scheduler
    """
    scheduler.shutdown()
    logger.debug("APScheduler shutdown", extra={'extra': {'fpfId': get_fpf_id(), 'api_key': get_or_request_api_key()}})
