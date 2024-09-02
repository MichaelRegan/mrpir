"""
Screen Control module for managing screen brightness and state.
"""
import time
import subprocess
from datetime import datetime, timedelta
import logging
from utils.logger import logger # pylint: disable=import-error
from time_events import TimeEvents # pylint: disable=import-error

logger = logging.getLogger(__name__)

class ScreenControl:
    """
    Controls the screen brightness and power state based on motion detection
    and time of day, with the ability to turn off the screen after sundown if no
    motion is detected.

    Attributes:
        config (dict): Configuration settings for screen control.
        current_brightness (int): The current brightness level of the screen.
        last_motion_time (datetime): The last time motion was detected.
        motion_detected (bool): Tracks whether motion has been detected.
    """

    def __init__(self, config):
        """
        Initializes the ScreenControl with the given configuration.

        Args:
            config (dict): Configuration settings for the screen control.
        """
        self.config = config
        self.current_brightness = self.get_current_brightness()
        self.last_motion_time = None  # Track the last motion detection time
        self.motion_detected = None
        self.on_sundown = None
        self.on_sunup = None
        self.night_time = False

    def get_current_brightness(self):
        """
        Retrieves the current brightness level from the system.

        Returns:
            int: The current brightness level.
        """
        try:
            with open(self.config.brightness_path, 'r', encoding='utf-8') as file:
                brightness = int(file.read().strip())
                logger.debug("Current brightness read from %s: %d",
                             self.config.brightness_path, brightness)
                return brightness
        except FileNotFoundError as err:
            logger.error(f"Brightness file not found: {err}")
            return self.config.bright_brightness  # Default to bright brightness if reading fails
        except ValueError as err:
            logger.error(f"Error parsing brightness value: {err}")
            return self.config.bright_brightness  # Default to bright brightness if reading fails

    def on_motion(self) -> None:
        """
        Handles the event when motion is detected.
        Sets the screen brightness to the bright level.
        """
        self.motion_detected = True
        self.last_motion_time = datetime.now()
        logger.debug("Motion detected, setting brightness to bright level: %d",
                     self.config.bright_brightness)
        self.smooth_transition(self.current_brightness, self.config.bright_brightness, self.config.transition_time)

    def on_no_motion(self) -> None:
        """
        Handles the event when no motion is detected.
        Dims the screen and turns it off after sundown 
        """

        if self.night_time == False:
            logger.debug("on_no_motion: Night time == false.dim_brightness: {self.config.dim_brightness}")
            self.set_brightness(self.config.dim_brightness)
        else:
            if not self.is_screen_off():
                self.turn_off_screen()
                logger.debug("on_no_motion: Screen turned off after sundown.")

    def on_sundown(self) -> None:
        """
        Handles the event when the sun goes down.        
        """
        self.night_time = True
        if (self.motion_detected == False):
            self.turn_off_screen()
            logger.debug("on_sundown: Screen turned off after sundown.")

    def on_sunup(self) -> None:
        """
        Handles the event when the sun comes up.
        """
        self.night_time = False
        # if (self.motion_detected == False):
        #     self.set_brightness(self.config.dim_brightness)

    def set_brightness(self, value: int) -> None:
        """
        Sets the screen brightness to the specified value.

        Args:
            value (int): The brightness level to set.
        """
        # logger.debug("Setting screen brightness to %d from %d", self.current_brightness, value)
        try:
            if value != self.current_brightness:
                with open(self.config.brightness_path, 'w', encoding='utf-8') as file:
                    file.write(str(value))
                self.current_brightness = value
                # logger.debug("Screen brightness set to %d", value)
        except OSError as err:
            logger.error(f"Error setting brightness: {err}")

    def smooth_transition(self, start, end, duration):
        """Smoothly transition the screen brightness."""
        steps = 50  # Number of steps in the transition
        step_delay = duration / steps  # Time between each step
        brightness_range = end - start

        for i in range(steps + 1):
            current_brightness = start + (brightness_range * i // steps)
            self.set_brightness(current_brightness)
            time.sleep(step_delay)

    def turn_off_screen(self) -> None:
        """
        Turns off the screen using the system command.
        """
        try:
            logger.debug("Turning off the screen.")
            subprocess.run(['wlr-randr', '--output', 'DSI-1', '--off'], check=True)
            self.current_brightness = 0
        except subprocess.CalledProcessError as err:
            logger.error(f"Error turning off the screen: {err}")

    def is_screen_off(self) -> bool:
        """
        Checks if the screen is currently off by querying the system.

        Returns:
            bool: True if the screen is off, False otherwise.
        """
        try:
            logger.debug("Checking screen status.")
            result = subprocess.run(['wlr-randr'], stdout=subprocess.PIPE, text=True, check=True)
            if 'DSI-1' in result.stdout:
                for line in result.stdout.splitlines():
                    if 'DSI-1' in line and 'disabled' in line:
                        logger.info("Screen is off.")
                        return True
            logger.debug("Screen is on.")
            return False
        except subprocess.CalledProcessError as err:
            logger.error(f"Error checking screen status: {err}")
            return False

    def start(self) -> None:
        """
        Initializes the screen control, setting the brightness to bright and waiting for events.
        """
        self.current_brightness = self.get_current_brightness()
        self.set_brightness(self.config.bright_brightness)
        self.motion_detected = True
        logger.info("ScreenControl started and awaiting events.")

    def stop(self) -> None:
        """
        Stops the screen control, logging the stop event.
        """
        logger.info("ScreenControl stopped.")
