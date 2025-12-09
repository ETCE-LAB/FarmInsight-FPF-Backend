from rest_framework.exceptions import NotFound

from fpf_sensor_service.models import Action
from fpf_sensor_service.serializers import ActionSerializer


def get_actions() -> ActionSerializer:
    actions = Action.objects.all()
    return ActionSerializer(actions, many=True)


def get_action_by_id(action_id: str) -> Action:
    try:
        return Action.objects.get(id=action_id)
    except Action.DoesNotExist:
        raise NotFound(f'Action with id: {action_id} was not found.')


def create_action(action_data: dict) -> ActionSerializer:
    serializer = ActionSerializer(data=action_data, partial=True)
    if serializer.is_valid(raise_exception=True):
        action = Action(**serializer.validated_data)
        action.id = action_data['id']
        action.save()
        return ActionSerializer(action)


def update_action(action_id: str, action_data: any) -> ActionSerializer:
    try:
        action = Action.objects.get(id=action_id)
    except Action.DoesNotExist:
        raise NotFound()

    serializer = ActionSerializer(action, data=action_data, partial=True)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
    return serializer


def delete_action(action: Action):
    action.delete()


def set_is_automated(action_id: str, is_automated: bool) -> Action:
    action = get_action_by_id(action_id)
    action.isAutomated = is_automated
    action.save()
    return action


def set_action_order(ids: list[str]):
    items = Action.objects.filter(id__in=ids)
    for item in items:
        item.orderIndex = ids.index(str(item.id))
    Action.objects.bulk_update(items, ['orderIndex'])
