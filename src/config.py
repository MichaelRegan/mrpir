import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()
        self.brightness_path = os.getenv('BRIGHTNESS_PATH', '/sys/class/backlight/10-0045/brightness')
        self.dim_brightness = int(os.getenv('DIM_BRIGHTNESS', '0'))
        self.bright_brightness = int(os.getenv('BRIGHT_BRIGHTNESS', '90'))
        self.transition_time = int(os.getenv('TRANSITION_TIME', '30'))
        self.dim_delay = int(os.getenv('DIM_DELAY', '30'))
        self.no_motion_timeout = int(os.getenv('NO_MOTION_TIMEOUT', '60'))
        self.sundown_timeout = int(os.getenv('SUNDOWN_TIMEOUT', '3600'))
        self.mqtt_device = os.getenv('MQTT_DEVICE', 'mrpir')
        self.state_topic = f"homeassistant/binary_sensor/{self.mqtt_device}/state"
        self.mqtt_host = os.getenv('MQTT_HOST', 'localhost')
        self.mqtt_port = int(os.getenv('MQTT_PORT', '1883'))
        self.mqtt_username = os.getenv('MQTT_USERNAME', None)  # Ensure these attributes are initialized
        self.mqtt_password = os.getenv('MQTT_PASSWORD', None)
        self.gpio_pin = int(os.getenv('GPIO_PIN', '17'))

config = Config()
