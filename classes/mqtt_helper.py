"""Module providing a supporting class to manage MQTT calls."""

import logging
import paho.mqtt.client as mqtt  # pylint: disable=import-error
from config.config import Config  # pylint: disable=import-error


class MqttHelper:
    """Class representing an MQTT Queue."""

    def __init__(self):
        """Constructor."""
        self.client = mqtt.Client()
        self.client.username_pw_set(username=Config.MQTT_USER, password=Config.MQTT_PASSWORD)
        self.client.connect(Config.MQTT_SERVER, Config.MQTT_PORT, 60)

    def publish(self, topic, message):
        """Publish messages to the provided topic to MQTT."""
        try:
            self.client.publish(topic, message)
            logging.info("Published '%s' to topic '%s'", message, topic)
        except (mqtt.MQTTException, ValueError) as e:
            logging.error("Error publishing MQTT message: %s", e)

    def publish_config(self):
        """Publish the config for the PIR sensor for Home Assistant through MQTT."""
        try:
            self.client.publish(Config.CONFIG_TOPIC, Config.CONFIG_PAYLOAD, retain=True)
            logging.info(
                "Published Config '%s' to topic '%s'", Config.CONFIG_PAYLOAD, Config.CONFIG_TOPIC
            )
        except (mqtt.MQTTException, ValueError) as e:
            logging.error("Error publishing MQTT config: %s", e)
