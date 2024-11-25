from fpf_sensor_service.services import add_scheduler_task
from fpf_sensor_service.services.scheduler_services import scheduler, reschedule_task
from fpf_sensor_service.utils.logging_utils import get_logger
from fpf_sensor_service.models.sensor_config import SensorConfig
from fpf_sensor_service.serializers.sensor_config_serializer import SensorConfigSerializer

logger = get_logger()


def get_sensor_config(sensor_id: str) -> SensorConfigSerializer:
    sensor_config = SensorConfig.objects.get(id=sensor_id)
    return SensorConfigSerializer(sensor_config)


def create_sensor_config(data) -> SensorConfigSerializer:
    serializer = SensorConfigSerializer(data=data)
    if serializer.is_valid(raise_exception=True):
        sensor_config = SensorConfig(**serializer.validated_data)
        # need to make sure that we use the same ID as the dashboard backend and Serializer doesn't do that
        sensor_config.id = data['id']
        sensor_config.save()

        add_scheduler_task(sensor_config)

        return SensorConfigSerializer(sensor_config)


def update_sensor_config(data, sensor_id) -> SensorConfigSerializer:
    """
    Update the sensor interval on SQLite db and update the scheduling job interval.
    :param data: Parsed data from the request
    :param sensor_id: GUID of sensor which must already exist in the database
    :return: Response data and status
    """
    sensor = SensorConfig.objects.get(id=sensor_id)
    serializer = SensorConfigSerializer(sensor, data=data, partial=True)
    if serializer.is_valid(raise_exception=True):
        sensor_config = serializer.save()
        reschedule_task(sensor_config)

    return serializer
