import paho.mqtt.client as mqtt
from utils.logger import logger

class MQTTHelper:
    def __init__(self, config, sensor_monitor):
        self.config = config
        self.sensor_monitor = sensor_monitor
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_log = self.on_log  # Enable logging for the MQTT client
        self.last_sent_state = None  # Track the last state sent to Home Assistant

        if self.config.mqtt_username and self.config.mqtt_password:
            self.client.username_pw_set(self.config.mqtt_username, self.config.mqtt_password)

        # Register the callbacks for motion detection and no motion
        self.sensor_monitor.sensor.when_motion = self.handle_motion
        self.sensor_monitor.sensor.when_no_motion = self.handle_no_motion

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("Connected to MQTT broker")
        else:
            logger.error(f"Failed to connect to MQTT broker, return code {rc}")

    def on_disconnect(self, client, userdata, rc):
        logger.warning("Disconnected from MQTT broker")

    def on_log(self, client, userdata, level, buf):
        logger.debug(f"MQTT Log: {buf}")

    def handle_motion(self):
        self.publish_state("ON")

    def handle_no_motion(self):
        self.publish_state("OFF")

    def publish_state(self, state):
        # Only send an update if the state has changed
        if state != self.last_sent_state:
            self.client.publish(self.config.state_topic, state)
            logger.info(f"Published state {state} to {self.config.state_topic}")
            self.last_sent_state = state  # Update the last sent state

    def start(self):
        try:
            self.client.connect(self.config.mqtt_host, self.config.mqtt_port, 60)
            self.client.loop_start()
        except Exception as e:
            logger.error(f"MQTT connection error: {e}")

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()
