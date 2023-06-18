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

class Pirservice:
    """ Class to monitor a PIR sensor and publish the state to MQTT. """
    # pylint: disable=too-many-instance-attributes

    # Private variables
    _systemd_notify = sdnotify.SystemdNotifier()
    _logger = logging.getLogger(__name__)
    _mqtt_client = None

    _mqtt_connection_error = False
    # _mqtt_connection_error_rc = 0
    shutdown_requested = False

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

        Pirservice._logger = logging.getLogger('mrpir')
        self.notify("Status=Reading .env variables")

        # Read in reuited settings from local .env file
        try:
            # Get required settings from local .env file
            self.mqtt_server = config('MQTT_USER_NAME')
            self.mqtt_password = config('MQTT_PASSWORD')
            self.mqtt_device = config('MQTT_DEVICE')
            self.mqtt_client_id = config ("MQTT_CLIENT_ID")
            self.mqtt_broker = config ("MQTT_BROKER")
            self.config_topic = "homeassistant/binary_sensor/" + \
                self.mqtt_device + "/config"
            self.config_payload = '{"name": "' + self.mqtt_device + '_motion' + '", \
                    "device_class": "motion", \
                    "unique_id": "' + self.mqtt_client_id + '_' + self.mqtt_device + '_id' + '", \
                    "state_topic": "homeassistant/binary_sensor/' + self.mqtt_device + '/state"}'
            self.topic = 'homeassistant/binary_sensor/' + self.mqtt_device + '/state'

        except UndefinedValueError as err:
            sys.exit(err.message)

       # Get optional setting from local .env file
        self.mqtt_port = config ("MQTT_PORT", default=1883, cast=int)
        self.pir_pin = config ("PIR_PIN", default=23)
        self.logging_level = config ("LOGGING_LEVEL", default=1, cast=int) * 10
        self.xscreensaver_support = config ("XSCREENSAVER_SUPPORT", default=False, cast=bool)
        Pirservice._logger.setLevel(self.logging_level)
        Pirservice._logger.info(str(Pirservice._logger.getEffectiveLevel))

        # Setup MQTT
        self.notify("Status=Setting up MQTT Client")
        Pirservice._mqtt_client = mqtt.Client(self.mqtt_client_id, \
                clean_session=True, userdata=None, protocol=mqtt.MQTTv311, transport="tcp")
        Pirservice._mqtt_client.enable_logger(Pirservice._logger)
        Pirservice._mqtt_client.on_connect = self.on_connect
        Pirservice._mqtt_client.on_disconnect = self.on_disconnect
        Pirservice._mqtt_client.on_log = self.on_log
        Pirservice._mqtt_client.username_pw_set(self.mqtt_server, self.mqtt_password)
        self.is_mqtt_connected = False

        # Connect to the MQTT broker and start the background thread
        Pirservice._mqtt_client.connect(self.mqtt_broker, self.mqtt_port, keepalive=45)
        Pirservice._mqtt_client.loop_start()

        self.notify("Status=Setting up PIR connection")
        self.pir = MotionSensor(self.pir_pin)
        self.pir.when_motion = self.on_motion
        self.pir.when_no_motion = self.on_no_motion

        # Finally, notify systemd
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
            self.is_mqtt_connected = True
            self._logger.info("Connected to MQTT broker")
            # self._mqtt_client.subscribe(self.TOPIC)
            self._mqtt_client.publish(self.config_topic, self.config_payload, retain=True)
        else:
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
        Pirservice._systemd_notify.notify(message)

    def __del__(self):
        """ Destructor """
        self.pir.close()

        # Start a background thread to process MQTT messages
        Pirservice._mqtt_client.loop_stop()

    def can_run(self):
        """ can run for SIGINT """
        return not self.shutdown_requested

    def request_shutdown(self, *args):
        """ request shutdown for SIGINT """
        print('Request to shutdown received, stopping')
        self.shutdown_requested = True
        self.notify("STOPPING=1")

    def on_motion(self):
        """ Take action when PIR senses motion """
        Pirservice._logger.info("Motion detected")
        Pirservice._mqtt_client.publish(pirservice.topic, "ON", retain=False)
        try:
            if self.xscreensaver_support:
                Pirservice._logger.debug("Turn off screen saver")
                completed_process = subprocess.run(["/usr/bin/xscreensaver-command", "-display",  \
                    ":0.0", "-deactivate"], \
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
                if completed_process.returncode:
                    Pirservice._logger.error("Xscreensaver error: %s", completed_process.returncode)

            Pirservice._logger.debug("Motion Detected")

        except Exception as on_motion_err: # pylint: disable=broad-except
            Pirservice._logger.error(str(on_motion_err))


    def on_no_motion(self):
        """ Take action when PIR senses no motion """
        Pirservice._logger.info("No motion detected")
        Pirservice._mqtt_client.publish(pirservice.topic, "OFF", retain=True)

# main loop
if __name__ == '__main__':
    """ main loop """
    pirservice = Pirservice()
    pirservice.notify("Status=entering main loop")

    try:
        while pirservice.can_run():

            # mqtt is working on a background thread, so we just wait for motion
            pirservice.pir.wait_for_motion(timeout=5)
            pirservice.notify("WATCHDOG=1")

    finally:
        pirservice.pir.close()
        pirservice.notify("STOPPING=1")
        sys.exit(0)
