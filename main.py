"""Main module for the motion detection and screen control service."""

import time
import logging
from datetime import datetime
from gpiozero import MotionSensor  # pylint: disable=import-error
from sdnotify import SystemdNotifier  # pylint: disable=import-error
from classes.mqtt_helper import MqttHelper
from classes.screen_control import ScreenControl
from config.config import Config  # pylint: disable=import-error


def is_night_time():
    """Check if the current time is within the configured night mode hours."""
    current_hour = datetime.now().hour
    return current_hour >= Config.NIGHT_START_HOUR or current_hour < Config.NIGHT_END_HOUR


def main():
    """Main function to handle motion detection and screen control."""
    # Setup Systemd notifier and notify that the service is starting up
    notifier.notify("STATUS=Initializing motion detection service...") # pylint: disable=used-before-assignment

    # Initialize the motion sensor on the configured GPIO pin
    pir = MotionSensor(Config.GPIO_PIN)

    # Initialize the screen control
    screen_control = ScreenControl()

    # Initialize MQTT
    mqtt = MqttHelper()

    notifier.notify("STATUS=Submitting configuration to MQTT for Home Assistant...")
    mqtt.publish_config()

    notifier.notify("STATUS=Waiting for motion events...")
    while True:
        pir.wait_for_motion()
        logging.info("Motion detected.")
        mqtt.publish(Config.STATE_TOPIC, "ON")
        screen_control.brighten()
        screen_control.turn_screen_on()

        notifier.notify("WATCHDOG=1")

        while pir.motion_detected:
            time.sleep(1)

        time.sleep(Config.NO_MOTION_DELAY)

        logging.info("No motion detected.")
        mqtt.publish(Config.STATE_TOPIC, "OFF")
        screen_control.fade()

        # Check if it's night time and there has been no motion for the configured timeout period
        if is_night_time():
            logging.info(
                "No motion detected for %d seconds during night hours.",
                Config.NO_MOTION_TIMEOUT,
            )
            time.sleep(Config.NO_MOTION_TIMEOUT)  # Wait for the no-motion timeout
            if not pir.motion_detected:
                screen_control.turn_screen_off()

        notifier.notify("WATCHDOG=1")


if __name__ == "__main__":
    notifier = SystemdNotifier()
    notifier.notify("READY=1")

    try:
        main()
    except Exception as e:
        notifier.notify(f"STATUS=Service encountered an error: {e}")
        logging.error("Service encountered an error: %s", e)
        raise
    finally:
        notifier.notify("STOPPING=1")
