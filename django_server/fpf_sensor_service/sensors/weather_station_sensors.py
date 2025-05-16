import json

import requests
from typing import Optional
from .measurement_result import MeasurementResult
from .typed_sensor import TypedSensor
from .sensor_description import SensorDescription, ConnectionType, FieldDescription, FieldType, ValidHttpEndpointRule
from dateutil.parser import parse as parse_datetime  # to parse ISO 8601 strings


class HttpWeatherStationAirTemperatureSensor(TypedSensor):
    http_endpoint = None
    auth_header: Optional[dict] = None

    def init_additional_information(self):
        additional_information = json.loads(self.sensor_config.additionalInformation)
        self.http_endpoint = additional_information['http']
        api_key = additional_information.get('authorization')
        if api_key:
            self.auth_header = {"Authorization": f"Bearer {api_key}"}
        else:
            self.auth_header = {}

    @staticmethod
    def get_description() -> SensorDescription:
        return SensorDescription(
            sensor_class_id='a2f4cf30-2615-4b97-be38-1adb19f55d87',
            model='SenseCAP S2120 8-in-1',
            connection=ConnectionType.HTTP,
            parameter='Air Temperature;Luft Temperatur',
            unit='°C',
            tags={
                'info': 'see local SenseCap config to set matching interval. Most common is hourly.'
            },
            fields=[
                FieldDescription(
                    name='http',
                    type=FieldType.STRING,
                    rules=[
                        ValidHttpEndpointRule(),
                    ]
                ),
                FieldDescription(
                    name='authorization',
                    type=FieldType.STRING,
                    rules=[]
                ),
            ]
        )


    def get_measurement(self) -> MeasurementResult:
        url = self.http_endpoint + "?limit=1&order=-received_at"
        response = requests.get(url, headers=self.auth_header)
        response.raise_for_status()
        json_data = response.json()

        value = None
        timestamp = None

        for msg in json_data.get("result", {}).get("uplink_message", {}).get("decoded_payload", {}).get("messages", []):
            if msg["type"] == "Air Temperature":
                value = msg["measurementValue"]
                break

        ttn_timestamp = json_data.get("result", {}).get("uplink_message", {}).get("received_at")
        if ttn_timestamp:
            timestamp = parse_datetime(ttn_timestamp)
        print(value, timestamp)
        return MeasurementResult(value=value, timestamp=timestamp)

class HttpWeatherStationAirHumiditySensor(TypedSensor):
    http_endpoint = None
    auth_header: Optional[dict] = None

    def init_additional_information(self):
        additional_information = json.loads(self.sensor_config.additionalInformation)
        self.http_endpoint = additional_information['http']
        api_key = additional_information.get('authorization')
        if api_key:
            self.auth_header = {"Authorization": f"Bearer {api_key}"}
        else:
            self.auth_header = {}

    @staticmethod
    def get_description() -> SensorDescription:
        return SensorDescription(
            sensor_class_id='ed94acb5-847b-4872-9fa4-dce1c9e29cd7',
            model='SenseCAP S2120 8-in-1',
            connection=ConnectionType.HTTP,
            parameter='Air Humidity;Luft Luftfeuchtigkeit',
            unit='%',
            tags={
                'info': 'see local SenseCap config to set matching interval. Most common is hourly.'
            },
            fields=[
                FieldDescription(
                    name='http',
                    type=FieldType.STRING,
                    rules=[
                        ValidHttpEndpointRule(),
                    ]
                ),
                FieldDescription(
                    name='authorization',
                    type=FieldType.STRING,
                    rules=[]
                ),
            ]
        )


    def get_measurement(self) -> MeasurementResult:
        url = self.http_endpoint + "?limit=1&order=-received_at"
        response = requests.get(url, headers=self.auth_header)
        response.raise_for_status()
        json_data = response.json()

        value = None
        timestamp = None

        for msg in json_data.get("result", {}).get("uplink_message", {}).get("decoded_payload", {}).get("messages", []):
            if msg["type"] == "Air Humidity":
                value = msg["measurementValue"]
                break

        ttn_timestamp = json_data.get("result", {}).get("uplink_message", {}).get("received_at")
        if ttn_timestamp:
            timestamp = parse_datetime(ttn_timestamp)
        print(value, timestamp)
        return MeasurementResult(value=value, timestamp=timestamp)

class HttpWeatherStationLightIntensitySensor(TypedSensor):
    http_endpoint = None
    auth_header: Optional[dict] = None

    def init_additional_information(self):
        additional_information = json.loads(self.sensor_config.additionalInformation)
        self.http_endpoint = additional_information['http']
        api_key = additional_information.get('authorization')
        if api_key:
            self.auth_header = {"Authorization": f"Bearer {api_key}"}
        else:
            self.auth_header = {}

    @staticmethod
    def get_description() -> SensorDescription:
        return SensorDescription(
            sensor_class_id='388a4c21-c845-480c-945c-f54eb60e17d0',
            model='SenseCAP S2120 8-in-1',
            connection=ConnectionType.HTTP,
            parameter='Light Intensity;Licht Stärke',
            unit='lux',
            tags={
                'info': 'see local SenseCap config to set matching interval. Most common is hourly.'
            },
            fields=[
                FieldDescription(
                    name='http',
                    type=FieldType.STRING,
                    rules=[
                        ValidHttpEndpointRule(),
                    ]
                ),
                FieldDescription(
                    name='authorization',
                    type=FieldType.STRING,
                    rules=[]
                ),
            ]
        )

    def get_measurement(self) -> MeasurementResult:
        url = self.http_endpoint + "?limit=1&order=-received_at"
        response = requests.get(url, headers=self.auth_header)
        response.raise_for_status()
        json_data = response.json()

        value = None
        timestamp = None

        for msg in json_data.get("result", {}).get("uplink_message", {}).get("decoded_payload", {}).get("messages",
                                                                                                        []):
            if msg["type"] == "Light Intensity":
                value = msg["measurementValue"]
                break

        ttn_timestamp = json_data.get("result", {}).get("uplink_message", {}).get("received_at")
        if ttn_timestamp:
            timestamp = parse_datetime(ttn_timestamp)
        print(value, timestamp)
        return MeasurementResult(value=value, timestamp=timestamp)

class HttpWeatherStationUVIndexSensor(TypedSensor):
    http_endpoint = None
    auth_header: Optional[dict] = None

    def init_additional_information(self):
        additional_information = json.loads(self.sensor_config.additionalInformation)
        self.http_endpoint = additional_information['http']
        api_key = additional_information.get('authorization')
        if api_key:
            self.auth_header = {"Authorization": f"Bearer {api_key}"}
        else:
            self.auth_header = {}

    @staticmethod
    def get_description() -> SensorDescription:
        return SensorDescription(
            sensor_class_id='61e563fc-3acd-4cc6-981b-5ad26b663209',
            model='SenseCAP S2120 8-in-1',
            connection=ConnectionType.HTTP,
            parameter='UV Index;UV Index',
            unit='UV',
            tags={
                'info': 'see local SenseCap config to set matching interval. Most common is hourly.'
            },
            fields=[
                FieldDescription(
                    name='http',
                    type=FieldType.STRING,
                    rules=[
                        ValidHttpEndpointRule(),
                    ]
                ),
                FieldDescription(
                    name='authorization',
                    type=FieldType.STRING,
                    rules=[]
                ),
            ]
        )

    def get_measurement(self) -> MeasurementResult:
        url = self.http_endpoint + "?limit=1&order=-received_at"
        response = requests.get(url, headers=self.auth_header)
        response.raise_for_status()
        json_data = response.json()

        value = None
        timestamp = None

        for msg in json_data.get("result", {}).get("uplink_message", {}).get("decoded_payload", {}).get("messages",
                                                                                                        []):
            if msg["type"] == "UV Index":
                value = msg["measurementValue"]
                break

        ttn_timestamp = json_data.get("result", {}).get("uplink_message", {}).get("received_at")
        if ttn_timestamp:
            timestamp = parse_datetime(ttn_timestamp)
        print(value, timestamp)
        return MeasurementResult(value=value, timestamp=timestamp)

class HttpWeatherStationWindSpeedSensor(TypedSensor):
    http_endpoint = None
    auth_header: Optional[dict] = None

    def init_additional_information(self):
        additional_information = json.loads(self.sensor_config.additionalInformation)
        self.http_endpoint = additional_information['http']
        api_key = additional_information.get('authorization')
        if api_key:
            self.auth_header = {"Authorization": f"Bearer {api_key}"}
        else:
            self.auth_header = {}

    @staticmethod
    def get_description() -> SensorDescription:
        return SensorDescription(
            sensor_class_id='f9cd248d-6332-419f-9563-187ee785df33',
            model='SenseCAP S2120 8-in-1',
            connection=ConnectionType.HTTP,
            parameter='Wind Speed;Wind Gschwindigkeit',
            unit='km/h',
            tags={
                'info': 'see local SenseCap config to set matching interval. Most common is hourly.'
            },
            fields=[
                FieldDescription(
                    name='http',
                    type=FieldType.STRING,
                    rules=[
                        ValidHttpEndpointRule(),
                    ]
                ),
                FieldDescription(
                    name='authorization',
                    type=FieldType.STRING,
                    rules=[]
                ),
            ]
        )

    def get_measurement(self) -> MeasurementResult:
        url = self.http_endpoint + "?limit=1&order=-received_at"
        response = requests.get(url, headers=self.auth_header)
        response.raise_for_status()
        json_data = response.json()

        value = None
        timestamp = None

        for msg in json_data.get("result", {}).get("uplink_message", {}).get("decoded_payload", {}).get("messages",
                                                                                                        []):
            if msg["type"] == "Wind Speed":
                value = msg["measurementValue"]
                break

        ttn_timestamp = json_data.get("result", {}).get("uplink_message", {}).get("received_at")
        if ttn_timestamp:
            timestamp = parse_datetime(ttn_timestamp)
        print(value, timestamp)
        return MeasurementResult(value=value, timestamp=timestamp)

class HttpWeatherStationWindDirectionSensor(TypedSensor):
    http_endpoint = None
    auth_header: Optional[dict] = None

    def init_additional_information(self):
        additional_information = json.loads(self.sensor_config.additionalInformation)
        self.http_endpoint = additional_information['http']
        api_key = additional_information.get('authorization')
        if api_key:
            self.auth_header = {"Authorization": f"Bearer {api_key}"}
        else:
            self.auth_header = {}

    @staticmethod
    def get_description() -> SensorDescription:
        return SensorDescription(
            sensor_class_id='62c4fe04-150a-41c4-a49d-c6585416aa9d',
            model='SenseCAP S2120 8-in-1',
            connection=ConnectionType.HTTP,
            parameter='Wind Direction;Wind Richtung',
            unit='°',
            tags={
                'info': 'see local SenseCap config to set matching interval. Most common is hourly.'
            },
            fields=[
                FieldDescription(
                    name='http',
                    type=FieldType.STRING,
                    rules=[
                        ValidHttpEndpointRule(),
                    ]
                ),
                FieldDescription(
                    name='authorization',
                    type=FieldType.STRING,
                    rules=[]
                ),
            ]
        )

    def get_measurement(self) -> MeasurementResult:
        url = self.http_endpoint + "?limit=1&order=-received_at"
        response = requests.get(url, headers=self.auth_header)
        response.raise_for_status()
        json_data = response.json()

        value = None
        timestamp = None

        for msg in json_data.get("result", {}).get("uplink_message", {}).get("decoded_payload", {}).get("messages",
                                                                                                        []):
            if msg["type"] == "Wind Direction Sensor":
                value = msg["measurementValue"]
                break

        ttn_timestamp = json_data.get("result", {}).get("uplink_message", {}).get("received_at")
        if ttn_timestamp:
            timestamp = parse_datetime(ttn_timestamp)
        print(value, timestamp)
        return MeasurementResult(value=value, timestamp=timestamp)

class HttpWeatherStationRainGaugeSensor(TypedSensor):
    http_endpoint = None
    auth_header: Optional[dict] = None

    def init_additional_information(self):
        additional_information = json.loads(self.sensor_config.additionalInformation)
        self.http_endpoint = additional_information['http']
        api_key = additional_information.get('authorization')
        if api_key:
            self.auth_header = {"Authorization": f"Bearer {api_key}"}
        else:
            self.auth_header = {}

    @staticmethod
    def get_description() -> SensorDescription:
        return SensorDescription(
            sensor_class_id='d17901dd-9179-4a5c-b506-927b90986b73',
            model='SenseCAP S2120 8-in-1',
            connection=ConnectionType.HTTP,
            parameter='Rain Gauge;Regen Pegel',
            unit='mm',
            tags={
                'info': 'see local SenseCap config to set matching interval. Most common is hourly.'
            },
            fields=[
                FieldDescription(
                    name='http',
                    type=FieldType.STRING,
                    rules=[
                        ValidHttpEndpointRule(),
                    ]
                ),
                FieldDescription(
                    name='authorization',
                    type=FieldType.STRING,
                    rules=[]
                ),
            ]
        )

    def get_measurement(self) -> MeasurementResult:
        url = self.http_endpoint + "?limit=1&order=-received_at"
        response = requests.get(url, headers=self.auth_header)
        response.raise_for_status()
        json_data = response.json()

        value = None
        timestamp = None

        for msg in json_data.get("result", {}).get("uplink_message", {}).get("decoded_payload", {}).get("messages",
                                                                                                        []):
            if msg["type"] == "Rain Gauge":
                value = msg["measurementValue"]
                break

        ttn_timestamp = json_data.get("result", {}).get("uplink_message", {}).get("received_at")
        if ttn_timestamp:
            timestamp = parse_datetime(ttn_timestamp)
        print(value, timestamp)
        return MeasurementResult(value=value, timestamp=timestamp)

class HttpWeatherStationBarometricPressureSensor(TypedSensor):
    http_endpoint = None
    auth_header: Optional[dict] = None

    def init_additional_information(self):
        additional_information = json.loads(self.sensor_config.additionalInformation)
        self.http_endpoint = additional_information['http']
        api_key = additional_information.get('authorization')
        if api_key:
            self.auth_header = {"Authorization": f"Bearer {api_key}"}
        else:
            self.auth_header = {}

    @staticmethod
    def get_description() -> SensorDescription:
        return SensorDescription(
            sensor_class_id='c1d19d8c-8ba3-4607-8ebb-ee0faec46042',
            model='SenseCAP S2120 8-in-1',
            connection=ConnectionType.HTTP,
            parameter='Barometric Pressure;Barometischer Druck',
            unit='mm',
            tags={
                'info': 'see local SenseCap config to set matching interval. Most common is hourly.'
            },
            fields=[
                FieldDescription(
                    name='http',
                    type=FieldType.STRING,
                    rules=[
                        ValidHttpEndpointRule(),
                    ]
                ),
                FieldDescription(
                    name='authorization',
                    type=FieldType.STRING,
                    rules=[]
                ),
            ]
        )

    def get_measurement(self) -> MeasurementResult:
        url = self.http_endpoint + "?limit=1&order=-received_at"
        response = requests.get(url, headers=self.auth_header)
        response.raise_for_status()
        json_data = response.json()

        value = None
        timestamp = None

        for msg in json_data.get("result", {}).get("uplink_message", {}).get("decoded_payload", {}).get("messages",
                                                                                                        []):
            if msg["type"] == "Barometric Pressure":
                value = msg["measurementValue"]
                break

        ttn_timestamp = json_data.get("result", {}).get("uplink_message", {}).get("received_at")
        if ttn_timestamp:
            timestamp = parse_datetime(ttn_timestamp)
        print(value, timestamp)
        return MeasurementResult(value=value, timestamp=timestamp)
