import json
import asyncio
from aiohttp import ClientSession

from fpf_sensor_service.utils import get_logger
from .http_sensor import HttpSensor
from .measurement_result import MeasurementResult
from .sensor_description import SensorDescription, ConnectionType
from fpf_sensor_service.scripts_base import FieldDescription, FieldType

from anker_solix_api.api import api


class AnkerSolarbankPowerSensor(HttpSensor):
    # uses the unofficial anker-solix-api library, if errors occur search/contact there and possibly update submodule
    # https://github.com/thomluther/anker-solix-api
    account = None
    password = None
    country = None
    serial = None
    logger = None

    def init_additional_information(self):
        additional_information = json.loads(self.model.additionalInformation)
        self.account = additional_information['email']
        self.password = additional_information['password']
        self.country = additional_information['country_code']
        self.serial = additional_information['device_serial']
        self.logger = get_logger()

    @staticmethod
    def get_description() -> SensorDescription:
        return SensorDescription(
            script_class_id='e1ae510b-f79e-4cc5-8053-26b8c5cdf6e0',
            model='Anker Solix Cloud API',
            connection=ConnectionType.HTTP,
            parameter='watts;watt',
            unit='W',
            tags={
                'info': 'uses an unofficial api library, can break with updates;verwendet eine inoffizielle API library, Anker updates können die Kompatibilität stören'
            },
            fields=[
                FieldDescription(
                    id='',
                    name='email',
                    description='',
                    type=FieldType.STRING,
                    rules=[]
                ),
                FieldDescription(
                    id='',
                    name='password',
                    description='',
                    type=FieldType.STRING,
                    rules=[]
                ),
                FieldDescription(
                    id='',
                    name='country_code',
                    description='',
                    type=FieldType.STRING,
                    rules=[]
                ),
                FieldDescription(
                    id='',
                    name='device_serial',
                    description='',
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

    def run(self, payload=None) -> any:
        asyncio.run(self._get_measurement_async())
        return MeasurementResult(value=self.value)
