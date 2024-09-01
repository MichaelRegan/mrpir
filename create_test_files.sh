#!/bin/bash

# Create the project structure
mkdir -p mrpir/src
mkdir -p mrpir/tests
mkdir -p mrpir/.github/workflows

# Create the SensorMonitor test file
cat <<EOL > mrpir/tests/test_sensor_monitor.py
import pytest
from unittest.mock import patch, MagicMock
from sensor_monitor import SensorMonitor

def test_sensor_monitor_initialization():
    config = {
        "gpio_pin": 17,
        "no_motion_timeout": 60  # 60 seconds
    }
    with patch('gpiozero.MotionSensor') as mock_sensor:
        monitor = SensorMonitor(config)
        assert monitor.sensor == mock_sensor.return_value
        assert monitor.motion_detected is False
        assert len(monitor.callbacks["on_motion"]) == 0
        assert len(monitor.callbacks["on_no_motion"]) == 0
        assert monitor.last_motion_time <= pytest.approx(time.time() - 60)

def test_register_callbacks():
    config = {
        "gpio_pin": 17,
        "no_motion_timeout": 60
    }
    monitor = SensorMonitor(config)
    
    def mock_callback():
        pass
    
    monitor.register_callback("on_motion", mock_callback)
    monitor.register_callback("on_no_motion", mock_callback)
    
    assert mock_callback in monitor.callbacks["on_motion"]
    assert mock_callback in monitor.callbacks["on_no_motion"]

def test_on_motion():
    config = {
        "gpio_pin": 17,
        "no_motion_timeout": 60
    }
    monitor = SensorMonitor(config)
    
    mock_callback = MagicMock()
    monitor.register_callback("on_motion", mock_callback)
    
    with patch.object(monitor.sensor, 'motion_detected', True):
        monitor.on_motion()
        
        assert monitor.motion_detected is True
        mock_callback.assert_called_once()
        assert monitor.last_motion_time <= time.time()

def test_on_no_motion():
    config = {
        "gpio_pin": 17,
        "no_motion_timeout": 60
    }
    monitor = SensorMonitor(config)
    
    mock_callback = MagicMock()
    monitor.register_callback("on_no_motion", mock_callback)
    
    with patch.object(monitor.sensor, 'motion_detected', False):
        monitor.on_no_motion()
        
        assert monitor.motion_detected is False
        mock_callback.assert_called_once()

def test_update_sensor():
    config = {
        "gpio_pin": 17,
        "no_motion_timeout": 60
    }
    monitor = SensorMonitor(config)
    
    with patch.object(monitor.sensor, 'motion_detected', True):
        monitor.on_motion = MagicMock()
        monitor.on_no_motion = MagicMock()
        
        monitor.update_sensor()
        
        monitor.on_motion.assert_called_once()
        monitor.on_no_motion.assert_not_called()
    
    with patch.object(monitor.sensor, 'motion_detected', False):
        monitor.on_motion = MagicMock()
        monitor.on_no_motion = MagicMock()
        
        monitor.update_sensor()
        
        monitor.on_no_motion.assert_called_once()
        monitor.on_motion.assert_not_called()

def test_initialization_error_handling():
    config = {
        "gpio_pin": 17,
        "no_motion_timeout": 60
    }
    with patch('gpiozero.MotionSensor', side_effect=gpiozero.GPIOZeroError("Initialization failed")):
        with pytest.raises(gpiozero.GPIOZeroError):
            SensorMonitor(config)

def test_start_stop_monitoring():
    config = {
        "gpio_pin": 17,
        "no_motion_timeout": 60
    }
    with patch('gpiozero.MotionSensor') as mock_sensor:
        monitor = SensorMonitor(config)
        
        monitor.start()
        assert monitor.sensor.when_motion == monitor.on_motion
        assert monitor.sensor.when_no_motion == monitor.on_no_motion
        
        monitor.stop()
        mock_sensor.return_value.close.assert_called_once()
EOL

# Create the GitHub Actions workflow file
cat <<EOL > mrpir/.github/workflows/test.yml
name: Run tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10]

    steps:
    - uses: actions/checkout@v2
    - name: Set up Python \${{ matrix.python-version }}
      uses: actions/setup-python@v2
      with:
        python-version: \${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pytest pytest-cov freezegun
    - name: Run tests
      run: |
        pytest --cov=src --cov-report=term-missing
    - name: Upload coverage report
      uses: actions/upload-artifact@v2
      with:
        name: coverage-report
        path: coverage.xml
EOL


# Print success message
echo "Test files and GitHub Actions workflow created successfully!"
