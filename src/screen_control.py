import os
import time
import threading
from utils.logger import logger

class ScreenControl:
    def __init__(self, config, sensor_monitor):
        self.config = config
        self.sensor_monitor = sensor_monitor
        self.current_brightness = self.config.bright_brightness
        self._stop_event = threading.Event()

    def start(self):
        threading.Thread(target=self.control_brightness).start()

    def control_brightness(self):
        while not self._stop_event.is_set():
            if self.sensor_monitor.motion_detected:
                self.set_brightness(self.config.bright_brightness)
            else:
                time_since_motion = time.time() - self.sensor_monitor.last_motion_time
                if time_since_motion > self.config.dim_delay:
                    self.set_brightness(self.config.dim_brightness)
            time.sleep(0.5)

    def set_brightness(self, value):
        try:
            if value != self.current_brightness:
                with open(self.config.brightness_path, 'w') as f:
                    f.write(str(value))
                self.current_brightness = value
                logger.info(f"Set screen brightness to {value}")
        except Exception as e:
            logger.error(f"Error setting brightness: {e}")

    def stop(self):
        self._stop_event.set()
