import os
import time
import uuid
import base64
from io import BytesIO

import requests
from PIL import Image as pilImg

from django.core.files import File

from django_server import settings
from fpf_sensor_service.utils import get_logger
from fpf_sensor_service.models import Image
from .auth_services import get_fpf_id, get_or_request_api_key, request_api_key
from ..sensors import Camera

logger = get_logger()


def send_image(camera_id, image: Image, recurse_on_forbidden=True):
    api_key = get_or_request_api_key()
    if api_key is not None:
        with image.image.open('rb') as file:
            image_str = base64.b64encode(file.read()).decode('ascii')
        data = {'measuredAt': image.measuredAt.isoformat(), 'image': image_str}
        response = requests.post(f"{settings.MEASUREMENTS_BASE_URL}/api/images/{camera_id}", json=data, headers={
            'Authorization': f'ApiKey {api_key}'
        })

        if response.status_code == 201:
            os.remove(image.image.path)
            image.delete()
            logger.debug('Successfully sent image.', extra={'extra': {'fpfId': get_fpf_id(), 'cameraId': camera_id, 'api_key': api_key}})
            return True
        elif response.status_code == 403:
            request_api_key()
            if recurse_on_forbidden:
                return send_image(camera_id, image, recurse_on_forbidden=False)
        else:
            logger.error('Error sending image, will retry later.',
                         extra={'extra': {'fpfId': get_fpf_id(), 'cameraId': camera_id, 'api_key': api_key}})
    return False


def send_images(camera_id):
    images = Image.objects.filter(camera_id=camera_id).order_by('measuredAt').all()
    if images.exists():
        for image in images:
            if not send_image(camera_id, image):
                break


def camera_task(camera: Camera):
    """
    Function to trigger the measurement of the sensor and to send existing images.
    Gets called at the configured interval for the sensor.
    :param camera: Camera of which images are to be processed.
    """
    logger.debug("Camera task triggered", extra={'extra': {'fpfId': get_fpf_id(), 'cameraId': camera.sensor_config.id, 'api_key': get_or_request_api_key()}})
    try:
        result = None
        if settings.USE_DEFAULT_IMAGE:
            with pilImg.open(settings.DEFAULT_IMAGE_PATH) as file:
                stream = BytesIO()
                file.save(stream, "PNG")
            result = File(stream, f"{str(uuid.uuid4())}.png")
        else:
            i = 0
            while i < settings.MEASUREMENT_RETRY_COUNT:
                i += 1
                try:
                    img_data = camera.get_image()
                    result = File(img_data, f"{str(uuid.uuid4())}.jpg")
                    break
                except Exception as e:
                    # only raise the error outwards if it's the last attempt
                    if i == settings.MEASUREMENT_RETRY_COUNT:
                        raise e
                    else:
                        time.sleep(settings.MEASUREMENT_RETRY_SLEEP_BETWEEN_S)

        if result is not None:
            Image.objects.create(
                image=result,
                camera_id=camera.sensor_config.id,
            )
            send_images(camera.sensor_config.id)
            logger.debug("Camera Task completed", extra={'extra': {'fpfId': get_fpf_id(), 'cameraId': camera.sensor_config.id, 'api_key': get_or_request_api_key()}})
        else:
            logger.warning("Camera Task skipped as value is None", extra={
                'extra': {'fpfId': get_fpf_id(), 'cameraId': camera.sensor_config.id, 'api_key': get_or_request_api_key()}})
    except Exception as e:
        logger.error(f"Error processing camera: {e}", extra={'extra': {'fpfId': get_fpf_id(), 'cameraId': camera.sensor_config.id, 'api_key': get_or_request_api_key()}})
