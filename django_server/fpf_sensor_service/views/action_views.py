from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from fpf_sensor_service.serializers import ActionScriptDescriptionSerializer
from fpf_sensor_service.utils import get_logger
from fpf_sensor_service.services import create_action, delete_action, get_action_by_id, set_is_automated, update_action, \
    get_hardware_by_name, get_active_state_of_action, create_manual_triggered_action_in_queue, \
    create_auto_triggered_actions_in_queue, action_queue, set_action_order, get_actions, clear_action_queue, \
    action_queue_entry
from fpf_sensor_service.action_scripts import TypedActionScriptFactory


typed_action_script_factory = TypedActionScriptFactory()
logger = get_logger()


class ActionView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = get_actions()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        if request.data.get('hardware').get('name'):
            hardware = get_hardware_by_name(request.data.get('hardware').get('name'))
            request.data['hardwareId'] = hardware.id

        action = create_action(request.data)

        logger.info("Controllable action created successfully", extra={'fpf_id': fpf_id})

        return Response(action.data, status=status.HTTP_201_CREATED)

    def put(self, request, action_id):
        serializer = update_action(action_id, request.data)

        #logger.info("Controllable Action updated successfully", extra={'fpf_id': fpf_id})

        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, action_id):
        delete_action(action_id)

        #logger.info("Controllable action deleted successfully", extra={'fpf_id': fpf_id})

        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def execute_action(request, action_id, trigger_id):
    data = []
    if trigger_id == "auto": # The user set the controllable action to automatic
        set_is_automated(action_id, True)
        # Check if the trigger for the affected action can trigger and process the queue
        # get trigger type and refresh the creation
        create_auto_triggered_actions_in_queue(action_id)

    else: # The user activated a manual trigger
        # Check if the action is already on manual mode and the current active action is the same one.
        # In this case, the action goes back to auto mode as the user deactivated the manual trigger.
        # This gives room for all other auto triggers related to the same hardware to execute.

        active_state = get_active_state_of_action(action_id)

        # Completely new action
        if active_state is None:
            set_is_automated(action_id, False)
            data = create_manual_triggered_action_in_queue(action_id, trigger_id)

        #if active_state is not None and get_action_by_id(action_id).isAutomated == False and (active_state.trigger.id is None or active_state.trigger.id == trigger_id):
        elif active_state is not None and (get_action_by_id(action_id).isAutomated == False and str(active_state.trigger.id) == trigger_id):
            set_is_automated(action_id, True)

        # The user selected a new manual trigger, different from the current active state
        else:
            set_is_automated(action_id, False)
            data = create_manual_triggered_action_in_queue(action_id, trigger_id)

    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_available_action_script_types(request):
    action_script_types = typed_action_script_factory.get_available_action_scripts()
    serializer = ActionScriptDescriptionSerializer(action_script_types, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_action_queue(request):
    serializer = action_queue()
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_action_order(request):
    set_action_order(request.data)
    return Response(data={'success': ''}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_clear_action_queue(request):
    clear_action_queue()
    return Response(data={'success': ''}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_action_queue_entry(request, entry_id: str):
    serializer = action_queue_entry(entry_id)
    return Response(serializer.data, status=status.HTTP_200_OK)
