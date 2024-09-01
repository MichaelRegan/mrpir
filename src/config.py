import os
from dotenv import load_dotenv


class Config:
    """
    Loads and stores configuration settings from environment variables.
    Provides default values for settings if not specified in the environment.

    Attributes:
        brightness_path (str): Path to the screen brightness control file.
        dim_brightness (int): Brightness level for dim state.
        bright_brightness (int): Brightness level for bright state.
        transition_time (int): Time in seconds for brightness transitions.
        time_zone (str): Time zone for determining sundown.
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

        # Load configuration from environment variables or set default values
        self.brightness_path = os.getenv('BRIGHTNESS_PATH',
                                         '/sys/class/backlight/10-0045/brightness')
        self.dim_brightness = int(os.getenv('DIM_BRIGHTNESS', '0'))
        self.bright_brightness = int(os.getenv('BRIGHT_BRIGHTNESS', '90'))
        self.transition_time = int(os.getenv('TRANSITION_TIME', '30'))
        self.time_zone = os.getenv('TIME_ZONE', 'America/Los_Angeles')
        self.no_motion_timeout = int(os.getenv('NO_MOTION_TIMEOUT', '60'))
        self.sundown_timeout = int(os.getenv('SUNDOWN_TIMEOUT', '3600'))
        self.mqtt_device = os.getenv('MQTT_DEVICE', 'mrpir')
        self.state_topic = f"homeassistant/binary_sensor/{self.mqtt_device}/state"
        self.mqtt_host = os.getenv('MQTT_HOST', 'localhost')
        self.mqtt_port = int(os.getenv('MQTT_PORT', '1883'))
        self.mqtt_username = os.getenv('MQTT_USERNAME', None)
        self.mqtt_password = os.getenv('MQTT_PASSWORD', None)
        self.gpio_pin = int(os.getenv('GPIO_PIN', '17'))


# Instantiate the Config class to be used throughout the application
config = Config()
