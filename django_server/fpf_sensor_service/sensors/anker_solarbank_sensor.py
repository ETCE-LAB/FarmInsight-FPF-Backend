import json
import asyncio
from aiohttp import ClientSession

from fpf_sensor_service.utils import get_logger
from fpf_sensor_service.sensors import HttpSensor, MeasurementResult
from fpf_sensor_service.sensors.sensor_description import SensorDescription, ConnectionType, FieldDescription, FieldType

from anker_solix_api.api import api


class AnkerSolarbankPowerSensor(HttpSensor):
    # uses the unofficial anker-solix-api library, if errors occur search/contact there and possibly update submodule
    # https://github.com/thomluther/anker-solix-api

    def init_additional_information(self):
        additional_information = json.loads(self.sensor_config.additionalInformation)
        self.account = additional_information['account']
        self.password = additional_information['password']
        self.country = additional_information['country']
        self.serial = additional_information['device_serial']
        self.logger = get_logger()

    @staticmethod
    def get_description() -> SensorDescription:
        return SensorDescription(
            sensor_class_id='e1ae510b-f79e-4cc5-8053-26b8c5cdf6e0',
            model='Anker Solix Cloud API',
            connection=ConnectionType.HTTP,
            parameter='watts;watt',
            unit='W',
            tags={
                'info': 'uses an unofficial api library, can break with updates'
            },
            fields=[
                FieldDescription(
                    name='account',
                    type=FieldType.STRING,
                    rules=[]
                ),
                FieldDescription(
                    name='password',
                    type=FieldType.STRING,
                    rules=[]
                ),
                FieldDescription(
                    name='country',
                    type=FieldType.STRING,
                    #hint='Country ID (e.g. DE)',
                    rules=[]
                ),
                FieldDescription(
                    name='device_serial',
                    type=FieldType.STRING,
                    rules=[]
                )
            ]
        )

    async def _get_measurement_async(self):
        async with ClientSession() as websession:
            myapi = api.AnkerSolixApi(
                self.account, self.password, self.country, websession, self.logger
            )
            await myapi.update_sites()
            await myapi.update_device_details()
            self.value = myapi.devices[self.serial]['battery_energy']

    def get_measurement(self):
        asyncio.run(self._get_measurement_async())
        return MeasurementResult(value=self.value)

