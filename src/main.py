"""
Main module for the application.
"""

import time
from datetime import datetime, timedelta
from config import Config
from sensor_monitor import SensorMonitor # pylint: disable=import-error
from screen_control import ScreenControl # pylint: disable=import-error
from mqtt_helper import MQTTHelper # pylint: disable=import-error
from service_manager import ServiceManager # pylint: disable=import-error
from utils.logger import logger  # pylint: disable=import-error
from utils.time_utils import is_after_sundown # pylint: disable=import-error

def main():
    """
    Main function to initialize and start the application components.
    """

    service_manager = sensor_monitor = screen_control = sundown_manager = mqtt_helper = None
    last_called = datetime.now()
    try:
        config = Config()
        service_manager = ServiceManager(config)
        sensor_monitor = SensorMonitor(config.sensor)
        screen_control = ScreenControl(config.display)
        mqtt_helper = MQTTHelper(config.mqtt)

        service_manager.notify_startup()

        sensor_monitor.register_callback("on_motion", screen_control.on_motion)
        sensor_monitor.register_callback("on_motion", mqtt_helper.on_motion)
        sensor_monitor.register_callback("on_no_motion", screen_control.on_no_motion)
        sensor_monitor.register_callback("on_no_motion", mqtt_helper.on_no_motion)

        sensor_monitor.start()
        screen_control.start()
        mqtt_helper.start()

        # Default to no motion detected
        # sensor_monitor.on_no_motion()

        while True:
            current_time = datetime.now()

            # Check if an hour has passed since the last call
            if current_time - last_called >= timedelta(hours=1):
                if is_after_sundown(config.time_zone):
                    logger.info("It's nighttime. Running update_sensor.")
                    sensor_monitor.update_sensor()
                    logger.info("Sleeping for 1 hour before the next update.")
                last_called = current_time  # Update the last called time

                service_manager.notify_status("Running")
            time.sleep(60)

    except KeyboardInterrupt:
        logger.info("Shutting down service due to KeyboardInterrupt")
    finally:
        if sensor_monitor:
            sensor_monitor.stop()
        if screen_control:
            screen_control.stop()
        if sundown_manager:
            sundown_manager.stop()
        if mqtt_helper:
            mqtt_helper.stop()
        if service_manager:
            service_manager.notify_shutdown()

        logger.info("Service shut down gracefully")

if __name__ == "__main__":
    main()
