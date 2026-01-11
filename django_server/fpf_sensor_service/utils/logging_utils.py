import logging
import aiohttp
from django.conf import settings

from django.utils import timezone


def get_logger():
    return logging.getLogger('fpf_sensor_service')


async def async_safe_log(level: str, message: str, extra: dict = None):
    from fpf_sensor_service.services import async_get_or_request_api_key

    # we can still log to std out in async, just not over the api the same way
    logger = logging.getLogger('async_safe')

    payload = {
        'message': message,
        'level': level,
        'createdAt': timezone.now().isoformat(),
    }

    if 'sensorId' in extra:
        payload['sensorId'] = str(extra['sensorId'])
    elif 'camera_id' in extra:
        payload['cameraId'] = str(extra['camera_id'])
    elif 'action_id' in extra:
        payload['actionId'] = str(extra['action_id'])
    elif 'fpfId' in extra:
        payload['fpfId'] = str(extra['fpfId'])

    headers = {
        'Authorization': f"ApiKey {await async_get_or_request_api_key()}"
    }

    try:
        async with aiohttp.ClientSession() as session:
            await session.get(settings.LOGGING_API_URL, json=payload, headers=headers, timeout=5)
    except Exception as e:
        logger.error(e)

    if level == 'debug':
        logger.debug(message, extra=extra)
    elif level == 'info':
        logger.info(payload, extra=extra)
    elif level == 'error':
        logger.error(message, extra=extra)