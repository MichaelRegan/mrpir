from gpiozero import MotionSensor
import threading
import time
from utils.logger import logger

class SensorMonitor:
    # def __init__(self, config, on_motion, on_no_motion):
    #     self.config = config
    #     self.on_motion = on_motion
    #     self.on_no_motion = on_no_motion
    #     self.motion_detected = False
    #     self.last_motion_time = time.time() - self.config.no_motion_timeout
    #     self._stop_event = threading.Event()

    #     # Initialize the MotionSensor using gpiozero
    #     self.sensor = MotionSensor(config.gpio_pin)

    def __init__(self, config):
        self.callbacks = {
            "on_motion": [],
            "on_no_motion": []
        }
        self.config = config
        self.on_no_motion = None
        self.motion_detected = False
        self.last_motion_time = time.time() - self.config.no_motion_timeout
        self._stop_event = threading.Event()

        # Initialize the MotionSensor using gpiozero
        self.sensor = MotionSensor(config.gpio_pin)

    def register_callback(self, key, callback):
        if key in self.callbacks:
            self.callbacks[key].append(callback)
        else:
            self.callbacks[key] = [callback]

    def start(self):
        try:
            # Link motion detected and no motion detected events to callbacks
            logger.debug("SensorMonitor started and awaiting events.")
            self.sensor.when_motion = self.handle_motion
            self.sensor.when_no_motion = self.handle_no_motion
        except Exception as e:
            logger.error(f"Error in start: {e}")

    def handle_motion(self):
        try:
            self.motion_detected = True
            self.last_motion_time = time.time()
            logger.debug("MotionSensor: Motion detected")
            if "on_motion" in self.callbacks:
                for callback in self.callbacks["on_motion"]:
                    callback()
        except Exception as e:
            logger.error(f"Error in handle_motion: {e}")
    
    def handle_no_motion(self):
        try:
            logger.debug("MotionSensor: No motion detected")
            time.sleep(self.config.no_motion_timeout) # why not use self.config.no_motion_timeout test?
            logger.debug("MotionSensor: if not self.sensor.motion_detected")
            if not self.sensor.motion_detected:
                self.motion_detected = False
            logger.debug("MotionSensor: if on_no_motion in self.callbacks")
            if "on_no_motion" in self.callbacks:
                for callback in self.callbacks["on_no_motion"]:
                    logger.debug("MotionSensor: callback()")
                    callback()
        except Exception as e:
            logger.error(f"Error in handle_no_motion: {e}")

    def stop(self):
        self._stop_event.set()
        self.sensor.close()
