"""Configuration module to load and manage environment variables."""

import os
import logging
from dotenv import load_dotenv  # pylint: disable=import-error

load_dotenv()


class Config: # pylint: disable=too-few-public-methods
    """Configuration class for loading environment variables."""

    try:
        # MQTT configuration
        MQTT_BROKER = os.getenv("MQTT_BROKER")
        if MQTT_BROKER is None:
            raise EnvironmentError("MQTT_BROKER environment variable is required but not set.")

        MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
        MQTT_USERNAME = os.getenv("MQTT_USERNAME", "user")
        MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "password")

        # Brightness configuration
        BRIGHTNESS_DEVICE = os.getenv("BRIGHTNESS_DEVICE")
        if BRIGHTNESS_DEVICE is None:
            raise EnvironmentError("BRIGHTNESS_DEVICE environment variable is required.")

        BRIGHTNESS_PATH = f'/sys/class/backlight/{BRIGHTNESS_DEVICE}/brightness'

        DIM_BRIGHTNESS = int(os.getenv("DIM_BRIGHTNESS", "0"))
        BRIGHT_BRIGHTNESS = int(os.getenv("BRIGHT_BRIGHTNESS", "230"))
        TRANSITION_TIME = int(os.getenv("TRANSITION_TIME", "2"))

        # Motion detection configuration
        NO_MOTION_DELAY = int(os.getenv("NO_MOTION_DELAY", "30"))
        GPIO_PIN = os.getenv("GPIO_PIN")
        if GPIO_PIN is None:
            raise EnvironmentError("GPIO_PIN environment variable is required but not set.")
        GPIO_PIN = int(GPIO_PIN)

        # MQTT device configuration
        MQTT_DEVICE = os.getenv("MQTT_DEVICE", "officescreen")
        if MQTT_DEVICE is None:
            raise EnvironmentError("MQTT_DEVICE environment variable is required but not set.")

        MQTT_CLIENT_ID = os.getenv("MQTT_CLIENT_ID", "pir_officescreen_id")
        if MQTT_CLIENT_ID is None:
            raise EnvironmentError("MQTT_CLIENT_ID environment variable is required but not set.")

        # MQTT topics and config payload
        STATE_TOPIC = f'homeassistant/binary_sensor/{MQTT_DEVICE}/state'
        CONFIG_TOPIC = f'homeassistant/binary_sensor/{MQTT_DEVICE}/config'
        CONFIG_PAYLOAD = (
            '{"name": "%s_motion", '
            '"device_class": "motion", '
            '"unique_id": "%s_%s_id", '
            '"state_topic": "%s"}' % (
                MQTT_DEVICE, MQTT_CLIENT_ID, MQTT_DEVICE, STATE_TOPIC)
        )

        # Night mode settings
        NIGHT_START_HOUR = int(os.getenv("NIGHT_START_HOUR", "22"))  # Default to 10 PM
        NIGHT_END_HOUR = int(os.getenv("NIGHT_END_HOUR", "6"))  # Default to 6 AM
        NO_MOTION_TIMEOUT = int(os.getenv("NO_MOTION_TIMEOUT", "3600"))  # Default to 1 hour

        # Screen device settings
        SCREEN_DEVICE = os.getenv("SCREEN_DEVICE", "HDMI-1")
        if SCREEN_DEVICE is None:
            raise EnvironmentError("SCREEN_DEVICE environment variable is required but not set.")

        SCREEN_OFF_COMMAND = f"wlr-randr --output {SCREEN_DEVICE} --off"
        SCREEN_ON_COMMAND = f"wlr-randr --output {SCREEN_DEVICE} --on"

        # Logging configuration
        LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
        logging.basicConfig(
            level=getattr(logging, LOG_LEVEL, logging.INFO),
            format="%(asctime)s - %(levelname)s - %(message)s"
        )

    except ValueError as e:
        logging.error("Error parsing environment variable: %s", e)
    except EnvironmentError as e:
        logging.critical("Critical environment variable error: %s", e)
        raise
    except RuntimeError as e:
        logging.error("Unexpected error occurred while loading configuration: %s", e)
