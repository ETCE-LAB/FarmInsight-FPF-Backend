import asyncio
import aiohttp
import json
import uuid
import base64
import aiofiles
import aiofiles.os

from io import BytesIO
from PIL import Image as pilImg
from asgiref.sync import sync_to_async

from django.core.files import File

from django_server import settings
from fpf_sensor_service.utils import async_safe_log
from fpf_sensor_service.scripts_base import FieldDescription, FieldType
from .typed_action_script import ActionScript
from .action_script_description import ActionScriptDescription
from fpf_sensor_service.models import SensorConfig, Image


async def async_send_image(camera_id, image: Image, recurse_on_forbidden=True):
    from fpf_sensor_service.services import async_get_or_request_api_key, async_request_api_key
    api_key = await async_get_or_request_api_key()
    if api_key is not None:
        async with aiofiles.open(image.image.path, 'rb') as file:
            image_str = base64.b64encode(await file.read()).decode('ascii')
        data = {'measuredAt': image.measuredAt.isoformat(), 'image': image_str}

        async with aiohttp.ClientSession() as session:
            url = f"{settings.MEASUREMENTS_BASE_URL}/api/images/{camera_id}"
            headers = {'Authorization': f'ApiKey {api_key}'}
            async with session.post(url, json=data, headers=headers, timeout=15) as response:
                if response.status == 201:
                    await aiofiles.os.remove(image.image.path)
                    await image.adelete()
                    await async_safe_log('debug', 'Successfully sent image.', extra={'camera_id': camera_id})
                    return True
                elif response.status == 403:
                    await async_request_api_key()
                    if recurse_on_forbidden:
                        return await async_send_image(camera_id, image, recurse_on_forbidden=False)
                else:
                    await async_safe_log('error', 'Error sending image, will retry later.', extra={'camera_id': camera_id})
    return False


@sync_to_async
def load_images(camera_id):
    return list(Image.objects.filter(camera_id=camera_id).order_by('measuredAt').all())


async def async_send_images(camera_id):
    images = await load_images(camera_id)
    for image in images:
        if not await async_send_image(camera_id, image):
            break


@sync_to_async
def load_camera(cam_id: str) -> SensorConfig:
    return SensorConfig.objects.get(id=cam_id)


class CameraWrapperActionScript(ActionScript):
    camera_id = ''

    def init_additional_information(self):
        additional_information = json.loads(self.model.additionalInformation)
        self.camera_id = additional_information['camera_id']

    @staticmethod
    def get_description() -> ActionScriptDescription:
        return ActionScriptDescription(
            script_class_id='ebc3f66e-ed6d-46b0-b694-80e6858019a1',
            name='Camera image to action wrapper',
            description=("Uses a configured camera to take an image, required to integrate it into an action chain."
                         ";Verwendet eine konfigurierte Kamera um ein Bild zu nehmen, benötigt um dies in Aktionsketten zu integrieren."),
            has_action_value=False,
            action_values=[],
            fields=[
                FieldDescription(
                    id='camera_id',
                    name='Camera;Kamera',
                    description="Camera to be used.;Kamera zu verwenden.",
                    type=FieldType.CAMERA_ID,
                    rules=[]
                )
            ]
        )

    async def run(self, payload=None):
        """
        Controls the Shelly plug via HTTP.
        Supports:
        - Plain string: "on" / "off"
        - JSON string: {"value": "on", "delay": 1800}
        """
        # Build URL
        model = await load_camera(self.camera_id)

        await async_safe_log('debug', "Camera task triggered", extra={'action_id': self.model.id})
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
                    async with aiohttp.ClientSession(auto_decompress=False, raise_for_status=True) as session:
                        additional_information = json.loads(model.additionalInformation)
                        url = additional_information['snapshotUrl']
                        async with session.get(url, timeout=5) as response:
                            img_data = await response.read()
                            result = File(img_data, f"{str(uuid.uuid4())}.jpg")
                            break
                except Exception as e:
                    # only raise the error outwards if it's the last attempt
                    if i == settings.MEASUREMENT_RETRY_COUNT:
                        raise e
                    else:
                        await asyncio.sleep(settings.MEASUREMENT_RETRY_SLEEP_BETWEEN_S)
        if result is not None:
            await Image.objects.acreate(
                image=result,
                camera_id=self.camera_id,
            )
            await async_send_images(self.camera_id)
            await async_safe_log('debug', "Camera Task completed", extra={'action_id': self.model.id})
        else:
            await async_safe_log('warning',"Camera Task skipped as result is None", extra={'action_id': self.model.id})
