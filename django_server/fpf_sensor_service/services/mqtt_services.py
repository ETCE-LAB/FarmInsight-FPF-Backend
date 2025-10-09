import paho.mqtt.client as mqtt
import threading
import json
from django.conf import settings

from fpf_sensor_service.sensors import ConnectionType
from .sensor_services import send_measurements
from .auth_services import get_fpf_id

from django_server import settings
from apscheduler.schedulers.background import BackgroundScheduler

from fpf_sensor_service.models import SensorConfig, SensorMeasurement
from fpf_sensor_service.sensors import TypedSensorFactory
from fpf_sensor_service.utils import get_logger


logger = get_logger()
'''
daemon=False is required in deployment to run correctly as a systemd service,
but it does not play nice with running it in the IDE during development. 
DO NOT OVERRIDE WHEN MERGING INTO DEPLOYMENT! 
'''
scheduler = BackgroundScheduler() # daemon=False)
typed_sensor_factory = TypedSensorFactory()


class MQTTService:
    def __init__(self):
        self.client = mqtt.Client()
        self.connected = False
        #self.client.on_log = self.on_log

        # Optional: enable auth if using user/pass
        if settings.MQTT_CONFIG["USERNAME"] and settings.MQTT_CONFIG["PASSWORD"]:
            self.client.username_pw_set(settings.MQTT_CONFIG["USERNAME"], settings.MQTT_CONFIG["PASSWORD"])

        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

    def start(self):
        # Start in a separate thread
        thread = threading.Thread(target=self._run, daemon=True)
        thread.start()

    def _run(self):
        try:
            self.client.connect(settings.MQTT_CONFIG["HOST"], settings.MQTT_CONFIG["PORT"], keepalive=60)
            self.client.loop_forever()
        except Exception as e:
            print(f"[MQTT] Initial connection error: {e}")

    def on_connect(self, client, userdata, flags, rc):
        self.connected = True

        # Subscribe to sensor topics
        for sensor in SensorConfig.objects.filter(isActive=True):
            sensor_class = typed_sensor_factory.get_typed_sensor_class(str(sensor.sensorClassId))
            curr_sensor = sensor_class(sensor)

            # Only with connection type == MQTT
            if curr_sensor.get_description().connection == ConnectionType.MQTT or curr_sensor.get_description().connection == ConnectionType.HTTP_MQTT:

                try:
                    additional_info = json.loads(sensor.additionalInformation)
                    topic = additional_info.get("mqtt_topic")
                    if topic:
                        print(f"[MQTT] Subscribing to {topic}")
                        client.subscribe(topic)
                    else:
                        print(f"[MQTT] No mqtt_topic found in additionalInformation for sensor {sensor.id}")
                except json.JSONDecodeError as e:
                    print(f"[MQTT] Failed to parse additionalInformation for sensor {sensor.id}: {e}")

    def on_disconnect(self, client, userdata, rc):
        self.connected = False
        print(f"[MQTT] Disconnected. Code: {rc}")

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            topic = msg.topic
            # Try to find the sensor config with this topic
            matching_sensor = None
            for sensor in SensorConfig.objects.filter(isActive=True):
                try:
                    additional_info = json.loads(sensor.additionalInformation)
                    if additional_info.get("mqtt_topic") == topic:
                        matching_sensor = sensor
                        break
                except json.JSONDecodeError:
                    continue

            if not matching_sensor:
                logger.warning(f"[MQTT] No sensor found for topic {topic}")
                return

            # Extract value and timestamp of payload
            sensor_class = typed_sensor_factory.get_typed_sensor_class(str(matching_sensor.sensorClassId))
            curr_sensor = sensor_class(matching_sensor)

            measurement = curr_sensor.get_measurement(payload)

            if measurement.value is None :
                logger.warning(f"[MQTT] Missing value in payload from {topic}: {payload}")
                return

            if measurement.timestamp is None:
                SensorMeasurement.objects.create(
                    sensor=matching_sensor,
                    value=measurement.value,
                )
            else:
                SensorMeasurement.objects.create(
                    sensor=matching_sensor,
                    value=measurement.value,
                    measuredAt=measurement.timestamp
                )

            send_measurements(sensor_id=matching_sensor.id)

            logger.debug("Sensor MQTT measurements sent", extra={'extra': {'sensorId': matching_sensor.id}})

        except Exception as e:
            logger.error(f"Error processing MQTT measurement: {e}", extra={'extra': {'fpfId': get_fpf_id()}})
