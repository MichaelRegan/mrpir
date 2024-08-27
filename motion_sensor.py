import RPi.GPIO as GPIO
import time
import threading

class MotionSensor:
    def __init__(self, pin, callback, timeout):
        self.pin = pin
        self.callback = callback
        self.timeout = timeout
        self.last_motion_time = None
        self.stop_event = threading.Event()
        self.motion_detected = False  # State-tracking variable

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN)

    def monitor(self):
        while not self.stop_event.is_set():
            current_state = GPIO.input(self.pin)
            
            if current_state == GPIO.HIGH:
                self.last_motion_time = time.time()
                if not self.motion_detected:
                    # Motion detected
                    self.motion_detected = True
                    self.callback(True)
            
            elif self.motion_detected and self.has_timed_out():
                # No motion detected after timeout
                self.motion_detected = False
                self.callback(False)
            
            time.sleep(1)

    def has_timed_out(self):
        if self.last_motion_time is None:
            return False
        return time.time() - self.last_motion_time >= self.timeout

    def get_current_state(self):
        """Returns the current state of the motion sensor (True for motion, False for no motion)."""
        return GPIO.input(self.pin) == GPIO.HIGH

    def stop(self):
        self.stop_event.set()
