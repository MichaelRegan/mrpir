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
    client_id: str
    state_topic: str
    host: str
    port: int
    username: str = None
    password: str = None
    config_topic: str = None
    config_payload: str = None

@dataclass
class DisplayConfig:
    """A class to store display configuration settings."""
    timezone: str
    brightness_path: str
    dim_brightness: int
    bright_brightness: int
    transition_time: int

@dataclass
class TimeoutConfig:
    """A class to store timeout configuration settings."""
    # no_motion_timeout: int
    sundown_timeout: int

@dataclass
class SensorConfig:
    """A class to store sensor configuration settings."""
    gpio_pin: int
    no_motion_delay: int

@dataclass
class TimeEventsConfig:
    location_name: str
    region: str
    latitude: float
    longitude: float


class Config:
    """
    Loads and stores configuration settings from environment variables.
    Provides default values for settings if not specified in the environment.
    """

    def __init__(self):
        """
        Initializes the Config class by loading environment variables
        and setting default values where necessary.
        """
        # Load environment variables from the specified .env file location
        env_path = os.path.expanduser('~/.mrpir/config/.env')
        load_dotenv(dotenv_path=env_path)
        

        # Display settings
        self.display = DisplayConfig(
            brightness_path=os.getenv('BRIGHTNESS_PATH', '/sys/class/backlight/10-0045/brightness'),
            dim_brightness=int(os.getenv('DIM_BRIGHTNESS', '0')),
            bright_brightness=int(os.getenv('BRIGHT_BRIGHTNESS', '90')),
            transition_time=int(os.getenv('TRANSITION_TIME', '2'))
            # timezone=os.getenv('timezone', 'America/Los_Angeles')
        )

        # Timeout settings
        self.timeouts = TimeoutConfig(
            # no_motion_timeout=int(os.getenv('NO_MOTION_TIMEOUT', '60')),
            sundown_timeout=int(os.getenv('SUNDOWN_TIMEOUT', '3600'))
        )

        # MQTT settings
        mqtt_device = os.getenv('MQTT_DEVICE', 'mrpir')
        self.mqtt = MQTTConfig(
            device=mqtt_device,
            client_id=os.getenv("MQTT_CLIENT_ID", None),
            state_topic=f"homeassistant/binary_sensor/{mqtt_device}/state",
            host=os.getenv('MQTT_HOST', 'localhost'),
            port=int(os.getenv('MQTT_PORT', '1883')),
            username=os.getenv('MQTT_USERNAME', None),
            password=os.getenv('MQTT_PASSWORD', None),
            config_topic=f'homeassistant/binary_sensor/{mqtt_device}/config',
            config_payload=(
                '{"name": "%s_motion", '
                '"device_class": "motion", '
                '"unique_id": "pir_%s_id_%s_id", '
                '"state_topic": "%s"}' % (
                    mqtt_device, mqtt_device, mqtt_device, f"homeassistant/binary_sensor/{mqtt_device}/state")
            )
        )

        # Sensor settings
        self.sensor = SensorConfig(
            gpio_pin=int(os.getenv('GPIO_PIN', '23')),
            no_motion_delay=int(os.getenv('NO_MOTION_DELAY', '60'))
        )

        # time event settings
        self.time_events = TimeEventsConfig(
            location_name=os.getenv('LOCATION_NAME', 'New York'),
            region=os.getenv('REGION', 'USA'),
            latitude=float(os.getenv('LATITUDE', '40.7128')),
            longitude=float(os.getenv('LONGITUDE', '-74.0060'))
        )
