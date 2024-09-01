import time
import pytest
import gpiozero
from dataclasses import dataclass
from unittest.mock import patch, MagicMock
from sensor_monitor import SensorMonitor # Import the SensorMonitor class


@dataclass
class SensorConfig:
    """A class to store sensor configuration settings."""
    gpio_pin: int
    no_motion_timeout: int

@patch('sensor_monitor.MotionSensor')  # Ensure this matches where MotionSensor is imported in sensor_monitor.py
def test_sensor_monitor_initialization(mock_motion_sensor):
    config = SensorConfig(
        gpio_pin=23,
        no_motion_timeout=60
    )
    
    # Mock sensor instance
    mock_sensor_instance = mock_motion_sensor.return_value
    
    # Initialize the SensorMonitor
    monitor = SensorMonitor(config)
    
    # Verify that the mock was used
    mock_motion_sensor.assert_called_once_with(23)
    assert monitor.sensor == mock_sensor_instance
    assert monitor.motion_detected is False
    assert len(monitor.callbacks["on_motion"]) == 0
    assert len(monitor.callbacks["on_no_motion"]) == 0
    
    # Ensure last_motion_time was set correctly
    assert time.time() - monitor.last_motion_time >= 60

def test_register_callbacks():
    config = SensorConfig(
        gpio_pin=23,
        no_motion_timeout=60
    )
    monitor = SensorMonitor(config)
    
    def mock_callback():
        pass
    
    monitor.register_callback("on_motion", mock_callback)
    monitor.register_callback("on_no_motion", mock_callback)
    
    assert mock_callback in monitor.callbacks["on_motion"]
    assert mock_callback in monitor.callbacks["on_no_motion"]

@patch('sensor_monitor.MotionSensor')
def test_on_motion(mock_motion_sensor):
    config = SensorConfig(
        gpio_pin=23,
        no_motion_timeout=60
    )
    
    # Create a mock sensor instance and set its is_active return value
    mock_sensor_instance = mock_motion_sensor.return_value
    mock_sensor_instance.motion_detected = True

    # Initialize the SensorMonitor
    monitor = SensorMonitor(config)
    
    # Register a mock callback
    mock_callback = MagicMock()
    monitor.register_callback("on_motion", mock_callback)
    
    # Simulate motion detection
    monitor.on_motion()
    
    # Check that the state was updated correctly
    assert monitor.motion_detected is True
    mock_callback.assert_called_once()
    assert monitor.last_motion_time <= time.time()

@patch('sensor_monitor.MotionSensor')
def test_on_no_motion(mock_motion_sensor):
    config = SensorConfig(
        gpio_pin=23,
        no_motion_timeout=60
    )
    
    # Create a mock sensor instance and set its motion_detected return value
    mock_sensor_instance = mock_motion_sensor.return_value
    mock_sensor_instance.motion_detected = False

    # Initialize the SensorMonitor
    monitor = SensorMonitor(config)
    
    # Register a mock callback
    mock_callback = MagicMock()
    monitor.register_callback("on_no_motion", mock_callback)
    
    # Simulate no motion detection
    monitor.on_no_motion()
    
    # Check that the state was updated correctly
    assert monitor.motion_detected is False
    mock_callback.assert_called_once()

@patch('sensor_monitor.MotionSensor')
def test_update_sensor(mock_motion_sensor):
    config = SensorConfig(
        gpio_pin=23,
        no_motion_timeout=60
    )
    
    # Create a mock sensor instance
    mock_sensor_instance = mock_motion_sensor.return_value
    
    # Initialize the SensorMonitor
    monitor = SensorMonitor(config)
    
    # Mock the on_motion and on_no_motion methods
    monitor.on_motion = MagicMock()
    monitor.on_no_motion = MagicMock()
    
    # Simulate motion detected
    mock_sensor_instance.motion_detected = True
    monitor.update_sensor()
    monitor.on_motion.assert_called_once()
    monitor.on_no_motion.assert_not_called()
    
    # Reset the mock
    monitor.on_motion.reset_mock()
    monitor.on_no_motion.reset_mock()
    
    # Simulate no motion detected
    mock_sensor_instance.motion_detected = False
    monitor.update_sensor()
    monitor.on_no_motion.assert_called_once()
    monitor.on_motion.assert_not_called()


