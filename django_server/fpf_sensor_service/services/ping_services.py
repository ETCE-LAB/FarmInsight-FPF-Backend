from rest_framework.exceptions import NotFound

from fpf_sensor_service.models import SensorConfig, Hardware
from fpf_sensor_service.scripts_base import HttpPing, HardwarePing
from .sensor_config_services import get_sensor
from .hardware_services import get_hardware_by_id


def ping_resource(resource_id):
    sensor = None
    hardware = None

    try:
        sensor = get_sensor(resource_id)
    except SensorConfig.DoesNotExist:
        try:
            hardware = get_hardware_by_id(resource_id)
        except Hardware.DoesNotExist:
            raise NotFound

    if sensor is not None and hardware is None:
        if sensor.hardware_id:
            hardware = get_hardware_by_id(sensor.hardware_id)

    if hardware is not None:
        return HardwarePing(hardware).run()
    elif sensor is not None:
        if not 'http' in sensor.additionalInformation:
            raise Exception('Sensors hardware configuration malformed, no ping possible.')

        return HttpPing(sensor).run()

    # should never happen?
    return False