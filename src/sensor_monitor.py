"""
Module: SensorMonitor
Description: This module monitors a motion sensor using the gpiozero library and triggers
             registered callbacks for motion and no-motion events. It provides an interface
             for registering callbacks, starting and stopping the sensor, and manually
             updating the sensor state.
"""

from typing import Callable, Dict, List
import threading
import time
import gpiozero # pylint: disable=import-error
from gpiozero import MotionSensor # pylint: disable=import-error
from utils.logger import logger  # pylint: disable=import-error


class SensorMonitor:
    """
    Monitors a motion sensor and triggers registered callbacks for motion and no-motion events.

    Attributes:
        config (dict): Configuration settings for the sensor monitor.
        callbacks (Dict[str, List[Callable]]): A dictionary of callback lists for motion events.
        motion_detected (bool): Tracks whether motion is currently detected.
        last_motion_time (float): The timestamp of the last detected motion.
        _stop_event (threading.Event): Event to signal the sensor monitor to stop.
        sensor (MotionSensor): The motion sensor instance from gpiozero.
    """

    def __init__(self, config):
        """
        Initializes the SensorMonitor with the provided configuration.

        Args:
            config (dict): Configuration settings for the sensor monitor.
        """
        self.callbacks: Dict[str, List[Callable]] = {
            "on_motion": [],
            "on_no_motion": []
        }
        self.config = config
        self.motion_detected = False
        self.last_motion_time = time.time() - self.config.no_motion_timeout
        self._stop_event = threading.Event()

        try:
            # Initialize the MotionSensor using gpiozero
            self.sensor = MotionSensor(self.config.gpio_pin)
        except gpiozero.GPIOZeroError as e:
            logger.error(f"Error initializing MotionSensor: {e}")
            raise

    def register_callback(self, key: str, callback: Callable) -> None:
        """
        Registers a callback function for the specified event.

        Args:
            key (str): The event key ('on_motion' or 'on_no_motion').
            callback (Callable): The function to call when the event occurs.
        """
        if key in self.callbacks:
            self.callbacks[key].append(callback)
        else:
            self.callbacks[key] = [callback]

    def start(self) -> None:
        """
        Starts the sensor monitoring by linking sensor events to the appropriate callbacks.
        """
        try:
            logger.debug("SensorMonitor started and awaiting events.")
            self.sensor.when_motion = self.on_motion
            self.sensor.when_no_motion = self.on_no_motion
        except gpiozero.GPIOZeroError as e:
            logger.error(f"GPIOZero error in start: {e}")

    def on_motion(self) -> None:
        """
        Handles the motion detected event and triggers the 'on_motion' callbacks.
        """
        try:
            self.motion_detected = True
            self.last_motion_time = time.time()
            logger.debug("MotionSensor: Motion detected")
            if "on_motion" in self.callbacks:
                for callback in self.callbacks["on_motion"]:
                    callback()
        except Exception as e:
            logger.error(f"Unexpected error in on_motion: {e}")

    def on_no_motion(self) -> None:
        """
        Handles the no motion detected event and triggers the 'on_no_motion' callbacks.
        """
        try:
            logger.debug("MotionSensor: No motion detected")
            if not self.sensor.motion_detected:
                self.motion_detected = False
            if "on_no_motion" in self.callbacks:
                for callback in self.callbacks["on_no_motion"]:
                    callback()
        except Exception as e:
            logger.error(f"Unexpected error in on_no_motion: {e}")

    def update_sensor(self) -> None:
        """
        Manually updates the sensor state, triggering the appropriate 
        callbacks based on the current state.
        """
        try:
            if self.sensor.motion_detected:
                self.on_motion()
            else:
                self.on_no_motion()
        except gpiozero.GPIOZeroError as e:
            logger.error(f"GPIOZero error in update_sensor: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in update_sensor: {e}")

    def stop(self) -> None:
        """
        Stops the sensor monitoring and releases any resources held by the sensor.
        """
        try:
            self._stop_event.set()
            self.sensor.close()
            logger.debug("SensorMonitor stopped.")
        except gpiozero.GPIOZeroError as e:
            logger.error(f"GPIOZero error in stop: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in stop: {e}")
