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
        self.account = additional_information['email']
        self.password = additional_information['password']
        self.country = additional_information['country_code']
        self.serial = additional_information['device_serial']
        self.logger = get_logger()

    @staticmethod
    def get_description() -> SensorDescription:
        return SensorDescription(
            sensor_class_id='e1ae510b-f79e-4cc5-8053-26b8c5cdf6e0',
            model='Anker Solix Cloud API (Battery Energy)',
            connection=ConnectionType.HTTP,
            parameter='battery_energy;Batterieladung',
            unit='Wh',
            tags={
                'info': 'uses an unofficial api library, can break with updates;verwendet eine inoffizielle API Bücherei, anker updates können diese mit Updates ändern',
                'energy_type': 'battery_level'
            },
            fields=[
                FieldDescription(name='email', type=FieldType.STRING, rules=[]),
                FieldDescription(name='password', type=FieldType.STRING, rules=[]),
                FieldDescription(name='country_code', type=FieldType.STRING, rules=[]),
                FieldDescription(name='device_serial', type=FieldType.STRING, rules=[])
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


class AnkerSolarbankSocSensor(HttpSensor):

    def init_additional_information(self):
        additional_information = json.loads(self.sensor_config.additionalInformation)
        self.account = additional_information['email']
        self.password = additional_information['password']
        self.country = additional_information['country_code']
        self.serial = additional_information['device_serial']
        self.logger = get_logger()

    @staticmethod
    def get_description() -> SensorDescription:
        return SensorDescription(
            sensor_class_id='f2bf621c-8a0f-5dd6-9164-37c9d6de7f1b',
            model='Anker Solix Cloud API (SoC)',
            connection=ConnectionType.HTTP,
            parameter='battery_soc;Ladezustand',
            unit='%',
            tags={
                'info': 'uses an unofficial api library, can break with updates;verwendet eine inoffizielle API Bücherei, anker updates können diese mit Updates ändern',
                'energy_type': 'battery_soc'
            },
            fields=[
                FieldDescription(name='email', type=FieldType.STRING, rules=[]),
                FieldDescription(name='password', type=FieldType.STRING, rules=[]),
                FieldDescription(name='country_code', type=FieldType.STRING, rules=[]),
                FieldDescription(name='device_serial', type=FieldType.STRING, rules=[])
            ]
        )

    async def _get_measurement_async(self):
        async with ClientSession() as websession:
            myapi = api.AnkerSolixApi(
                self.account, self.password, self.country, websession, self.logger
            )
            await myapi.update_sites()
            await myapi.update_device_details()
            self.value = myapi.devices[self.serial]['battery_soc']

    def get_measurement(self):
        asyncio.run(self._get_measurement_async())
        return MeasurementResult(value=self.value)


class AnkerSolarbankInputPowerSensor(HttpSensor):

    def init_additional_information(self):
        additional_information = json.loads(self.sensor_config.additionalInformation)
        self.account = additional_information['email']
        self.password = additional_information['password']
        self.country = additional_information['country_code']
        self.serial = additional_information['device_serial']
        self.logger = get_logger()

    @staticmethod
    def get_description() -> SensorDescription:
        return SensorDescription(
            sensor_class_id='a3c0732d-9b1e-6ee7-0275-48dad7ef8e2c',
            model='Anker Solix Cloud API (Input Power)',
            connection=ConnectionType.HTTP,
            parameter='input_power;Solareingang',
            unit='W',
            tags={
                'info': 'uses an unofficial api library, can break with updates;verwendet eine inoffizielle API Bücherei, anker updates können diese mit Updates ändern',
                'energy_type': 'solar_input'
            },
            fields=[
                FieldDescription(name='email', type=FieldType.STRING, rules=[]),
                FieldDescription(name='password', type=FieldType.STRING, rules=[]),
                FieldDescription(name='country_code', type=FieldType.STRING, rules=[]),
                FieldDescription(name='device_serial', type=FieldType.STRING, rules=[])
            ]
        )

    async def _get_measurement_async(self):
        async with ClientSession() as websession:
            myapi = api.AnkerSolixApi(
                self.account, self.password, self.country, websession, self.logger
            )
            await myapi.update_sites()
            await myapi.update_device_details()
            self.value = myapi.devices[self.serial]['input_power']

    def get_measurement(self):
        asyncio.run(self._get_measurement_async())
        return MeasurementResult(value=self.value)


class AnkerSolarbankOutputPowerSensor(HttpSensor):

    def init_additional_information(self):
        additional_information = json.loads(self.sensor_config.additionalInformation)
        self.account = additional_information['email']
        self.password = additional_information['password']
        self.country = additional_information['country_code']
        self.serial = additional_information['device_serial']
        self.logger = get_logger()

    @staticmethod
    def get_description() -> SensorDescription:
        return SensorDescription(
            sensor_class_id='b4d1843e-0c2f-7ff8-1386-59ebe8f09f3d',
            model='Anker Solix Cloud API (Output Power)',
            connection=ConnectionType.HTTP,
            parameter='output_power;Ausgangsleistung',
            unit='W',
            tags={
                'info': 'uses an unofficial api library, can break with updates;verwendet eine inoffizielle API Bücherei, anker updates können diese mit Updates ändern',
                'energy_type': 'output_power'
            },
            fields=[
                FieldDescription(name='email', type=FieldType.STRING, rules=[]),
                FieldDescription(name='password', type=FieldType.STRING, rules=[]),
                FieldDescription(name='country_code', type=FieldType.STRING, rules=[]),
                FieldDescription(name='device_serial', type=FieldType.STRING, rules=[])
            ]
        )

    async def _get_measurement_async(self):
        async with ClientSession() as websession:
            myapi = api.AnkerSolixApi(
                self.account, self.password, self.country, websession, self.logger
            )
            await myapi.update_sites()
            await myapi.update_device_details()
            self.value = myapi.devices[self.serial]['output_power']

    def get_measurement(self):
        asyncio.run(self._get_measurement_async())
        return MeasurementResult(value=self.value)


class AnkerSolarbankChargingPowerSensor(HttpSensor):

    def init_additional_information(self):
        additional_information = json.loads(self.sensor_config.additionalInformation)
        self.account = additional_information['email']
        self.password = additional_information['password']
        self.country = additional_information['country_code']
        self.serial = additional_information['device_serial']
        self.logger = get_logger()

    @staticmethod
    def get_description() -> SensorDescription:
        return SensorDescription(
            sensor_class_id='c5e2954f-1d3e-8009-2497-60fcf9010a4e',
            model='Anker Solix Cloud API (Charging Power)',
            connection=ConnectionType.HTTP,
            parameter='charging_power;Ladeleistung',
            unit='W',
            tags={
                'info': 'uses an unofficial api library, can break with updates;verwendet eine inoffizielle API Bücherei, anker updates können diese mit Updates ändern',
                'energy_type': 'charging_power'
            },
            fields=[
                FieldDescription(name='email', type=FieldType.STRING, rules=[]),
                FieldDescription(name='password', type=FieldType.STRING, rules=[]),
                FieldDescription(name='country_code', type=FieldType.STRING, rules=[]),
                FieldDescription(name='device_serial', type=FieldType.STRING, rules=[])
            ]
        )

    async def _get_measurement_async(self):
        async with ClientSession() as websession:
            myapi = api.AnkerSolixApi(
                self.account, self.password, self.country, websession, self.logger
            )
            await myapi.update_sites()
            await myapi.update_device_details()
            self.value = myapi.devices[self.serial]['charging_power']

    def get_measurement(self):
        asyncio.run(self._get_measurement_async())
        return MeasurementResult(value=self.value)
