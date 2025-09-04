import random
import time

import requests

from django_server import settings
from fpf_sensor_service.sensors import TypedSensor, MeasurementResult
from fpf_sensor_service.utils import get_logger
from .auth_services import get_fpf_id, get_or_request_api_key, request_api_key
from ..models import SensorMeasurement

logger = get_logger()


def send_package(sensor_id, measurements, recurse_on_forbidden=True):
    api_key = get_or_request_api_key()
    if api_key is not None:
        data = [
            {'measuredAt': m.measuredAt.isoformat(), 'value': m.value}
            for m in measurements
        ]

        response = requests.post(f"{settings.MEASUREMENTS_BASE_URL}/api/measurements/{sensor_id}", json=data, headers={
            'Authorization': f'ApiKey {api_key}'
        })

        if response.status_code == 201:
            SensorMeasurement.objects.filter(measuredAt__lte=measurements[-1].measuredAt).delete()
            logger.debug('Successfully sent measurements.',
                         extra={'extra': {'fpfId': get_fpf_id(), 'sensorId': sensor_id, 'api_key': api_key}})
            return True
        elif response.status_code == 403:
            request_api_key()
            if recurse_on_forbidden:
                return send_package(sensor_id, measurements, recurse_on_forbidden=False)
        else:
            logger.error('Error sending measurements, will retry later.',
                         extra={'extra': {'fpfId': get_fpf_id(), 'sensorId': sensor_id, 'api_key': api_key}})
    return False


def send_measurements(sensor_id):
    """
    For given sensor, try to send all measurements to central app.
    If succeeded, delete entries from local database.
    :param sensor_id: GUID of sensor
    """
    measurements = SensorMeasurement.objects.filter(sensor_id=sensor_id).order_by('measuredAt').all()
    package_size = settings.MEASUREMENT_PACKAGE_SIZE
    if measurements.exists():
        packages = (len(measurements) // package_size) + 1
        for i in range(packages):
            if not send_package(sensor_id, measurements[i * package_size: (i + 1) * package_size]):
                break


def sensor_task(sensor: TypedSensor):
    """
    Function to trigger the measurement of the sensor and to send existing measurements.
    Gets called at the configured interval for the sensor.
    :param sensor: Sensor of which values are to be processed.
    """
    logger.debug("Sensor task triggered", extra={'extra': {'fpfId': get_fpf_id(), 'sensorId': sensor.sensor_config.id, 'api_key': get_or_request_api_key()}})
    try:
        result = None
        if settings.GENERATE_MEASUREMENTS:
            result = MeasurementResult(value=random.uniform(20.0, 20.5))
        else:
            i = 0
            while i < settings.MEASUREMENT_RETRY_COUNT:
                i += 1
                try:
                    result = sensor.get_measurement()
                    break
                except Exception as e:
                    # only raise the error outwards if it's the last attempt
                    if i == settings.MEASUREMENT_RETRY_COUNT:
                        raise e
                    else:
                        time.sleep(settings.MEASUREMENT_RETRY_SLEEP_BETWEEN_S)

        if result.value is not None:
            SensorMeasurement.objects.create(
                sensor_id=sensor.sensor_config.id,
                value=result.value,
                measuredAt=result.timestamp
            )
            send_measurements(sensor.sensor_config.id)
            logger.debug("Sensor Task completed", extra={'extra': {'fpfId': get_fpf_id(), 'sensorId': sensor.sensor_config.id, 'api_key': get_or_request_api_key()}})
        else:
            logger.warning("Sensor Task skipped as value is None", extra={
                'extra': {'fpfId': get_fpf_id(), 'sensorId': sensor.sensor_config.id,
                          'api_key': get_or_request_api_key()}})
    except Exception as e:
        logger.error(f"Error processing sensor: {e}", extra={'extra': {'fpfId': get_fpf_id(), 'sensorId': sensor.sensor_config.id, 'api_key': get_or_request_api_key()}})
