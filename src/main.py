import time
from config import config
from utils.logger import logger
from sensor_monitor import SensorMonitor
from screen_control import ScreenControl
from sundown_manager import SundownManager
from mqtt_helper import MQTTHelper
from service_manager import ServiceManager

def on_motion():
    logger.info("Motion detected")

def on_no_motion():
    logger.info("No motion detected")

def main():
    service_manager = sensor_monitor = screen_control = sundown_manager = mqtt_helper = None
    try:
        service_manager = ServiceManager(config)
        sensor_monitor = SensorMonitor(config, on_motion, on_no_motion)
        screen_control = ScreenControl(config, sensor_monitor)
        sundown_manager = SundownManager(config, screen_control)
        mqtt_helper = MQTTHelper(config, sensor_monitor)  # MQTTHelper is instantiated here

        service_manager.notify_startup()

        sensor_monitor.start()
        screen_control.start()
        sundown_manager.start()
        mqtt_helper.start()  # Start the MQTT client connection

        while True:
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
