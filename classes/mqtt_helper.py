# mqtt_helper.py
import paho.mqtt.client as mqtt
import logging
from config.config import Config

class MqttHelper:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.username_pw_set(username=Config.MQTT_USER, password=Config.MQTT_PASSWORD)
        self.client.connect(Config.MQTT_SERVER, Config.MQTT_PORT, 60)

    def publish(self, topic, message):
        try:
            self.client.publish(topic, message)
            logging.info(f"Published '{message}' to topic '{topic}'")
        except Exception as e:
            logging.error(f"Error publishing MQTT message: {e}")

    def publish_config(self):
        try:            
            self.client.publish(Config.CONFIG_TOPIC, Config.CONFIG_PAYLOAD, retain=True)
            logging.info(f"Published Config '{Config.CONFIG_PAYLOAD}' to topic '{Config.CONFIG_TOPIC}'")
        except Exception as e:
            logging.error(f"Error publishing MQTT message: {e}")
            
