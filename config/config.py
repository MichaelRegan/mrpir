# config.py
import os
import logging
from dotenv import load_dotenv

load_dotenv()

class Config:
    try:
        MQTT_SERVER = os.getenv("MQTT_SERVER")
        if MQTT_SERVER is None:
            raise EnvironmentError("MQTT_SERVER environment variable is required but not set.")
        
        MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
        MQTT_USER = os.getenv('MQTT_USER', "user")
        MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "password")
        BRIGHTNESS_DEVICE = os.getenv('BRIGHTNESS_DEVICE')
        if BRIGHTNESS_DEVICE is None:
            raise EnvironmentError("BRIGHTNESS_DEVICE environment variable is required but not set. Check /sys/class/backlight.")

        BRIGHTNESS_PATH = f'/sys/class/backlight/{BRIGHTNESS_DEVICE}/brightness'
        
        DIM_BRIGHTNESS = int(os.getenv("DIM_BRIGHTNESS", 0))
        BRIGHT_BRIGHTNESS = int(os.getenv("BRIGHT_BRIGHTNESS", 230))
        TRANSITION_TIME = int(os.getenv("TRANSITION_TIME", 2))
        NO_MOTION_DELAY = int(os.getenv("NO_MOTION_DELAY", 30))
        GPIO_PIN = int(os.getenv("GPIO_PIN"))
        if GPIO_PIN is None:
            raise EnvironmentError("GPIO_PIN environment variable is required but not set.")
        
        MQTT_DEVICE = os.getenv("MQTT_DEVICE", "officescreen")
        if MQTT_DEVICE is None:
            raise EnvironmentError("MQTT_DEVICE environment variable is required but not set.")
        
        MQTT_CLIENT_ID = os.getenv("MQTT_CLIENT_ID", "pir_officescreen_id")
        if MQTT_CLIENT_ID is None:
            raise EnvironmentError("MQTT_CLIENT_ID environment variable is required but not set.")

        # Build mqtt topics and config payload
        STATE_TOPIC = f'homeassistant/binary_sensor/' + MQTT_DEVICE + '/state'
        CONFIG_TOPIC = f"homeassistant/binary_sensor/" + MQTT_DEVICE + "/config"
        CONFIG_PAYLOAD = f'{{"name": "{MQTT_DEVICE}_motion", "device_class": "motion", "unique_id": "{MQTT_CLIENT_ID}_{MQTT_DEVICE}_id", "state_topic": "{STATE_TOPIC}"}}'

        # New night mode settings
        NIGHT_START_HOUR = int(os.getenv("NIGHT_START_HOUR", 22))  # Default to 10 PM
        NIGHT_END_HOUR = int(os.getenv("NIGHT_END_HOUR", 6))        # Default to 6 AM
        NO_MOTION_TIMEOUT = int(os.getenv("NO_MOTION_TIMEOUT", 3600))  # Default to 1 hour
        
        # Get screen_device
        SCREEN_DEVICE = os.getenv("SCREEN_DEVICE");
        if SCREEN_DEVICE is None:
            raise EnvironmentError("SCREEN_DEVICE environment variable is required but not set. Should be HDMI-1, DSI-1, etc.")

        SCREEN_OFF_COMMAND = f"wlr-randr --output {SCREEN_DEVICE} --off"
        SCREEN_ON_COMMAND = f"wlr-randr --output {SCREEN_DEVICE} --on"

        # Load and configure logging level
        LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
        logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO), 
                            format='%(asctime)s - %(levelname)s - %(message)s')
        
    except ValueError as e:
        logging.error(f"Error parsing environment variable: {e}")
    except EnvironmentError as e:
        logging.critical(f"Critical environment variable error: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error occurred while loading configuration: {e}")
