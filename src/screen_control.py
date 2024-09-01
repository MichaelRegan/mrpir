import time
import subprocess
import os
from datetime import datetime, timedelta
from utils.logger import logger
from utils.time_utils import is_after_sundown


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

    def get_current_brightness(self):
        """
        Retrieves the current brightness level from the system.

        Returns:
            int: The current brightness level.
        """
        try:
            with open(self.config.brightness_path, 'r') as f:
                brightness = int(f.read().strip())
                logger.debug(f"Current brightness read from {self.config.brightness_path}: {brightness}")
                return brightness
        except Exception as e:
            logger.error(f"Error reading current brightness: {e}")
            return self.config.bright_brightness  # Default to bright brightness if reading fails

    def on_motion(self) -> None:
        """
        Handles the event when motion is detected.
        Sets the screen brightness to the bright level.
        """
        if self.motion_detected:
            return  # If motion is already detected, do nothing

        self.motion_detected = True
        self.last_motion_time = datetime.now()
        logger.debug(f"Motion detected, setting brightness to bright level: {self.config.bright_brightness}")
        self.set_brightness(self.config.bright_brightness)

    def on_no_motion(self) -> None:
        """
        Handles the event when no motion is detected.
        Dims the screen and may turn it off after sundown if no motion is detected for a specified duration.
        """
        if self.motion_detected:
            # Transitioning from motion detected to no motion detected
            self.motion_detected = False
            self.set_brightness(self.config.dim_brightness)

            if is_after_sundown(self.config.time_zone):
                if self.last_motion_time:
                    time_since_last_motion = datetime.now() - self.last_motion_time
                    logger.debug(f"Time since last motion: {time_since_last_motion}")

                    if time_since_last_motion >= timedelta(seconds=self.config.screen_off_delay):
                        logger.debug(f"No motion detected for {self.config.screen_off_delay} seconds after sundown. Turning off the screen.")
                        self.turn_off_screen()
                else:
                    logger.debug(f"No motion has been detected yet.")
        else:
            # Already in 'no motion' state, check if the screen should be turned off at night
            if is_after_sundown(self.config.time_zone):
                if self.last_motion_time:
                    time_since_last_motion = datetime.now() - self.last_motion_time
                    logger.debug(f"Time since last motion: {time_since_last_motion}")

                    if time_since_last_motion >= timedelta(seconds=self.config.screen_off_delay):
                        logger.debug(f"No motion detected for {self.config.screen_off_delay} seconds after sundown. Turning off the screen.")
                        if not self.is_screen_off():
                            self.turn_off_screen()

    def set_brightness(self, value: int) -> None:
        """
        Sets the screen brightness to the specified value.

        Args:
            value (int): The brightness level to set.
        """
        logger.debug(f"Setting screen brightness to {value} from {self.current_brightness}")
        try:
            if value != self.current_brightness:
                with open(self.config.brightness_path, 'w') as f:
                    f.write(str(value))
                self.current_brightness = value
                logger.debug(f"Screen brightness set to {value}")
        except Exception as e:
            logger.error(f"Error setting brightness: {e}")

    def is_night_time(self) -> bool:
        """
        Determines if it is currently nighttime based on the configured time zone.

        Returns:
            bool: True if it is after sundown, False otherwise.
        """
        return is_after_sundown(self.config.time_zone)

    def turn_off_screen(self) -> None:
        """
        Turns off the screen using the system command.
        """
        try:
            logger.info("Turning off the screen.")
            os.system('wlr-randr --output DSI-1 --off')
            self.current_brightness = 0
        except Exception as e:
            logger.error(f"Error turning off the screen: {e}")

    def is_screen_off(self) -> bool:
        """
        Checks if the screen is currently off by querying the system.

        Returns:
            bool: True if the screen is off, False otherwise.
        """
        try:
            logger.info("Checking screen status.")
            result = subprocess.run(['wlr-randr'], stdout=subprocess.PIPE, text=True)
            if 'DSI-1' in result.stdout:
                for line in result.stdout.splitlines():
                    if 'DSI-1' in line and 'disabled' in line:
                        logger.info("Screen is off.")
                        return True
            logger.info("Screen is on.")
            return False
        except Exception as e:
            logger.error(f"Error checking screen status: {e}")
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
