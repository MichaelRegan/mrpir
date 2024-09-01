import time
from datetime import datetime, timedelta
import asyncio

from config import config
from utils.logger import logger
from sensor_monitor import SensorMonitor
from screen_control import ScreenControl
from mqtt_helper import MQTTHelper
from service_manager import ServiceManager
from utils.time_utils import is_after_sundown


def main():
    """
    Main function to initialize and start the various service components, 
    manage their interactions, and handle graceful shutdown on exit.
    """
    service_manager = None
    sensor_monitor = None
    screen_control = None
    sundown_manager = None
    mqtt_helper = None

    last_called = datetime.now()  # Record the time of the last sensor update

    try:
        # Initialize service components
        service_manager = ServiceManager(config)
        sensor_monitor = SensorMonitor(config)
        screen_control = ScreenControl(config)
        mqtt_helper = MQTTHelper(config)

        # Notify that the service has started
        service_manager.notify_startup()

        # Register callbacks for motion detection
        sensor_monitor.register_callback("on_motion", screen_control.on_motion)
        sensor_monitor.register_callback("on_motion", mqtt_helper.on_motion)
        sensor_monitor.register_callback("on_no_motion", screen_control.on_no_motion)
        sensor_monitor.register_callback("on_no_motion", mqtt_helper.on_no_motion)

        # Start the components
        sensor_monitor.start()
        screen_control.start()
        mqtt_helper.start()

        # Default to no motion detected
        sensor_monitor.on_no_motion()

        while True:
            current_time = datetime.now()

            # Check if an hour has passed since the last update
            if current_time - last_called >= timedelta(hours=1):
                if is_after_sundown(config.time_zone):
                    logger.info("It's nighttime. Running update_sensor.")
                    sensor_monitor.update_sensor()
                    logger.info("Sleeping for 1 hour before the next update.")

                last_called = current_time  # Update the last called time
                service_manager.notify_status("Running")  # Notify that the service is running

            time.sleep(60)  # Sleep for 60 seconds before the next iteration

    except KeyboardInterrupt:
        logger.info("Shutting down service due to KeyboardInterrupt")

    finally:
        # Ensure all components are stopped and shut down gracefully
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
