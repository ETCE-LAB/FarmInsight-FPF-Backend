import random
from .models import SensorConfig, SensorMeasurement
import requests
from django.conf import settings
from fpf_sensor_service.logging_utils import get_logger

logger = get_logger()


def generate_measurement(sensor):
    """
    Dummy function to mimic a sensor measurement
    Stores a random measurement value in the sqlite db SensorMeasurement
    :param sensor: Sensor to measure
    """
    try:
        logger.info(f"Run measurement for {sensor.id}.")
        db_sensor = SensorConfig.objects.get(id=sensor.id)
        SensorMeasurement.objects.create(
            sensor_id=db_sensor.id,
            value=random.uniform(20.0, 100.0)
        )
    except SensorConfig.DoesNotExist:
        logger.error(f"SensorConfig with sensorId {sensor.id} does not exist.")
    except ValueError as e:
        logger.error(f"Invalid UUID format: {e}")


def send_measurements(sensorId):
    """
    For given sensor, try to send all measurements to central app.
    If succeeded, delete entries from local database.
    :param sensorId: GUID of sensor
    """
    measurements = SensorMeasurement.objects.filter(sensor_id=sensorId)
    if measurements.exists():
        data = [
            {'measuredAt': m.measuredAt.isoformat(), 'value': m.value}
            for m in measurements
        ]

        url = f"{settings.MEASUREMENTS_BASE_URL}/api/measurements/{sensorId}"
        response = requests.post(url, json=data)

        if response.status_code == 201:
            measurements.delete()
        else:
            logger.info('Error sending measurements, will retry.')
