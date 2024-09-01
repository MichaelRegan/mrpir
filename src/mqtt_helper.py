import paho.mqtt.client as mqtt
from utils.logger import logger


class MQTTHelper:
    """
    Helper class to manage MQTT communication, including connecting to the broker,
    handling motion detection events, and publishing states to Home Assistant.

    Attributes:
        config (dict): Configuration settings for the MQTT client.
        client (mqtt.Client): The MQTT client instance.
        last_sent_state (str): The last state sent to Home Assistant.
    """

    def __init__(self, config):
        """
        Initializes the MQTTHelper with the given configuration.

        Args:
            config (dict): Configuration settings for the MQTT client.
        """
        self.config = config
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_log = self.on_log  # Enable logging for the MQTT client
        self.client.client_id = "pir_officescreen_id"
        self.last_sent_state = None  # Track the last state sent to Home Assistant

        # Set MQTT username and password if provided in the configuration
        if self.config.mqtt_username and self.config.mqtt_password:
            self.client.username_pw_set(self.config.mqtt_username, self.config.mqtt_password)

    def on_connect(self, client, userdata, flags, rc):
        """
        Callback for when the client connects to the MQTT broker.

        Args:
            client (mqtt.Client): The client instance for this callback.
            userdata (Any): The private user data.
            flags (dict): Response flags sent by the broker.
            rc (int): The connection result.
        """
        if rc == 0:
            logger.info("Connected to MQTT broker")
        else:
            logger.error(f"Failed to connect to MQTT broker, return code {rc}")

    def on_disconnect(self, client, userdata, rc):
        """
        Callback for when the client disconnects from the MQTT broker.

        Args:
            client (mqtt.Client): The client instance for this callback.
            userdata (Any): The private user data.
            rc (int): The disconnection result.
        """
        logger.warning("Disconnected from MQTT broker")

    def on_log(self, client, userdata, level, buf):
        """
        Callback for logging MQTT client messages.

        Args:
            client (mqtt.Client): The client instance for this callback.
            userdata (Any): The private user data.
            level (int): The log level.
            buf (str): The log message.
        """
        logger.debug(f"MQTT Log: {buf}")

    def on_motion(self) -> None:
        """
        Handles motion detected events by publishing the 'ON' state to Home Assistant.
        """
        logger.debug("MQTTHelper: Motion detected, publishing state ON.")
        if self.last_sent_state != "ON":
            self.publish_state("ON")

    def on_no_motion(self) -> None:
        """
        Handles no motion detected events by publishing the 'OFF' state to Home Assistant.
        """
        logger.debug("MQTTHelper: No motion detected, publishing state OFF.")
        if self.last_sent_state != "OFF":
            self.publish_state("OFF")

    def publish_state(self, state: str) -> None:
        """
        Publishes the given state to the configured MQTT topic if the state has changed.

        Args:
            state (str): The state to publish ('ON' or 'OFF').
        """
        if state != self.last_sent_state:
            self.client.publish(self.config.state_topic, state)
            logger.info(f"Published state {state} to {self.config.state_topic}")
            self.last_sent_state = state  # Update the last sent state

    def start(self) -> None:
        """
        Starts the MQTT client and connects to the broker.
        """
        try:
            self.client.connect(self.config.mqtt_host, self.config.mqtt_port, 60)
            self.client.loop_start()
        except Exception as e:
            logger.error(f"MQTT connection error: {e}")

    def stop(self) -> None:
        """
        Stops the MQTT client and disconnects from the broker.
        """
        self.client.loop_stop()
        self.client.disconnect()
