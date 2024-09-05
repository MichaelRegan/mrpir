import os
from unittest import TestCase
from unittest.mock import patch
from src.config import Config, MQTTConfig, DisplayConfig, TimeoutConfig, SensorConfig, TimeEventsConfig

class TestConfig(TestCase):

    @patch.dict(os.environ, {}, clear=True)
    @patch('src.config.load_dotenv', return_value=None)  # Mock load_dotenv to prevent loading .env variables
    def test_default_initialization(self, mock_load_dotenv):
        config = Config()
        
        # Test DisplayConfig defaults
        self.assertEqual(config.display.brightness_path, '/sys/class/backlight/10-0045/brightness')
        self.assertEqual(config.display.dim_brightness, 0)
        self.assertEqual(config.display.bright_brightness, 90)
        self.assertEqual(config.display.transition_time, 2)
        self.assertEqual(config.display.timezone, 'America/Los_Angeles')
        
        # Test TimeoutConfig defaults
        self.assertEqual(config.timeouts.sundown_timeout, 3600)
        
        # Test MQTTConfig defaults
        self.assertEqual(config.mqtt.device, None)
        self.assertEqual(config.mqtt.client_id, None)
        self.assertEqual(config.mqtt.state_topic, None)
        self.assertEqual(config.mqtt.host, None)
        self.assertEqual(config.mqtt.port, None)
        self.assertEqual(config.mqtt.username, '')
        self.assertEqual(config.mqtt.password, '')
        self.assertEqual(config.mqtt.config_topic, None)
        self.assertFalse(config.mqtt.supported, False)
        self.assertIn(config.mqtt.config_payload, None)
        
        # Test SensorConfig defaults
        self.assertEqual(config.sensor.gpio_pin, 23)
        self.assertEqual(config.sensor.no_motion_delay, 60)
        
        # Test TimeEventsConfig defaults
        self.assertEqual(config.time_events.location_name, 'New York')
        self.assertEqual(config.time_events.region, 'USA')
        self.assertEqual(config.time_events.latitude, 40.7128)
        self.assertEqual(config.time_events.longitude, -74.0060)

    @patch.dict(os.environ, {
        'BRIGHTNESS_PATH': '/custom/path',
        'DIM_BRIGHTNESS': '10',
        'BRIGHT_BRIGHTNESS': '100',
        'TRANSITION_TIME': '5',
        'timezone': 'Europe/London',
        'SUNDOWN_TIMEOUT': '7200',
        'MQTT_DEVICE': 'custom_device',
        'MQTT_CLIENT_ID': 'custom_client_id',
        'MQTT_HOST': 'custom_host',
        'MQTT_PORT': '8883',
        'MQTT_USERNAME': 'user',
        'MQTT_PASSWORD': 'pass',
        'GPIO_PIN': '24',
        'NO_MOTION_DELAY': '120',
        'LOCATION_NAME': 'Los Angeles',
        'REGION': 'California',
        'LATITUDE': '34.0522',
        'LONGITUDE': '-118.2437'
    }, clear=True)
    def test_environment_initialization(self):
        config = Config()
        
        # Test DisplayConfig from environment
        self.assertEqual(config.display.brightness_path, '/custom/path')
        self.assertEqual(config.display.dim_brightness, 10)
        self.assertEqual(config.display.bright_brightness, 100)
        self.assertEqual(config.display.transition_time, 5)
        self.assertEqual(config.display.timezone, 'Europe/London')
        
        # Test TimeoutConfig from environment
        self.assertEqual(config.timeouts.sundown_timeout, 7200)
        
        # Test MQTTConfig from environment
        self.assertEqual(config.mqtt.device, 'custom_device')
        self.assertEqual(config.mqtt.client_id, 'custom_client_id')
        self.assertEqual(config.mqtt.state_topic, 'homeassistant/binary_sensor/custom_device/state')
        self.assertEqual(config.mqtt.host, 'custom_host')
        self.assertEqual(config.mqtt.port, 8883)
        self.assertEqual(config.mqtt.username, 'user')
        self.assertEqual(config.mqtt.password, 'pass')
        self.assertEqual(config.mqtt.config_topic, 'homeassistant/binary_sensor/custom_device/config')
        self.assertTrue(config.mqtt.supported)
        self.assertIn('custom_device_motion', config.mqtt.config_payload)
        
        # Test SensorConfig from environment
        self.assertEqual(config.sensor.gpio_pin, 24)
        self.assertEqual(config.sensor.no_motion_delay, 120)
        
        # Test TimeEventsConfig from environment
        self.assertEqual(config.time_events.location_name, 'Los Angeles')
        self.assertEqual(config.time_events.region, 'California')
        self.assertEqual(config.time_events.latitude, 34.0522)
        self.assertEqual(config.time_events.longitude, -118.2437)