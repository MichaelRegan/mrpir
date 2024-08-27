# main.py
from datetime import datetime
from gpiozero import MotionSensor
import time
import logging
from sdnotify import SystemdNotifier
from classes.mqtt_helper import MqttHelper
from classes.screen_control import ScreenControl  # Import the new ScreenControl class
from config.config import Config

def is_night_time():
    """Check if the current time is within the configured night mode hours."""
    current_hour = datetime.now().hour
    return current_hour >= Config.NIGHT_START_HOUR or current_hour < Config.NIGHT_END_HOUR

def main():
    # Setup Systemd notifier and notify that the service is starting up
    n = SystemdNotifier()
    n.notify("STATUS=Initializing motion detection service...")

    # Initialize the motion sensor on the configured GPIO pin
    pir = MotionSensor(Config.GPIO_PIN)
    
    # Initialize the screen control
    screen_control = ScreenControl()

    # Initialize MQTT
    mqtt = MqttHelper()

    n.notify("STATUS=Submitting configuration to MQTT for Home Assistant...")
    mqtt.publish_config()
    
    n.notify("Waiting for motion events...")
    while True:
        pir.wait_for_motion()
        logging.info("Motion detected.")
        mqtt.publish(Config.STATE_TOPIC, "ON")
        screen_control.brighten()
        screen_control.turn_screen_on()
        
        n.notify("WATCHDOG=1")

        while pir.motion_detected:
            time.sleep(1)
        
        time.sleep(Config.DIM_DELAY)

        logging.info("No motion detected.")
        mqtt.publish(Config.STATE_TOPIC, "OFF")
        screen_control.fade()

        # Check if it's night time and there has been no motion for the configured timeout period
        if is_night_time():
            logging.info(f"No motion detected for {Config.NO_MOTION_TIMEOUT} seconds during night hours.")
            time.sleep(Config.NO_MOTION_TIMEOUT)  # Wait for the no-motion timeout before turning off the screen
            if not pir.motion_detected:
                screen_control.turn_screen_off()

        n.notify("WATCHDOG=1")

if __name__ == "__main__":
    n = SystemdNotifier()
    n.notify("READY=1")
    
    try:
        main()
    except Exception as e:
        n.notify(f"STATUS=Service encountered an error: {e}")
        logging.error(f"Service encountered an error: {e}")
        raise
    finally:
        n.notify("STOPPING=1")
