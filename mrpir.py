"""
This is a Python script to monitor a PIR sensor and publish the state to MQTT.
"""

import os
import subprocess
import sys
import signal
import logging
import logging.config
import sdnotify # pylint: disable=import-error
from decouple import UndefinedValueError, config # pylint: disable=import-error
# import logging.config # pylint: disable=import-error
import paho.mqtt.client as mqtt # pylint: disable=import-error
import yaml
from gpiozero import MotionSensor # pylint: disable=import-error

class PIRService:
    """ Class to monitor a PIR sensor and publish the state to MQTT. """

    # Private variables
    _systemd_notify = sdnotify.SystemdNotifier() # Send notifications for SystemD

    # Log information and errors based on setting in logging.yml file
    _logger = logging.getLogger(__name__)
    _mqtt_client = None # MQTT client for publishing metion events
    _mqtt_connection_error = False # MQTT connection error flag

    shutdown_requested = False # Shutdown requested flag

    def __init__(self):
        """ Constructor """
        signal.signal(signal.SIGINT, self.request_shutdown)
        signal.signal(signal.SIGTERM, self.request_shutdown)
        self.notify("Status=Setting up logging")

        # Setup logging
        with open(os.path.abspath(os.path.dirname(__file__)) + \
                  '/logging.yml', 'r', encoding='UTF-8') as file_steam:
            logger_config = yaml.safe_load(file_steam.read())
            logging.config.dictConfig(logger_config)

        PIRService._logger = logging.getLogger('mrpir')
        self.notify("Status=Reading .env variables")

        # Read in reuited settings from local .env file
        try:
            # Get required settings from local .env file
            mqtt_user_name = config('MQTT_USER_NAME') # User name to log into the MQTT broker
            mqtt_password = config('MQTT_PASSWORD') # Password for the MQTT broker
            mqtt_device = config('MQTT_DEVICE') # Device name for the MQTT broker
            mqtt_client_id = config ("MQTT_CLIENT_ID") # Client ID for the MQTT broker
            mqtt_broker = config ("MQTT_BROKER") # IP address or FQDN to the MQTT broker

            # Create the config topic for Home Assistant
            self.config_topic = "homeassistant/binary_sensor/" + \
                mqtt_device + "/config"

            # Create the config payload for Home Assistant
            self.config_payload = '{"name": "' + mqtt_device + '_motion' + '", \
                    "device_class": "motion", \
                    "unique_id": "' + mqtt_client_id + '_' + mqtt_device + '_id' + '", \
                    "state_topic": "homeassistant/binary_sensor/' + mqtt_device + '/state"}'

            # Create the state topic for Home Assistant
            self.topic = 'homeassistant/binary_sensor/' + mqtt_device + '/state'

        except UndefinedValueError as err:
            sys.exit(err)

       # Get optional setting from local .env file
        mqtt_port = config ("MQTT_PORT", default=1883, cast=int) # Port for the MQTT broker
        pir_pin = config ("PIR_PIN", default=23) # GPIO pin for the PIR sensor

        # Logging level debug=10, info=20, warning=30, error=40, critical=50. input is 1-5
        logging_level = config ("LOGGING_LEVEL", default=1, cast=int) * 10

        # Support for XScreenSaver
        self.xscreensaver_support = config ("XSCREENSAVER_SUPPORT", default=False, cast=bool)
        PIRService._logger.setLevel(logging_level) # Set the logging level for PIR
        # Log the logging level
        PIRService._logger.info(str(PIRService._logger.getEffectiveLevel))

        # Notify systemd that we are setting up MQTT
        self.notify("Status=Setting up MQTT Client")

        # Create the MQTT client
        PIRService._mqtt_client = mqtt.Client(mqtt_client_id, \
                clean_session=True, userdata=None, protocol=mqtt.MQTTv311, transport="tcp")
        PIRService._mqtt_client.enable_logger(PIRService._logger) # Enable logging for MQTT

        # Setup MQTT callbacks
        PIRService._mqtt_client.on_connect = self.on_connect
        PIRService._mqtt_client.on_disconnect = self.on_disconnect
        PIRService._mqtt_client.on_log = self.on_log

        # Set the MQTT user name and password
        PIRService._mqtt_client.username_pw_set(mqtt_user_name, mqtt_password)
        self.is_mqtt_connected = False # MQTT connection flag

        # Connect to the MQTT broker and start the background thread
        PIRService._mqtt_client.connect(mqtt_broker, mqtt_port, keepalive=45)
        PIRService._mqtt_client.loop_start() # Start the MQTT background thread

        self.notify("Status=Setting up PIR connection")
        self.pir = MotionSensor(pir_pin) # Setup the PIR sensor

        # Setup the PIR motion callbacks
        self.pir.when_motion = self.on_motion
        self.pir.when_no_motion = self.on_no_motion

        # Finally, notify systemd that we are ready
        self.notify("READY=1")

    def on_connect(self, client, userdata, flags, result_code): # pylint: disable=unused-argument
        """ Handle connection to MQTT broker """
        # 0: Connection successful
        # 1: Connection refused - incorrect protocol version
        # 2: Connection refused - invalid client identifier
        # 3: Connection refused - server unavailable
        # 4: Connection refused - bad username or password
        # 5: Connection refused - not authorised
        # 7: duplicate client id - personal testing found this
        # 6-255: Currently unused.
        if result_code == 0:
            self.is_mqtt_connected = True # MQTT connection flag
            self._logger.info("Connected to MQTT broker") # Log MQTT connection

            # Publish the config payload to Home Assistant. This support auto discovery
            self._mqtt_client.publish(self.config_topic, self.config_payload, retain=True)
        else:
            # Log MQTT connection error
            self._logger.error("Failed to connect to MQTT broker with error code %s", result_code)

    def on_disconnect(self, client, userdata, result_code): # pylint: disable=unused-argument
        """ Handle disconnection from MQTT broker """
        if result_code != 0:
            self._logger.warning("Unexpected disconnection from MQTT broker")
            self.is_mqtt_connected = False

    def on_log(self, client, userdata, level, buf): # pylint: disable=unused-argument
        """ Log MQTT messages """
        self._logger.debug("MQTT log: %s", buf)

    def notify(self, message):
        """ Notify systemd of status """
        PIRService._systemd_notify.notify(message)

    def __del__(self):
        """ Destructor """

        # Stop a background thread to process MQTT messages
        PIRService._mqtt_client.loop_stop()

    def can_run(self):
        """ can run for SIGINT """
        return not self.shutdown_requested

    def request_shutdown(self, *args): # pylint: disable=unused-argument
        """ request shutdown for SIGINT """
        print('Request to shutdown received, stopping')
        self.shutdown_requested = True
        self.notify("STOPPING=1")

    def on_motion(self):
        """ Take action when PIR senses motion """
        PIRService._logger.info("Motion detected")
        PIRService._mqtt_client.publish(self.topic, "ON", retain=False)
        try:
            if self.xscreensaver_support: # Turn off screen saver if configured
                PIRService._logger.debug("Turn off screen saver")

                # Turn off screen saver
                completed_process = subprocess.run(["/usr/bin/xscreensaver-command", "-display",  \
                    ":0.0", "-deactivate"], \
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
                if completed_process.returncode:
                    # Log error
                    PIRService._logger.error("Xscreensaver error: %s", completed_process.returncode)

            # Log motion detected
            PIRService._logger.debug("Motion Detected")

        except Exception as on_motion_err: # pylint: disable=broad-except
            PIRService._logger.error(str(on_motion_err))


    def on_no_motion(self):
        """ Take action when PIR senses no motion """
        PIRService._logger.info("No motion detected")
        PIRService._mqtt_client.publish(self.topic, "OFF", retain=True)

    def run(self):
        """ Run the PIR main loop """

        while self.can_run():
            # mqtt is working on a background thread, so we just wait for motion
            self.pir.wait_for_motion(timeout=5)
            self.notify("WATCHDOG=1") # Notify systemd that we are still running

        # Stop the PIR sensor
        self.pir.close()




# main loop
if __name__ == '__main__':
    PIRServiceController = PIRService() # Create the PIR service

    try:
        PIRServiceController.run() # Run the PIR service as a blocking call
    
    except KeyboardInterrupt:
        PIRServiceController.request_shutdown()

    finally:
        PIRServiceController.notify("STOPPING=1") # Notify systemd that we are stopping
        sys.exit(0)
