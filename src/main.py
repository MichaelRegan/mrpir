"""
Main module for the application.
"""

import time
from config import Config
from sensor_monitor import SensorMonitor  # pylint: disable=import-error
from screen_control import ScreenControl  # pylint: disable=import-error
from mqtt_sensor_helper import MQTTSensorHelper  # pylint: disable=import-error
from service_manager import ServiceManager  # pylint: disable=import-error
from base_component import BaseComponent  # pylint: disable=import-error
from time_events import TimeEvents  # pylint: disable=import-error

class MainApplication(BaseComponent):
    def __init__(self):
        super().__init__(__name__)
        self.config = Config()
        self.service_manager = None
        self.sensor_monitor = None
        self.screen_control = None
        self.time_events = None
        self.mqtt_helper = None

    def initialize(self):
        self.log_info("Starting the mrpir application")

        self.service_manager = ServiceManager(self.config)
        self.sensor_monitor = SensorMonitor(self.config.sensor)
        self.screen_control = ScreenControl(self.config.display)
        self.time_events = TimeEvents(self.config.time_events)

        if self.config.mqtt.supported:
            self.mqtt_helper = MQTTSensorHelper(self.config.mqtt)
            self.sensor_monitor.register_callback("on_motion", self.mqtt_helper.on_motion)
            self.sensor_monitor.register_callback("on_no_motion", self.mqtt_helper.on_no_motion)

        self.sensor_monitor.register_callback("on_motion", self.screen_control.on_motion)
        self.sensor_monitor.register_callback("on_motion", self.mqtt_helper.on_motion)
        self.sensor_monitor.register_callback("on_no_motion", self.screen_control.on_no_motion)
        self.sensor_monitor.register_callback("on_no_motion", self.mqtt_helper.on_no_motion)

        self.time_events.schedule_sundown_callback(
            self.screen_control.on_sundown,
            delay_seconds=self.config.display.transition_time
        )

        self.time_events.schedule_sunup_callback(
            self.screen_control.on_sunup,
            delay_seconds=0
        )

        self.sensor_monitor.start()
        self.time_events.start()
        self.screen_control.start()

        if self.config.mqtt.supported:
            self.mqtt_helper.start()

        self.time_events._schedule_test_event(
            event='sundown',
            callback=self.screen_control.on_sundown,
            delay_seconds=10
        )

        self.log_info("Initialization complete")
        self.service_manager.notify_startup()

    def run(self):
        try:
            while True:
                self.service_manager.notify_status("Running")
                time.sleep(900)

        except KeyboardInterrupt as exception:
            self.handle_exception(exception)
        except Exception as error:
            self.handle_exception(error)
        finally:
            self.shutdown()

    def shutdown(self):
        self.service_manager.notify_stopping()
        self.log_info("Shutting down the application...")
        if self.sensor_monitor:
            self.sensor_monitor.stop()
        if self.screen_control:
            self.screen_control.stop()
        if self.time_events:
            self.time_events.stop()
        if self.mqtt_helper:
            self.mqtt_helper.stop()
        if self.service_manager:
            self.service_manager.notify_shutdown()

        self.log_info("Service shut down gracefully")


def main():
    app = MainApplication()
    app.initialize()
    app.run()


if __name__ == "__main__":
    main()
