import asyncio
import random

import aiohttp
import json

from asgiref.sync import sync_to_async

from django_server import settings
from fpf_sensor_service.utils import async_safe_log
from fpf_sensor_service.scripts_base import FieldDescription, FieldType
from fpf_sensor_service.models import SensorConfig, SensorMeasurement
from fpf_sensor_service.sensors import MeasurementResult, TypedSensor, TypedSensorFactory
from .action_script_description import ActionScriptDescription
from .typed_action_script import ActionScript


typed_sensor_factory = TypedSensorFactory()


async def send_package(sensor_id, measurements, recurse_on_forbidden=True):
    from fpf_sensor_service.services import async_get_or_request_api_key, async_request_api_key
    api_key = await async_get_or_request_api_key()
    if api_key is not None:
        data = [
            {'measuredAt': m.measuredAt.isoformat(), 'value': m.value}
            for m in measurements
        ]

        async with aiohttp.ClientSession() as session:
            url = f"{settings.MEASUREMENTS_BASE_URL}/api/measurements/{sensor_id}"
            headers = {'Authorization': f'ApiKey {api_key}'}
            async with session.post(url, json=data, headers=headers, timeout=15) as response:
                if response.status == 201:
                    await SensorMeasurement.objects.filter(measuredAt__lte=measurements[-1].measuredAt).adelete()
                    await async_safe_log('debug', 'Successfully sent measurements.', extra={'sensorId': sensor_id})
                    return True
                elif response.status == 403:
                    await async_request_api_key()
                    if recurse_on_forbidden:
                        return await send_package(sensor_id, measurements, recurse_on_forbidden=False)
                else:
                    await async_safe_log('error', 'Error sending measurements, will retry later.', extra={'sensorId': sensor_id})
    return False


@sync_to_async
def load_measurements(sensor_id):
    return list(SensorMeasurement.objects.filter(sensor_id=sensor_id).order_by('measuredAt').all())


async def send_measurements(sensor_id):
    measurements = await load_measurements(sensor_id)
    package_size = settings.MEASUREMENT_PACKAGE_SIZE
    if len(measurements) > 0:
        packages = (len(measurements) // package_size) + 1
        for i in range(packages):
            if not await send_package(sensor_id, measurements[i * package_size: (i + 1) * package_size]):
                break


@sync_to_async
def load_sensor(sensor_id: str) -> TypedSensor:
    model = SensorConfig.objects.get(id=sensor_id)
    sensor_class = typed_sensor_factory.get_typed_sensor_class(str(model.sensorClassId))
    sensor = sensor_class(model)
    return sensor


@sync_to_async
def run_sensor(sensor: TypedSensor) -> MeasurementResult:
    return sensor.run()


class SensorWrapperActionScript(ActionScript):
    sensor_id = ''

    def init_additional_information(self):
        additional_information = json.loads(self.model.additionalInformation)
        self.sensor_id = additional_information['sensor_id']

    @staticmethod
    def get_description() -> ActionScriptDescription:
        return ActionScriptDescription(
            script_class_id='24ddc870-34f8-4120-a2c3-c036acecafed',
            name='Sensor measurement to action wrapper',
            description=("Uses a configured sensor to take a measurement, required to integrate it into an action chain."
                         ";Verwendet einen konfigurierten Sensor um einen Wert zu messen, benötigt um es in Aktionsketten zu integrieren."),
            has_action_value=False,
            action_values=[],
            fields=[
                FieldDescription(
                    id='sensor_id',
                    name='Sensor;Sensor',
                    description="Sensor to be used.;Sensor zu verwenden.",
                    type=FieldType.SENSOR_ID,
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
        sensor = await load_sensor(self.sensor_id)

        await async_safe_log('debug', "Sensor task triggered", extra={'action_id': self.model.id})
        result = None
        if settings.GENERATE_MEASUREMENTS:
            result = MeasurementResult(value=random.uniform(20.0, 20.5))
        else:
            i = 0
            while i < settings.MEASUREMENT_RETRY_COUNT:
                i += 1
                try:
                    result = await run_sensor(sensor)
                    break
                except Exception as e:
                    # only raise the error outwards if it's the last attempt
                    if i == settings.MEASUREMENT_RETRY_COUNT:
                        raise e
                    else:
                        await asyncio.sleep(settings.MEASUREMENT_RETRY_SLEEP_BETWEEN_S)

        if result.value is not None:
            await SensorMeasurement.objects.acreate(
                sensor_id=self.sensor_id,
                value=result.value,
                measuredAt=result.timestamp
            )
            await async_safe_log('info', f"Successfully retrieved sensor value: {result.value:.2f}", extra={'action_id': self.model.id})
            await send_measurements(self.sensor_id)
            await async_safe_log('debug', "Sensor Task completed", extra={'action_id': self.model.id})
        else:
            await async_safe_log('warning',"Sensor Task skipped as result is None", extra={'action_id': self.model.id})
