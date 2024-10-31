from fpf_sensor_service.scheduler import scheduler
from fpf_sensor_service.utils.logging_utils import get_logger
from fpf_sensor_service.models.sensor_config import SensorConfig
from fpf_sensor_service.serializers.sensor_config_serializer import SensorConfigSerializer

logger = get_logger()


def update_sensor_interval(data, sensorId):
    """
    Update the sensor interval on SQLite db and update the scheduling job interval.
    :param data: Parsed data from the request
    :param sensorId: GUID of sensor which must already exist in the database
    :return: Response data and status
    """
    try:
        sensor = SensorConfig.objects.get(id=sensorId)
    except SensorConfig.DoesNotExist:
        return {'data': {'error': f'Sensor with sensorId {sensorId} not found.'}, 'status': 404}

    serializer = SensorConfigSerializer(sensor, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        job_id = f"sensor_{sensorId}"
        job = scheduler.get_job(job_id)
        if job:
            scheduler.reschedule_job(job_id, trigger='interval', seconds=sensor.intervalSeconds)
            return {'data': {'status': 'success', 'sensorId': sensorId, 'newInterval': sensor.intervalSeconds},
                    'status': 200}
        else:
            return {'data': {'error': f'No scheduled job found for sensor {sensorId}'}, 'status': 404}
    else:
        return {'data': serializer.errors, 'status': 400}
