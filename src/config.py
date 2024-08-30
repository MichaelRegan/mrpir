"""
Configuration module.

This module loads environment variables using dotenv and provides
a Config class to access these variables throughout the application.
"""

import os
from dotenv import load_dotenv
from dataclasses import dataclass


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
    brightness_path: str
    dim_brightness: int
    bright_brightness: int
    transition_time: int
    dim_delay: int


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
    A class to load and store configuration settings from environment variables.
    """

    def __init__(self):
        """
        Initialize the configuration by loading environment variables
        and setting default values where necessary.
        """
        load_dotenv()

        # Display settings
        self.display = DisplayConfig(
            brightness_path=os.getenv('BRIGHTNESS_PATH', '/sys/class/backlight/10-0045/brightness'),
            dim_brightness=int(os.getenv('DIM_BRIGHTNESS', '0')),
            bright_brightness=int(os.getenv('BRIGHT_BRIGHTNESS', '90')),
            transition_time=int(os.getenv('TRANSITION_TIME', '30')),
            dim_delay=int(os.getenv('DIM_DELAY', '30'))
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
            gpio_pin=int(os.getenv('GPIO_PIN', '17')),
            no_motion_timeout=int(os.getenv('NO_MOTION_TIMEOUT', '60'))
        )


# Instantiate the config to make it available globally
config = Config()
