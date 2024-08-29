from gpiozero import MotionSensor
import threading
import time
from utils.logger import logger

class SensorMonitor:
    def __init__(self, config, on_motion, on_no_motion):
        self.config = config
        self.on_motion = on_motion
        self.on_no_motion = on_no_motion
        self.motion_detected = False
        # Initialize last_motion_time to current time minus no_motion_timeout to ensure the first motion is detected
        self.last_motion_time = time.time() - self.config.no_motion_timeout
        self._stop_event = threading.Event()

        # Initialize the MotionSensor using gpiozero
        self.sensor = MotionSensor(config.gpio_pin)

    def start(self):
        # Link motion detected and no motion detected events to callbacks
        self.sensor.when_motion = self.handle_motion
        self.sensor.when_no_motion = self.handle_no_motion
        # threading.Thread(target=self.monitor_sensor).start()

    def handle_motion(self):
        self.motion_detected = True
        self.last_motion_time = time.time()  # Update last_motion_time on motion detection
        logger.info("Motion detected")
        self.on_motion()

    def handle_no_motion(self):
        logger.info("No motion detected")
        time.sleep(self.config.no_motion_timeout)  # Ensure the no motion timeout is respected
        if not self.sensor.motion_detected:  # Double-check if motion has reoccurred
            self.motion_detected = False
            self.on_no_motion()

    # def monitor_sensor(self):
    #     while not self._stop_event.is_set():
    #         time.sleep(0.1)  # Just to keep the thread alive

    def stop(self):
        self._stop_event.set()
        self.sensor.close()
