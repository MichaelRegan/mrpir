from typing import Callable, Dict, List
import threading
import time
from datetime import datetime, timedelta
import gpiozero  # pylint: disable=import-error
from gpiozero import MotionSensor  # pylint: disable=import-error
from utils.logger import logger  # pylint: disable=import-error


class SensorMonitor:
    """
    Monitors a motion sensor and triggers registered callbacks for motion and no-motion events.

    Attributes:
        config (dict): Configuration settings for the sensor monitor.
        callbacks (Dict[str, List[Callable]]): A dictionary of callback lists for motion events.
        motion_detected (bool): Tracks whether motion is currently detected.
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
        
        # set the last motion time far enough back to trigger the first no_motion event
        # self.last_motion_time = time.time() - self.config.no_motion_delay
        self._stop_event = threading.Event()

        try:
            # Initialize the MotionSensor using gpiozero
            self.sensor = MotionSensor(self.config.gpio_pin)
        except gpiozero.GPIOZeroError as err:
            logger.error(f"Error initializing MotionSensor: {err}")
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
        except gpiozero.GPIOZeroError as err:
            logger.error(f"GPIOZero error in start: {err}")

    def on_motion(self) -> None:
        """
        Handles the motion detected event and triggers the 'on_motion' callbacks.
        """
        self.motion_detected = True
        # self.last_motion_time = time.time()
        logger.debug("MotionSensor: Motion detected")
        if "on_motion" in self.callbacks:
            for callback in self.callbacks["on_motion"]:
                callback()

    def on_no_motion(self) -> None:
        """
        Handles the no motion detected event with a delay before triggering the 'on_no_motion' callbacks.
        """
        def delayed_no_motion():
            current_time = datetime.now()
            target_time = current_time + timedelta(seconds=self.config.no_motion_delay)

            start_time = time.time()
            logger.debug(f"Current time: {current_time.strftime('%H:%M:%S')} | Target time: {target_time.strftime('%H:%M:%S')} | offset: {self.config.no_motion_delay} seconds")

            # Wait for the no_motion_delay period
            time.sleep(self.config.no_motion_delay)

            # Ensure no new motion was detected during the delay
            if not self.sensor.motion_detected:
                self.motion_detected = False
                end_time = time.time()
                logger.info(f"MotionSensor: No motion detected (after delay). Total delay: {end_time - start_time} seconds")
                if "on_no_motion" in self.callbacks:
                    for callback in self.callbacks["on_no_motion"]:
                        callback()

        # Start a thread to handle the delay
        threading.Thread(target=delayed_no_motion).start()

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
        except gpiozero.GPIOZeroError as err:
            logger.error(f"GPIOZero error in update_sensor: {err}")

    def stop(self) -> None:
        """
        Stops the sensor monitoring and releases any resources held by the sensor.
        """
        try:
            self._stop_event.set()
            self.sensor.close()
            logger.debug("SensorMonitor stopped.")
        except gpiozero.GPIOZeroError as err:
            logger.error(f"GPIOZero error in stop: {err}")
