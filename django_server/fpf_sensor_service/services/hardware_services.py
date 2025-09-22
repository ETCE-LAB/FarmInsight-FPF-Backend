from fpf_sensor_service.models import Hardware
from fpf_sensor_service.serializers import HardwareSerializer


def get_hardware() -> HardwareSerializer:
    """
    Returns all distinct Hardware objects used by Actions under the given FPF.
    """
    return HardwareSerializer(Hardware.objects, many=True)


def get_or_create_hardware(hardware_name):
    """
    Creates a new Hardware object from the given data.
    """
    if not hardware_name:
        raise ValueError("Hardware name must not be empty.")

    existing_hardware = Hardware.objects.filter(name=hardware_name).first()

    if existing_hardware:
        return existing_hardware

    try:
        hardware = Hardware.objects.create(name=hardware_name)
        return hardware
    except Exception as e:
        raise RuntimeError(f"Error creating the Hardware: {str(e)}")


def create_hardware(data) -> HardwareSerializer:
    serializer = HardwareSerializer(data=data)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
    return serializer


def set_hardware_order(ids: list[str]) -> HardwareSerializer:
    items = Hardware.objects.filter(id__in=ids)
    for item in items:
        item.orderIndex = ids.index(str(item.id))

    Hardware.objects.bulk_update(items, ['orderIndex'])
    return HardwareSerializer(items, many=True)


def update_hardware(hardware_id:str, data) -> HardwareSerializer:
    hardware = Hardware.objects.get(id=hardware_id)
    serializer = HardwareSerializer(hardware, data=data)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
    return serializer


def remove_hardware(hardware_id:str):
    hardware = Hardware.objects.get(id=hardware_id)
    hardware.delete()
