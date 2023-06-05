""" This file reads pir signals and posts them to MQTT """
import os # pylint: disable=import-error
import sys # pylint: disable=import-error
import time # pylint: disable=import-error
import systemd.daemon # pylint: disable=import-error
import subprocess # pylint: disable=import-error
import logging # pylint: disable=import-error
# import sdnotify # pylint: disable=import-error
import logging.config # pylint: disable=import-error
import signal # pylint: disable=import-error
from decouple import UndefinedValueError, config # pylint: disable=import-error
import yaml # pylint: disable=import-error
from gpiozero import MotionSensor # pylint: disable=import-error
import paho.mqtt.client as mqtt # pylint: disable=import-error

# Setup the logger
with open(os.path.abspath(os.path.dirname(__file__)) + '/logging.yml', 'r', encoding='UTF-8') as f:
    logger_config = yaml.safe_load(f.read())
    logging.config.dictConfig(logger_config)

logger = logging.getLogger('mrpir')

try:
    # Get required settings from local .env file
    MQTT_USER = config('MQTT_USER_NAME')
    MQTT_PASSWORD = config('MQTT_PASSWORD')
    MQTT_DEVICE = config('MQTT_DEVICE')
    MQTT_CLIENT_ID = config ("MQTT_CLIENT_ID")
    MQTT_BROKER = config ("MQTT_BROKER")
    CONFIG_TOPIC = "homeassistant/binary_sensor/" + MQTT_DEVICE + "/config"
    CONFIG_PAYLOAD = '{"name": "' + MQTT_DEVICE + '_motion' + '", \
                    "device_class": "motion", \
                    "unique_id": "' + MQTT_CLIENT_ID + '_' + MQTT_DEVICE + '_id' + '", \
                    "state_topic": "homeassistant/binary_sensor/' + MQTT_DEVICE + '/state"}'
    TOPIC = 'homeassistant/binary_sensor/' + MQTT_DEVICE + '/state'

except UndefinedValueError as err:
    logger.exception("Error reading settings from .env file")
    sys.exit(0)

# Get optional setting from local .env file
try:
    XSCREENSAVER_SUPPORT = config ("XSCREENSAVER_SUPPORT", cast=bool)

except UndefinedValueError as err:
    logger.warning('Warning: XSCREENSAVER_SUPPORT was not provided, using defaul value of False')
    XSCREENSAVER_SUPPORT = False

except IOError as err:
    logger.exception("Error reading XSCREENSAVER_SUPPORT, using defaul value of False")
    XSCREENSAVER_SUPPORT = False

# Get optional setting from local .env file
try:
    MQTT_PORT = config ("MQTT_PORT", cast=int)

except UndefinedValueError as err:
    logger.warning('Warning: MQTT_PORT was not provided, using defaul value of 1883')
    MQTT_PORT = 1883

except IOError as err:
    logger.exception("Error reading MQTT_PORT, using defaul value of 1883")
    MQTT_PORT = 1883

# Get optional setting from local .env file
try:
    PIR_PIN = config ("PIR_PIN")

except UndefinedValueError as err:
    logger.warning('Error getting PIR_PIN from .env file, using defaul value of 23')
    PIR_PIN = 23

except IOError as err:
    logger.exception('Error getting PIR_PIN from .env file, using defaul value of 23')
    PIR_PIN = 23

# Get optional setting from local .env file ***** Need to update this block *******
try:
    LOGGING_LEVEL = config ("LOGGING_LEVEL", cast=int) * 10
    logger.setLevel(LOGGING_LEVEL)

except UndefinedValueError as err:
    logger.exception('Error getting LOGGING_LEVEL from .env file, \
                     using defaul value of WARNING log level')
    LOGGING_LEVEL = 10
    logger.setLevel(LOGGING_LEVEL)

logger.info(str(logger.getEffectiveLevel))

class pirservice:
    """ Signal handler for SIGINT """
    shutodwn_requested = False
    mqtt_connected = False
    # mqtt_client = None
    # notify = None
    pir = None
    
    def __init__(self):
        signal.signal(signal.SIGINT, self.request_shutdown)
        signal.signal(signal.SIGTERM, self.request_shutdown)
        # self.notify = sdnotify.SystemdNotifier()
        # pirservice.mqtt_client = self.connect_mqtt()
        # pirservice.mqtt_client.on_connect = self.on_connect
        # pirservice.mqtt_client.on_disconnect = self.on_disconnect
        # pirservice.mqtt_client.on_log = self.on_log
        # pirservice.mqtt_client.client_id = MQTT_CLIENT_ID
        # pirservice.mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
        # # pirservice.mqtt_client.connect(MQTT_BROKER, MQTT_PORT, keepalive=45)
        # pirservice.mqtt_client.enable_logger()
        # pirservice.mqtt_client.loop_start()
        # while not pirservice.mqtt_client.is_connected() and not pirservice.mqtt_client.mqtt_connection_error:
        #     time.sleep(1)
        # pirservice.mqtt_client.loop_stop()
        # if pirservice.mqtt_client.mqtt_connection_error:
        #     raise ConnectionError('Connection Error', pirservice.mqtt_client.mqtt_connection_error_rc)
        # pirservice.mqtt_connected = True
        self.pir = MotionSensor(23)
        # pirservice.notify.notify("STATUS=Waiting for motion")
        pirservice.pir.when_motion = self.on_motion
        pirservice.pir.when_no_motion = self.on_no_motion
        # self.notify.notify("STATUS=Motion sensor ready")
        # self.notify.notify("WATCHDOG=1")
        # self.notify.notify("MAINPID=" + str(os.getpid()))
        systemd.daemon.notify("READY=1")
        
    def connect_mqtt(self):
        """ Connect to the MQTT broker and setup callbacks """
        # Set Connecting Client ID
        # mqtt.Client.mqtt_connection_error = False
        # mqtt.Client.mqtt_connection_error_rc = 0

        # self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT, keepalive=45)

        # self.mqtt_client.enable_logger()
        # self.mqtt_client.loop_start()

        # # Give some time for the connection to be established
        # while not self.mqtt_client.is_connected() and not self.mqtt_client.mqtt_connection_error:
        #     time.sleep(1)

        # self.mqtt_client.loop_stop()
        # if self.mqtt_client.mqtt_connection_error:
        #     raise ConnectionError('Connection Error', self.mqtt_client.mqtt_connection_error_rc)

        # return self.mqtt_client
    
    def on_connect(self, client, userdata, flags, return_code):
        """ When connecting to MQTT, set flags on err """
        # pylint: disable=unused-argument
        # if return_code!=0:
        #     client.mqtt_connection_error = True
        #     client.mqtt_connection_error_rc = return_code

    def on_disconnect(self, client, userdata, return_code):
        """ Capture reporting when disconnecting from MQTT """
        # pylint: disable=unused-argument
        # if return_code:
        #     logger.warning("Disconnecting on error: %s", str(return_code))
        #     # exit()
        # else:
        #     logger.info("Diconnecting from MQTT broker: %s", str(MQTT_BROKER))


    def request_shutdown(self, *args):
        """ request shutdown for SIGINT """
        print('Request to shutdown received, stopping')
        self.pir.close()
        self.shutdown_requested = True

    def can_run(self):
        """ can run for SIGINT """
        return not self.shutdown_requested

    def publish(client, msg):
        """ Publish MQTT message """
        # result = client.publish(TOPIC, msg, retain=False)
        # result: [0, 1]
        
    def on_motion(self):
        """ Take action when PIR senses motion """
        # try:
        #     if pirservice.xscreensaver_support:
        #         logger.debug("Turn off screen saver")
        #         completed_process = subprocess.run(["/usr/bin/xscreensaver-command", "-display",  \
        #                     ":0.0", "-deactivate"], \
        #                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        #         if completed_process.returncode:
                    # logger.error("Xscreensaver error: %s", completed_process.returncode)

    def on_no_motion(self):
        """ Take action when PIR senses motion """

pirservice = pirservice()

while pirservice.can_run():
    time.sleep(1)
