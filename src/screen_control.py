import time
import subprocess
import os
from datetime import datetime, timedelta
from utils.logger import logger
from utils.time_utils import is_after_sundown

class ScreenControl:
    def __init__(self, config):
        self.config = config
        self.current_brightness = self.current_brightness = self.get_current_brightness()
        self.last_motion_time = None  # Track the last motion detection time
        self.motion_detected = None

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
        if self.motion_detected:
            return
        
        self.motion_detected = True

        self.last_motion_time = datetime.now()
        logger.debug(f"Motion detected, setting brightness to bright level. {self.config.bright_brightness}")
        self.set_brightness(self.config.bright_brightness)

    def on_no_motion(self) -> None:
        # True if we are changing from motion detected to no motion detected
        if self.motion_detected:
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
        # esle we are already in the 'no motion' state so only check to turn off the screen at night
        else:
            if is_after_sundown(self.config.time_zone):
                if self.last_motion_time:
                    time_since_last_motion = datetime.now() - self.last_motion_time
                    logger.debug(f"Time since last motion: {time_since_last_motion}")
                    
                    if time_since_last_motion >= timedelta(seconds=self.config.screen_off_delay):
                        logger.debug(f"No motion detected for {self.config.screen_off_delay} seconds after sundown. Turning off the screen.")
                        if self.is_screen_off():
                            self.turn_off_screen()
                        
            
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

    def is_night_time(self):
        return is_after_sundown(self.config.time_zone)
    
    def turn_off_screen(self):
        try:
            logger.debug(f"Turning off the screen.")
            os.system('wlr-randr --output DSI-1 --off')
            self.current_brightness = 0
        except Exception as e:
            logger.error(f"Error turning off the screen: {e}")    

    def is_screen_off():
        try:
            result = subprocess.run(['wlr-randr'], stdout=subprocess.PIPE, text=True)
            if 'DSI-1' in result.stdout:
                for line in result.stdout.splitlines():
                    if 'DSI-1' in line and 'disabled' in line:
                        return True
            return False
        except Exception as e:
            logger.error(f"Error checking screen status: {e}")
            return False


    def start(self):
        self.current_brightness = self.get_current_brightness()
        self.set_brightness(self.config.bright_brightness)
        self.motion_detected = True
        logger.info("ScreenControl started and awaiting events.")

    def stop(self):
        logger.info("ScreenControl stopped.")
