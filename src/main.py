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
    service_manager = sensor_monitor = screen_control = sundown_manager = mqtt_helper = None
    last_called = datetime.now() 
    try:
        service_manager = ServiceManager(config)
        sensor_monitor = SensorMonitor(config) #, on_motion, on_no_motion)
        screen_control = ScreenControl(config)
        mqtt_helper = MQTTHelper(config)  # MQTTHelper is instantiated here

        service_manager.notify_startup()

        sensor_monitor.register_callback("on_motion", screen_control.on_motion)
        sensor_monitor.register_callback("on_motion", mqtt_helper.on_motion)
        sensor_monitor.register_callback("on_no_motion", screen_control.on_no_motion)
        sensor_monitor.register_callback("on_no_motion", mqtt_helper.on_no_motion)

        sensor_monitor.start()
        screen_control.start()
        # sundown_manager.start()
        mqtt_helper.start()  # Start the MQTT client connection

        # Default to no motion detected
        sensor_monitor.on_no_motion()

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
