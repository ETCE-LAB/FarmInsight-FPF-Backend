import random

import requests
from apscheduler.schedulers.background import BackgroundScheduler

from django_server import settings
from fpf_sensor_service.models import SensorConfig, SensorMeasurement
from fpf_sensor_service.sensors import TypedSensor, TypedSensorFactory
from fpf_sensor_service.utils import get_logger


logger = get_logger()
scheduler = BackgroundScheduler()
typed_sensor_factory = TypedSensorFactory()


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
        response = requests.post(url, json=data)

        if response.status_code == 201:
            measurements.delete()
        else:
            logger.info('Error sending measurements, will retry.')


def schedule_task(sensor: TypedSensor):
    """
    Function to trigger the measurement of the sensor and to send existing measurements.
    Gets called at the configured interval for the sensor.
    :param sensor: Sensor of which values are to be processed.
    """
    logger.debug(f"Task triggered for sensor: {sensor.sensor_config.id}")
    try:
        if settings.GENERATE_MEASUREMENTS:
            value = random.uniform(20.0, 100.0)
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


    sensor_class = typed_sensor_factory.get_typed_sensor_class(str(sensor_config.sensorClassId))
    sensor = sensor_class(sensor_config)

    job = scheduler.get_job(job_id)
    if job:
        scheduler.remove_job(job_id)

    schedule_task(sensor)


def add_scheduler_task(sensor_config: SensorConfig):
    sensor_class = typed_sensor_factory.get_typed_sensor_class(str(sensor_config.sensorClassId))
    sensor = sensor_class(sensor_config)
    scheduler.add_job(
        schedule_task,
        trigger='interval',
        seconds=sensor_config.intervalSeconds,
        args=[sensor],
        id=f"sensor_{sensor_config.id}"
    )


def start_scheduler():
    """
    Get all sensor configurations from sqlite db and schedule jobs based on set intervals.
    """
    sensors = SensorConfig.objects.all()
    logger.debug(f"Following sensors are configured: {sensors}")
    for sensor in sensors:
        add_scheduler_task(sensor)
        logger.info(f"Scheduled task for sensor: {sensor.id}")

    scheduler.start()


def stop_scheduler():
    """
    Stop the scheduler
    """
    scheduler.shutdown()
    logger.debug("APScheduler shutdown")
