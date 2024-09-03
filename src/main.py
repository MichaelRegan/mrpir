"""
Main module for the application.
"""

import time
from config import Config
from sensor_monitor import SensorMonitor # pylint: disable=import-error
from screen_control import ScreenControl # pylint: disable=import-error
from mqtt_sensor_helper import MQTTSensorHelper # pylint: disable=import-error
from service_manager import ServiceManager # pylint: disable=import-error
import logging
from utils.logger import logger # pylint: disable=import-error
from time_events import TimeEvents # pylint: disable=import-error

logger = logging.getLogger(__name__)

def main():
    """
    Main function to initialize and start the application components.
    """
    
    logger.info("Logging is setup for info messages")
    logger.error("Logging is setup for error messages")
    logger.debug("Logging is setup for debug messages")

    service_manager = sensor_monitor = screen_control = sundown_manager = mqtt_helper = None

    try:
        config = Config()
        service_manager = ServiceManager(config)
        sensor_monitor = SensorMonitor(config.sensor)
        screen_control = ScreenControl(config.display)
        time_events = TimeEvents(config.time_events)
        mqtt_helper = MQTTSensorHelper(config.mqtt)

        service_manager.notify_startup()
        sensor_monitor.register_callback("on_motion", screen_control.on_motion)
        sensor_monitor.register_callback("on_motion", mqtt_helper.on_motion)
        sensor_monitor.register_callback("on_no_motion", screen_control.on_no_motion)
        sensor_monitor.register_callback("on_no_motion", mqtt_helper.on_no_motion)
        time_events.schedule_sundown_callback(
            screen_control.on_sundown, 
            delay_seconds=config.display.transition_time)
        
        time_events.schedule_sunup_callback(
            screen_control.on_sunup, 
            delay_seconds=0)

        sensor_monitor.start()
        time_events.start()
        screen_control.start()
        mqtt_helper.start()


        while True:
            service_manager.notify_status("Running")
            time.sleep(60)

    except KeyboardInterrupt:
        logger.info("Shutting down service due to KeyboardInterrupt")
    # except Exception as error:
    #     logger.error(f"An error occurred: {error}")
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
        if time_events:
            time_events.stop()

        logger.info("Service shut down gracefully")

if __name__ == "__main__":
    main()
