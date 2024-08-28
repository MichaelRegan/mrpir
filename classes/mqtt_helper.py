"""Module providing a class to manage MQTT communication."""
import logging
from config.config import Config  # Local import # pylint: disable=import-error
import paho.mqtt.client as mqtt

class MqttHelper:
    def __init__(self, broker, port, username=None, password=None):
        """Initialize the MQTT client."""
        self.client = mqtt.Client()
        self.broker = broker
        self.port = port
        self.username = username
        self.password = password

        if username and password:
            self.client.username_pw_set(username, password)

        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_publish = self.on_publish

    def on_connect(self, client, userdata, flags, rc):
        """Callback for when the client receives a CONNACK response from the server."""
        if rc == 0:
            logging.info("Connected to MQTT Broker!")
        else:
            logging.error(f"Failed to connect, return code {rc}")

    def on_disconnect(self, client, userdata, rc):
        """Callback for when the client disconnects from the server."""
        logging.info("Disconnected from MQTT Broker")

    def on_publish(self, client, userdata, mid):
        """Callback for when a message has been published."""
        logging.info(f"Message {mid} published.")

    def connect(self):
        """Connect to the MQTT broker."""
        try:
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
        except Exception as e:
            logging.error(f"Failed to connect to MQTT Broker: {e}")

    def publish(self, topic, payload, qos=0, retain=False):
        """Publish a message to a specified topic."""
        try:
            result = self.client.publish(topic, payload, qos, retain)
            result.wait_for_publish()
        except Exception as e:
            logging.error(f"Failed to publish message: {e}")

    def disconnect(self):
        """Disconnect from the MQTT broker."""
        self.client.loop_stop()
        self.client.disconnect()
