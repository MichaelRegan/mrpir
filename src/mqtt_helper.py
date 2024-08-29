import time
import paho.mqtt.client as mqtt
import threading
from utils.logger import logger

class MQTTHelper:
    def __init__(self, config, sensor_monitor):
        self.config = config
        self.sensor_monitor = sensor_monitor
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self._stop_event = threading.Event()
        self._thread = None  # Add a reference to the thread

        if self.config.mqtt_username and self.config.mqtt_password:
            self.client.username_pw_set(self.config.mqtt_username, self.config.mqtt_password)
            logger.info("MQTT username and password set")

    def on_connect(self, client, userdata, flags, rc):
        logger.info("Connected to MQTT broker")

    def on_disconnect(self, client, userdata, rc):
        logger.warning("Disconnected from MQTT broker")

    def start(self):
        try:
            logger.info(f"Connecting to MQTT broker at {self.config.mqtt_host}:{self.config.mqtt_port}")
            self.client.connect(self.config.mqtt_host, self.config.mqtt_port, 60)
            self.client.loop_start()
            self._thread = threading.Thread(target=self.monitor_sensor_state)
            self._thread.start()
        except Exception as e:
            logger.error(f"MQTT connection error: {e}")

    def monitor_sensor_state(self):
        while not self._stop_event.is_set():
            state = "ON" if self.sensor_monitor.motion_detected else "OFF"
            self.client.publish(self.config.state_topic, state)
            logger.info(f"Published state {state} to {self.config.state_topic}")
            time.sleep(10)

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join()  # Ensure the thread has finished
        self.client.loop_stop()
        self.client.disconnect()
