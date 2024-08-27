# mqtt_helper.py
"""Module providing a supporting class to manage MQTT calls."""

import logging
from config.config import Config # pylint: disable=import-error
import paho.mqtt.client as mqtt # pylint: disable=import-error

class MqttHelper:
    """Class representing an MQTT Queue"""
    def __init__(self):
        """Contructor"""
        self.client = mqtt.Client()
        self.client.username_pw_set(username=Config.MQTT_USER, password=Config.MQTT_PASSWORD)
        self.client.connect(Config.MQTT_SERVER, Config.MQTT_PORT, 60)

    def publish(self, topic, message):
        """Publish messages to the provided topic to MQTT"""
        try:
            self.client.publish(topic, message)
            logging.info(f"Published '{message}' to topic '{topic}'")
        except Exception as e:
            logging.error(f"Error publishing MQTT message: {e}")

    def publish_config(self):
        """Publish the config for the PIR sensor for Home Assistant through MQTT"""
        try:
            self.client.publish(Config.CONFIG_TOPIC, Config.CONFIG_PAYLOAD, retain=True)
            logging.info(f"Published Config '{Config.CONFIG_PAYLOAD}' to topic '{Config.CONFIG_TOPIC}'")
        except Exception as e:
            logging.error(f"Error publishing MQTT message: {e}")
