# Python script for the Python Demo Service
import os
import subprocess
import sys
import time
import signal # pylint: disable=import-error
import sdnotify # pylint: disable=import-error
import logging # pylint: disable=import-error
import logging.config # pylint: disable=import-error
from decouple import UndefinedValueError, config # pylint: disable=import-error
# import logging.config # pylint: disable=import-error
import paho.mqtt.client as mqtt # pylint: disable=import-error
import yaml # pylint: disable=import-error
from gpiozero import MotionSensor # pylint: disable=import-error

class Pirservice:

    # Private variables
    _systemd_notify = sdnotify.SystemdNotifier()
    _logger = logging.getLogger(__name__)
    _mqtt_client = None

    _mqtt_connection_error = False
    _mqtt_connection_error_rc = 0
    shutdown_requested = False
    
    def __init__(self):
        signal.signal(signal.SIGINT, self.request_shutdown)
        signal.signal(signal.SIGTERM, self.request_shutdown)
        # _logger = logging.getLogger(__name__)
        
        # time.sleep(1)
        # Tell systemd that our service is ready
        # Pirservice._systemd_notify = sdnotify.SystemdNotifier()

        Pirservice._systemd_notify.notify("Status=Setting up logging")
        # Setup logging
        with open(os.path.abspath(os.path.dirname(__file__)) + '/logging.yml', 'r', encoding='UTF-8') as f:
            logger_config = yaml.safe_load(f.read())
            logging.config.dictConfig(logger_config)
        
        Pirservice._logger = logging.getLogger('mrpir')

        Pirservice._systemd_notify.notify("Status=Reading .env variables")
        # Read in reuited settings from local .env file
        try:
            # Get required settings from local .env file
            self.MQTT_USER = config('MQTT_USER_NAME')
            self.MQTT_PASSWORD = config('MQTT_PASSWORD')
            self.MQTT_DEVICE = config('MQTT_DEVICE')
            self.MQTT_CLIENT_ID = config ("MQTT_CLIENT_ID")
            self.MQTT_BROKER = config ("MQTT_BROKER")
            self.CONFIG_TOPIC = "homeassistant/binary_sensor/" + self.MQTT_DEVICE + "/config"
            self.CONFIG_PAYLOAD = '{"name": "' + self.MQTT_DEVICE + '_motion' + '", \
                            "device_class": "motion", \
                            "unique_id": "' + self.MQTT_CLIENT_ID + '_' + self.MQTT_DEVICE + '_id' + '", \
                            "state_topic": "homeassistant/binary_sensor/' + self.MQTT_DEVICE + '/state"}'
            self.TOPIC = 'homeassistant/binary_sensor/' + self.MQTT_DEVICE + '/state'

        except UndefinedValueError as err:
            sys.exit(0)

       # Get optional setting from local .env file
        self.MQTT_PORT = config ("MQTT_PORT", default=1883, cast=int)
        self.PIR_PIN = config ("PIR_PIN", default=23)
        self.LOGGING_LEVEL = config ("LOGGING_LEVEL", default=1, cast=int) * 10
        Pirservice._logger.setLevel(self.LOGGING_LEVEL)
        Pirservice._logger.info(str(Pirservice._logger.getEffectiveLevel))

        # Setup MQTT
        Pirservice._systemd_notify.notify("Status=Setting up MQTT Client")
        Pirservice._mqtt_client = mqtt.Client(self.MQTT_CLIENT_ID, clean_session=True, userdata=None, protocol=mqtt.MQTTv311, transport="tcp")
        Pirservice._mqtt_client.enable_logger(Pirservice._logger)
        Pirservice._mqtt_client.on_connect = self.on_connect
        Pirservice._mqtt_client.on_disconnect = self.on_disconnect
        Pirservice._mqtt_client.on_log = self.on_log
        Pirservice._mqtt_client.username_pw_set(self.MQTT_USER, self.MQTT_PASSWORD)
        self.is_mqtt_connected = False

        # Connect to the MQTT broker and start the background thread
        Pirservice._mqtt_client.connect(self.MQTT_BROKER, self.MQTT_PORT, keepalive=45)
        Pirservice._mqtt_client.loop_start()


        Pirservice._systemd_notify.notify("Status=Setting up PIR connection")
        self.pir = MotionSensor(self.PIR_PIN)
        pirservice.pir.when_motion = self.on_motion
        pirservice.pir.when_no_motion = self.on_no_motion

        # Finally, notify systemd
        Pirservice._systemd_notify.notify("READY=1")

    def on_connect(self, client, userdata, flags, rc):
        # 0: Connection successful 
        # 1: Connection refused - incorrect protocol version 
        # 2: Connection refused - invalid client identifier 
        # 3: Connection refused - server unavailable 
        # 4: Connection refused - bad username or password 
        # 5: Connection refused - not authorised 
        # 7: duplicate client id - personal testing found this
        # 6-255: Currently unused.
        if rc == 0:
            self.is_mqtt_connected = True     
            self._logger.info("Connected to MQTT broker")
            # self._mqtt_client.subscribe(self.TOPIC)
            self._mqtt_client.publish(self.CONFIG_TOPIC, self.CONFIG_PAYLOAD, retain=True)
        else:
            self._logger.error("Failed to connect to MQTT broker with error code %s", rc)

    def on_disconnect(self, client, userdata, rc): # pylint: disable=unused-argument
        if rc != 0:
            self._logger.warning("Unexpected disconnection from MQTT broker")
            self.is_mqtt_connected = False

    def on_log(self, client, userdata, level, buf): # pylint: disable=unused-argument # pylint: disable=invalid-name 
        self._logger.debug("MQTT log: %s", buf)

    def __del__(self):
        # Pirservice.pir.close()
        self.pir.close()

        # Start a background thread to process MQTT messages
        Pirservice._mqtt_client.loop_stop()


    def can_run(self):
        """ can run for SIGINT """
        return not self.shutdown_requested
    
    def request_shutdown(self, *args):
        """ request shutdown for SIGINT """
        print('Request to shutdown received, stopping')
        # self.pir.close()
        self.shutdown_requested = True
        Pirservice._systemd_notify.notify("STOPPING=1")

    def on_motion(self):
        """ Take action when PIR senses motion """
        Pirservice._logger.info("Motion detected")
        # pirservice.connect_mqtt()
        Pirservice._mqtt_client.publish(pirservice.TOPIC, "ON", retain=False)
        try:
            # if myclient.xscreensaver_support:
                # logger.debug("Turn off screen saver")
            completed_process = subprocess.run(["/usr/bin/xscreensaver-command", "-display",  \
                    ":0.0", "-deactivate"], \
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
                # if completed_process.returncode:
                #     logger.error("Xscreensaver error: %s", completed_process.returncode)

    #        os.system("/usr/bin/xscreensaver-command -display " + '":0.0"' + \
    #        " -deactivate >> /home/pi/xscreensaver.log")
            Pirservice._logger.debug("Motion Detected")

        except Exception as on_motion_err: # pylint: disable=broad-except
            Pirservice._logger.error(str(on_motion_err))


    def on_no_motion(self):
        Pirservice._logger.info("No motion detected")
        Pirservice._mqtt_client.publish(pirservice.TOPIC, "OFF", retain=True)

if __name__ == '__main__':
    pirservice = Pirservice()
    Pirservice._systemd_notify.notify("Status=entering main loop")

    try:
        # pirservice.pir.when_motion = pirservice.on_motion
        # pirservice.pir.when_no_motion = pirservice.on_no_motion

        while pirservice.can_run():
            # mqtt is working on a background thread, so we just wait for motion
            pirservice.pir.wait_for_motion(timeout=5)
            Pirservice._systemd_notify.notify("WATCHDOG=1")

    finally:
        pirservice.pir.close()