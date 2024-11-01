from apscheduler.schedulers.background import BackgroundScheduler
from fpf_sensor_service.models import SensorConfig
from fpf_sensor_service.tasks import generate_measurement, send_measurements
from fpf_sensor_service.utils.logging_utils import get_logger

logger = get_logger()
scheduler = BackgroundScheduler()


def schedule_sensor_task(sensor):
    """
    Function to trigger the measurement of the sensor and to send existing measurements.
    Gets called at the configured interval for the sensor.
    :param sensor: Sensor of which values are to be processed.
    """
    logger.debug(f"Task triggered for sensor: {sensor.id}")
    try:
        generate_measurement(sensor)
        send_measurements(sensor.id)
        logger.info(f"Task completed for sensor: {sensor.id}")
    except Exception as e:
        logger.error(f"Error processing sensor {sensor.id}: {e}")


def start_scheduler():
    """
    Get all sensor configurations from sqlite db and schedule jobs based on set intervalls.
    """
    sensors = SensorConfig.objects.all()
    logger.debug(f"Following sensors are configured: {sensors}")
    for sensor in sensors:
        scheduler.add_job(
            schedule_sensor_task,
            'interval',
            seconds=sensor.intervalSeconds,
            args=[sensor],
            id=f"sensor_{sensor.id}"
        )
        logger.info(f"Scheduled task for sensor: {sensor.id}")

    scheduler.start()


def stop_scheduler():
    """
    Stop the scheduler
    """
    scheduler.shutdown()
    logger.debug("APScheduler shutdown")
