from rest_framework.exceptions import NotFound

from fpf_sensor_service.models import Hardware
from fpf_sensor_service.serializers import HardwareSerializer


def get_hardware() -> HardwareSerializer:
    """
    Returns all distinct Hardware objects used by Actions under the given FPF.
    """
    return HardwareSerializer(Hardware.objects, many=True)


def get_hardware_by_name(hardware_name):
    try:
        existing_hardware = Hardware.objects.filter(name=hardware_name).first()
    except Hardware.DoesNotExist:
        raise NotFound()
    return existing_hardware


def create_hardware(data) -> HardwareSerializer:
    serializer = HardwareSerializer(data=data)
    if serializer.is_valid(raise_exception=True):
        hardware = Hardware(**serializer.validated_data)
        hardware.id = data['id']
        hardware.save()
        return HardwareSerializer(hardware)


def set_hardware_order(ids: list[str]) -> HardwareSerializer:
    items = Hardware.objects.filter(id__in=ids)
    for item in items:
        item.orderIndex = ids.index(str(item.id))

    Hardware.objects.bulk_update(items, ['orderIndex'])
    return HardwareSerializer(items, many=True)


def update_hardware(hardware_id:str, data) -> HardwareSerializer:
    try:
        hardware = Hardware.objects.get(id=hardware_id)
    except Hardware.DoesNotExist:
        raise NotFound()

    serializer = HardwareSerializer(hardware, data=data)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
    return serializer


def remove_hardware(hardware_id:str):
    hardware = Hardware.objects.get(id=hardware_id)
    hardware.delete()
