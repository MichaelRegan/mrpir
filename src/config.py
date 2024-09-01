"""
Loads and stores configuration settings from environment variables.
Provides default values for settings if not specified in the environment.
"""
import os
from dataclasses import dataclass
from dotenv import load_dotenv # pylint: disable=import-error

@dataclass
class MQTTConfig:
    """A class to store MQTT configuration settings."""
    device: str
    state_topic: str
    host: str
    port: int
    username: str = None
    password: str = None

@dataclass
class DisplayConfig:
    """A class to store display configuration settings."""
    timezone: str
    brightness_path: str
    dim_brightness: int
    bright_brightness: int
    transition_time: int
    # dim_delay: int

@dataclass
class TimeoutConfig:
    """A class to store timeout configuration settings."""
    no_motion_timeout: int
    sundown_timeout: int

@dataclass
class SensorConfig:
    """A class to store sensor configuration settings."""
    gpio_pin: int
    no_motion_timeout: int

class Config:
    """
    Loads and stores configuration settings from environment variables.
    Provides default values for settings if not specified in the environment.

    Attributes:
        brightness_path (str): Path to the screen brightness control file.
        dim_brightness (int): Brightness level for dim state.
        bright_brightness (int): Brightness level for bright state.
        transition_time (int): Time in seconds for brightness transitions.
        timezone (str): Time zone for determining sundown.
        no_motion_timeout (int): Timeout in seconds for detecting no motion.
        sundown_timeout (int): Timeout in seconds for screen off after sundown.
        mqtt_device (str): MQTT device name.
        state_topic (str): MQTT state topic for the device.
        mqtt_host (str): MQTT broker host address.
        mqtt_port (int): MQTT broker port.
        mqtt_username (str): MQTT broker username.
        mqtt_password (str): MQTT broker password.
        gpio_pin (int): GPIO pin number used for motion detection.
    """

    def __init__(self):
        """
        Initializes the Config class by loading environment variables
        and setting default values where necessary.
        """
        load_dotenv()

        # Display settings
        self.display = DisplayConfig(
            brightness_path=os.getenv('BRIGHTNESS_PATH', '/sys/class/backlight/10-0045/brightness'),
            dim_brightness=int(os.getenv('DIM_BRIGHTNESS', '0')),
            bright_brightness=int(os.getenv('BRIGHT_BRIGHTNESS', '90')),
            transition_time=int(os.getenv('TRANSITION_TIME', '30')),
            timezone=os.getenv('timezone', 'America/Los_Angeles')
            # dim_delay=int(os.getenv('DIM_DELAY', '30'))
        )

        # Timeout settings
        self.timeouts = TimeoutConfig(
            no_motion_timeout=int(os.getenv('NO_MOTION_TIMEOUT', '60')),
            sundown_timeout=int(os.getenv('SUNDOWN_TIMEOUT', '3600'))
        )

        # MQTT settings
        mqtt_device = os.getenv('MQTT_DEVICE', 'mrpir')
        self.mqtt = MQTTConfig(
            device=mqtt_device,
            state_topic=f"homeassistant/binary_sensor/{mqtt_device}/state",
            host=os.getenv('MQTT_HOST', 'localhost'),
            port=int(os.getenv('MQTT_PORT', '1883')),
            username=os.getenv('MQTT_USERNAME', None),
            password=os.getenv('MQTT_PASSWORD', None)
        )

        # Sensor settings
        self.sensor = SensorConfig(
            gpio_pin=int(os.getenv('GPIO_PIN', '23')),
            no_motion_timeout=int(os.getenv('NO_MOTION_TIMEOUT', '60'))
        )

        # GPIO settings
        self.gpio_pin = int(os.getenv('GPIO_PIN', '23'))

# Instantiate the Config class to be used throughout the application
config = Config()
