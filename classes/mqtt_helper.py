"""Module providing a class to manage MQTT communication."""

import logging  # Standard import should be first
import paho.mqtt.client as mqtt  # Third-party import # pylint: disable=import-error
from config.config import Config  # Local import # pylint: disable=import-error


class MqttHelper:
    """Helper class for managing MQTT communication."""

    def __init__(self):
        """Initialize the MQTT client and connect to the server."""
        self.client = mqtt.Client()
        self.client.username_pw_set(username=Config.MQTT_USER, password=Config.MQTT_PASSWORD)
        self.client.connect(Config.MQTT_SERVER, Config.MQTT_PORT, 60)

    def publish(self, topic, message):
        """Publish messages to the provided topic via MQTT."""
        try:
            self.client.publish(topic, message)
            logging.info("Published '%s' to topic '%s'", message, topic)
        except mqtt.MQTTException as e:
            logging.error("Error publishing MQTT message: %s", e)

    def publish_config(self):
        """Publish the config for the PIR sensor to Home Assistant via MQTT."""
        try:
            self.client.publish(Config.CONFIG_TOPIC, Config.CONFIG_PAYLOAD, retain=True)
            logging.info("Published Config '%s' to topic '%s'",
                         Config.CONFIG_PAYLOAD, Config.CONFIG_TOPIC)
        except mqtt.MQTTException as e:
            logging.error("Error publishing MQTT config: %s", e)
