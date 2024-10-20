import logging
from apscheduler.schedulers.background import BackgroundScheduler
from fpf_sensor_service.models import SensorConfig
from fpf_sensor_service.tasks import generate_measurement, send_measurements

# Set up logging
logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.DEBUG)

scheduler = BackgroundScheduler()


def schedule_sensor_task(sensor):
    """
    Function to trigger the measurement of the sensor and to send existing measurements.
    Gets called at the configured interval for the sensor.
    :param sensor: Sensor of which values are to be processed.
    """
    logging.info(f"Task triggered for sensor: {sensor.id}")
    try:
        generate_measurement(sensor)
        send_measurements(sensor.id)
        logging.info(f"Task completed for sensor: {sensor.id}")
    except Exception as e:
        logging.error(f"Error processing sensor {sensor.id}: {e}")


def start_scheduler():
    """
    Get all sensor configurations from sqlite db and schedule jobs based on set intervalls.
    """
    sensors = SensorConfig.objects.all()
    for sensor in sensors:
        scheduler.add_job(
            schedule_sensor_task,
            'interval',
            seconds=sensor.intervallSeconds,
            args=[sensor]
        )
        logging.info(f"Scheduled task for sensor: {sensor.id}")

    scheduler.start()
    logging.info("APScheduler started")


def stop_scheduler():
    """
    Stop the scheduler
    """
    scheduler.shutdown()
    logging.info("APScheduler shutdown")
