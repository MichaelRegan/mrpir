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
        self.client.on_log = self.on_log  # Enable logging for the MQTT client
        self._stop_event = threading.Event()
        self._thread = None
        self.last_sent_state = None  # Track the last state sent to Home Assistant

        if self.config.mqtt_username and self.config.mqtt_password:
            self.client.username_pw_set(self.config.mqtt_username, self.config.mqtt_password)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("Connected to MQTT broker")
        else:
            logger.error(f"Failed to connect to MQTT broker, return code {rc}")

    def on_disconnect(self, client, userdata, rc):
        logger.warning("Disconnected from MQTT broker")

    def on_log(self, client, userdata, level, buf):
        logger.debug(f"MQTT Log: {buf}")

    def start(self):
        try:
            self.client.connect(self.config.mqtt_host, self.config.mqtt_port, 60)
            self.client.loop_start()
            self._thread = threading.Thread(target=self.monitor_sensor_state)
            self._thread.start()
        except Exception as e:
            logger.error(f"MQTT connection error: {e}")

    def monitor_sensor_state(self):
        while not self._stop_event.is_set():
            current_state = "ON" if self.sensor_monitor.motion_detected else "OFF"
            
            # Only send an update if the state has changed
            if current_state != self.last_sent_state:
                self.client.publish(self.config.state_topic, current_state)
                logger.info(f"Published state {current_state} to {self.config.state_topic}")
                self.last_sent_state = current_state  # Update the last sent state
            
            time.sleep(1)  # Adjust the sleep time as necessary

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join()
        self.client.loop_stop()
        self.client.disconnect()
