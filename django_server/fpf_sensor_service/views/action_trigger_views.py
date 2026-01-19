from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from fpf_sensor_service.utils import get_logger
from fpf_sensor_service.services.action_trigger_services import update_action_trigger
from fpf_sensor_service.services import create_action_trigger, get_action_trigger


logger = get_logger()


class ActionTriggerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = create_action_trigger(request.data)

        # logger.info(f"Action trigger {request.data['description']} created successfully", extra={'action_id': request.data['actionId']})

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, action_trigger_id):
        serializer = update_action_trigger(action_trigger_id, request.data)

        #logger.info(f'Action trigger {request.data['description']} updated', extra={'action_id': request.data['actionId']})

        return Response(serializer.data, status=status.HTTP_200_OK)

    def get(self, request, action_trigger_id):
        serializer = get_action_trigger(action_trigger_id)
        return Response(serializer.data)

    def delete(self, request, action_trigger_id):

        return Response(data={}, status=status.HTTP_200_OK)