"""
Screen Control module for managing screen brightness and state.
"""
import time
import subprocess
from datetime import datetime
from base_component import BaseComponent

class ScreenControl(BaseComponent):
    def __init__(self, config):
        super().__init__(__name__)
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
                self.log_debug(f"Current brightness read from {self.config.brightness_path}:{brightness}")
                return brightness
        except FileNotFoundError as err:
            self.log_error(f"Brightness file not found: {err}")
            return self.config.bright_brightness  # Default to bright brightness if reading fails
        except ValueError as err:
            self.log_error(f"Error parsing brightness value: {err}")
            return self.config.bright_brightness  # Default to bright brightness if reading fails

    def on_motion(self) -> None:
        """
        Handles the event when motion is detected.
        Sets the screen brightness to the bright level.
        """
        self.motion_detected = True
        self.last_motion_time = datetime.now()
        self.log_debug(f"Motion detected, setting brightness to bright level: {self.config.bright_brightness}")
        self.smooth_transition(self.current_brightness, self.config.bright_brightness, self.config.transition_time)

    def on_no_motion(self) -> None:
        """
        Handles the event when no motion is detected.
        Dims the screen and turns it off after sundown 
        """

        if not self.night_time:
            self.log_debug("on_no_motion: Night time == false.dim_brightness: {self.config.dim_brightness}")
            # self.set_brightness(self.config.dim_brightness)
            self.smooth_transition(self.current_brightness, self.config.dim_brightness, self.config.transition_time)
        else:
            if not self.is_screen_off():
                self.turn_off_screen()
                self.log_debug("on_no_motion: Screen turned off after sundown.")

    def on_sundown(self) -> None:
        """
        Handles the event when the sun goes down.        
        """
        self.night_time = True
        if  not self.motion_detected:
            self.turn_off_screen()
            self.log_debug("on_sundown: Screen turned off after sundown.")

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
        try:
            if value != self.current_brightness:
                with open(self.config.brightness_path, 'w', encoding='utf-8') as file:
                    file.write(str(value))
                self.current_brightness = value
        except OSError as err:
            self.log_error(f"Error setting brightness: {err}")

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
            self.log_debug("Turning off the screen.")
            subprocess.run(['wlr-randr', '--output', 'DSI-1', '--off'], check=True)
            self.current_brightness = 0
        except subprocess.CalledProcessError as err:
            self.log_error(f"Error turning off the screen: {err}")

    def is_screen_off(self) -> bool:
        """
        Checks if the screen is currently off by querying the system.

        Returns:
            bool: True if the screen is off, False otherwise.
        """
        try:
            self.log_debug("Checking screen status.")
            result = subprocess.run(['wlr-randr'], stdout=subprocess.PIPE, text=True, check=True)
            if 'DSI-1' in result.stdout:
                for line in result.stdout.splitlines():
                    if 'DSI-1' in line and 'disabled' in line:
                        self.log_info("Screen is off.")
                        return True
            self.log_debug("Screen is on.")
            return False
        except subprocess.CalledProcessError as err:
            self.log_error(f"Error checking screen status: {err}")
            return False

    def start(self) -> None:
        """
        Initializes the screen control, setting the brightness to bright and waiting for events.
        """
        if self.is_screen_off():
            self.current_brightness = 0
            self.motion_detected = False
        else:
            brightness = self.get_current_brightness()
            if self.get_current_brightness() == self.config.dim_brightness:
                self.motion_detected = False
            else:
                self.current_brightness = self.get_current_brightness()
                self.set_brightness(self.config.bright_brightness)
                self.motion_detected = True

        self.log_info("ScreenControl started and awaiting events.")

    def stop(self) -> None:
        """
        Stops the screen control, logging the stop event.
        """
        self.log_info("ScreenControl stopped.")
