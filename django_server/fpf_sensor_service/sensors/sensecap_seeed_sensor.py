import json
import requests
from dateutil.parser import parse as parse_datetime
from datetime import datetime

from .measurement_result import MeasurementResult
from .typed_sensor import TypedSensor
from .sensor_description import SensorDescription, ConnectionType, FieldDescription, FieldType, ValidHttpEndpointRule


class SenseCapSeeedSensor(TypedSensor):
    http_endpoint = None
    sensor_id = None
    username = None
    password = None

    def init_additional_information(self):
        additional_information = json.loads(self.sensor_config.additionalInformation)
        self.http_endpoint = additional_information['http']
        self.sensor_id = additional_information['sensor_id']
        self.username = additional_information['username']
        self.password = additional_information['password']

    @staticmethod
    def get_description() -> SensorDescription:
        return SensorDescription(
            sensor_class_id='edecce4b-731d-4527-ad28-0b906e1f0da0',
            model='',
            connection=ConnectionType.HTTP,
            parameter='',
            unit='',
            tags={
                'info': 'See local Sensor config to set matching interval.;Aus lokaler SenseCap Konfiguration passendes Intervall entnehmen.',
            },
            fields=[
                FieldDescription(
                    name='http',
                    type=FieldType.STRING,
                    rules=[ValidHttpEndpointRule()],
                ),
                FieldDescription(
                    name='sensor_id',
                    type=FieldType.INTEGER,
                    rules=[],
                ),
                FieldDescription(
                    name='username',
                    type=FieldType.STRING,
                    rules=[],
                ),
                FieldDescription(
                    name='password',
                    type=FieldType.STRING,
                    rules=[],
                ),
            ]
        )

    def get_measurement(self) -> MeasurementResult:

        response = requests.get(
            self.http_endpoint,
            auth=(self.username, self.password),
            timeout=10
        )

        response.raise_for_status()
        data = response.json()

        sensor_id = self.sensor_id

        points = data.get("data", [{}])[0].get("points", [])

        # Try to get the matching measurement
        matched_points = [p for p in points if p.get("measurement_id") == sensor_id]

        if not matched_points:
            raise ValueError(f"No measurement with id {sensor_id} found")

        # Get the latest measurement in case there are multiple measurements returned
        newest_point = max(
            matched_points,
            key=lambda p: datetime.fromisoformat(p["time"].replace("Z", "+00:00"))
        )

        value = newest_point.get("measurement_value")

        timestamp = None
        if newest_point.get("time"):
            timestamp = parse_datetime(newest_point["time"])

        return MeasurementResult(value=value, timestamp=timestamp)
