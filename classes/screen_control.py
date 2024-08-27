import os
import time
from subprocess import run
import logging
from config.config import Config

class ScreenControl:
    def __init__(self, brightness_path="/sys/class/backlight/10-0045/brightness", 
                 dim_brightness=Config.DIM_BRIGHTNESS, 
                 bright_brightness=Config.BRIGHT_BRIGHTNESS,
                 transition_time=Config.TRANSITION_TIME):
        self.brightness_path = brightness_path
        self.dim_brightness = dim_brightness
        self.bright_brightness = bright_brightness
        self.transition_time = transition_time

    def set_brightness(self, level):
        """Set the screen brightness to a specific level."""
        try:
            with open(self.brightness_path, 'w') as brightness_file:
                brightness_file.write(str(level))
            logging.info(f"Brightness set to {level}")
        except Exception as e:
            logging.error(f"Error setting brightness: {e}")

    def smooth_transition(self, start, end, duration):
        """Smoothly transition the screen brightness from start to end over the specified duration."""
        steps = 50  # Number of steps in the transition
        step_delay = duration / steps  # Time between each step
        brightness_range = end - start

        for i in range(steps + 1):
            current_brightness = start + (brightness_range * i // steps)
            self.set_brightness(current_brightness)
            time.sleep(step_delay)
    
    def fade(self):
            self.smooth_transition(self.bright_brightness, self.dim_brightness, self.transition_time)

    def brighten(self):
            self.smooth_transition(self.dim_brightness, self.bright_brightness, self.transition_time)

    def turn_screen_on(self):
        """Turn the screen on using a shell command."""
        try:
            os.system('wlr-randr --output DSI-1 --on')
            logging.info("Screen turned on")
        except Exception as e:
            logging.error(f"Error turning screen on: {e}")

    def turn_screen_off(self):
        """Turn the screen off using a shell command."""
        try:
            os.system('wlr-randr --output DSI-1 --off')
            logging.info("Screen turned off")
        except Exception as e:
            logging.error(f"Error turning screen off: {e}")
