import time
import os
from utils.logger import logger

# In Set screen brightness to /sys/class/backlight/10-0045/brightness from 0
# Error setting brightness: [Errno 22] Invalid argument

class ScreenControl:
    def __init__(self, config, sensor_monitor):
        self.config = config
        self.sensor_monitor = sensor_monitor
        self.current_brightness = self.config.bright_brightness

    def handle_motion(self):
        logger.debug(f"Motion detected, setting brightness to bright level. {self.config.bright_brightness}")
        self.set_brightness(self.config.bright_brightness)

    def handle_no_motion(self):
        logger.debug(f"No motion detected, will dim the screen after {self.config.dim_delay} seconds.")
        # Delay the dimming to respect the configured dim delay
        time.sleep(self.config.dim_delay)
        # Double-check that motion hasn't been detected again during the delay
        if not self.sensor_monitor.motion_detected:
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
        self.current_brightness = 0
        self.set_brightness(self.config.bright_brightness)
        logger.info("ScreenControl started and awaiting events.")

    def stop(self):
        logger.info("ScreenControl stopped.")
