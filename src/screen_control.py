import time
import os
from utils.logger import logger

class ScreenControl:
    def __init__(self, config):
        self.config = config
        self.current_brightness = self.current_brightness = self.get_current_brightness()

    def get_current_brightness(self):
        try:
            with open(self.config.brightness_path, 'r') as f:
                brightness = int(f.read().strip())
                logger.debug(f"Current brightness read from {self.config.brightness_path}: {brightness}")
                return brightness
        except Exception as e:
            logger.error(f"Error reading current brightness: {e}")
            return self.config.bright_brightness  # Default to bright brightness if reading fails

    def on_motion(self) -> None:
        logger.debug(f"Motion detected, setting brightness to bright level. {self.config.bright_brightness}")
        self.set_brightness(self.config.bright_brightness)

    def on_no_motion(self) -> None:
        self.set_brightness(self.config.dim_brightness)

    def set_brightness(self, value):
        logger.debug(f"In Set screen brightness to {value} from {self.current_brightness}")
        try:
            if value != self.current_brightness:
                with open(self.config.brightness_path, 'w') as f:
                    f.write(str(value))
                self.current_brightness = value
                logger.debug(f"Set screen brightness to {value}")
        except Exception as e:
            logger.error(f"Error setting brightness: {e}")

    def start(self):
        self.current_brightness = self.get_current_brightness()
        self.set_brightness(self.config.bright_brightness)
        logger.info("ScreenControl started and awaiting events.")

    def stop(self):
        logger.info("ScreenControl stopped.")
