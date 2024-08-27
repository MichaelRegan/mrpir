"""Screen control class to handle dimming and turning off/on."""

import os
import time
import logging
from subprocess import run
from config.config import Config

class ScreenControl:
    """Class to control screen brightness and power state."""

    def __init__(self, brightness_path=Config.BRIGHTNESS_PATH,
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
            with open(self.brightness_path, 'w', encoding='utf-8') as brightness_file:
                brightness_file.write(str(level))
            logging.info("Brightness set to %d", level)
        except (OSError, ValueError) as e:
            logging.error("Error setting brightness: %s", e)

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
        """Fade the screen brightness to a dim level."""
        self.smooth_transition(self.bright_brightness, self.dim_brightness, self.transition_time)

    def brighten(self):
        """Brighten the screen brightness to the bright level."""
        self.smooth_transition(self.dim_brightness, self.bright_brightness, self.transition_time)

    def turn_screen_on(self):
        """Turn the screen on using a shell command."""
        try:
            run('wlr-randr --output DSI-1 --on', check=True, shell=True)
            logging.info("Screen turned on")
        except (OSError, ValueError) as e:
            logging.error("Error turning screen on: %s", e)

    def turn_screen_off(self):
        """Turn the screen off using a shell command."""
        try:
            run('wlr-randr --output DSI-1 --off', check=True, shell=True)
            logging.info("Screen turned off")
        except (OSError, ValueError) as e:
            logging.error("Error turning screen off: %s", e)
