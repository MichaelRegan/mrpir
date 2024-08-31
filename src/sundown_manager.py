import time
import threading
from utils.time_utils import is_after_sundown
from utils.logger import logger

class SundownManager:
    def __init__(self, config, screen_control):
        self.config = config
        self.screen_control = screen_control
        self._stop_event = threading.Event()

    def start(self):
        threading.Thread(target=self.manage_screen_after_sundown).start()

    def manage_screen_after_sundown(self):
        while not self._stop_event.is_set():
            if is_after_sundown(self.config.time_zone) and not self.screen_control.sensor_monitor.motion_detected:
                time_since_motion = time.time() - self.screen_control.sensor_monitor.last_motion_time
                if time_since_motion > self.config.sundown_timeout:
                    self.screen_control.set_brightness(0)
            time.sleep(60)

    def stop(self):
        self._stop_event.set()
