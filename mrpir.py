""" This file reads pir signals and posts them to MQTT """
import os # pylint: disable=import-error
import sys # pylint: disable=import-error
import time # pylint: disable=import-error
import subprocess # pylint: disable=import-error
import logging # pylint: disable=import-error
import logging.config # pylint: disable=import-error
from decouple import UndefinedValueError, config # pylint: disable=import-error
import yaml # pylint: disable=import-error
from gpiozero import MotionSensor # pylint: disable=import-error
import paho.mqtt.client as mqtt # pylint: disable=import-error

# Setup the logger
with open(os.path.abspath(os.path.dirname(__file__)) + '/logging.yml', 'r', encoding='UTF-8') as f:
    logger_config = yaml.safe_load(f.read())
    logging.config.dictConfig(logger_config)

logger = logging.getLogger('mrpir')

# mqtt client
# mrClient = mqtt.Client()

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

def on_connect(client, userdata, flags, return_code):
    """ When connecting to MQTT, set flags on err """
    # pylint: disable=unused-argument
    if return_code!=0:
        client.mqtt_connection_error = True
        client.mqtt_connection_error_rc = return_code

def on_disconnect(client, userdata, return_code):
    """ Capture reporting when disconnecting from MQTT """
    # pylint: disable=unused-argument
    if return_code:
        logger.warning("Disconnecting on error: %s", str(return_code))
        # exit()
    else:
        logger.info("Diconnecting from MQTT broker: %s", str(MQTT_BROKER))

def on_log(client, userdata, level, buf):
    """ Log MQTT messages if set to DEBUG """
    # pylint: disable=unused-argument
    if logger.getEffectiveLevel == logging.DEBUG:
        logger.debug(buf)

def connect_mqtt():
    """ Connect to the MQTT broker and setup callbacks """
    # Set Connecting Client ID
    mqtt.Client.mqtt_connection_error = False
    mqtt.Client.mqtt_connection_error_rc = 0
    mqtt.Client.xscreensaver_support = XSCREENSAVER_SUPPORT

    mqtt_client = mqtt.Client(MQTT_CLIENT_ID)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_disconnect = on_disconnect
    mqtt_client.on_log = on_log
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, keepalive=45)

    mqtt_client.enable_logger()
    mqtt_client.loop_start()

    # Give some time for the connection to be established
    while not mqtt_client.is_connected() and not mqtt_client.mqtt_connection_error:
        time.sleep(1)

    mqtt_client.loop_stop()
    if mqtt_client.mqtt_connection_error:
        raise ConnectionError('Connection Error', mqtt_client.mqtt_connection_error_rc)

    return mqtt_client

def publish(client, msg):
    """ Publish MQTT message """
    result = client.publish(TOPIC, msg, retain=False)
    # result: [0, 1]
    status = result[0]
    if status != 0:
        logger.warning("Failed to send message to topic: %s", str(TOPIC))

def on_motion():
    """ Take action when PIR senses motion """
    try:
        if myclient.xscreensaver_support:
            logger.debug("Turn off screen saver")
            completed_process = subprocess.run(["/usr/bin/xscreensaver-command", "-display",  \
                        ":0.0", "-deactivate"], \
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            if completed_process.returncode:
                logger.error("Xscreensaver error: %s", completed_process.returncode)

#        os.system("/usr/bin/xscreensaver-command -display " + '":0.0"' + \
#        " -deactivate >> /home/pi/xscreensaver.log")
        logger.debug("Motion Detected")
        publish(myclient, "ON")

    except Exception as on_motion_err: # pylint: disable=broad-except
        logger.error(str(on_motion_err))

def on_no_motion():
    """ Publish to MQTT on motion events """
    logger.debug("motion off")
    publish(myclient, "OFF")

try:
    logger.info("Connecting to MQTT")
    myclient = connect_mqtt()

except IOError as on_no_motion_error:
    logger.exception('Connection Error: %s', on_no_motion_error.strerror)
    sys.exit(0)

else:
    logger.info("Connected to MQTT")
    # myclient.on_log = on_log

try:
    # Publish the home assistant autodiscovery entry for this motion sensor
    myclient.publish(CONFIG_TOPIC, CONFIG_PAYLOAD, qos=0, retain=True)
    logger.info("Connecting to PIR on pin: %s", PIR_PIN)
    pir = MotionSensor(PIR_PIN)
    pir.when_motion = on_motion
    pir.when_no_motion = on_no_motion

    logger.info("waiting for motion")
    myclient.loop_start()
    myclient.loop_forever(retry_first_connection=False)

except KeyboardInterrupt:
    logger.info ('Execution stopped by user')

# except Exception as err:
#     logger.error(str(err))

finally:
    if myclient.is_connected():
        myclient.disconnect()
        myclient.loop_start()
        while myclient.is_connected():
            time.sleep(1)

    myclient.loop_stop()
    pir.close()

    # As a service, this component should never stop. Exit with error for autorestart to kick in
    logger.error("Exiting with error")
    # exit("Terminated")
    sys.exit(0)


def test_on_motion():
    """ Test on_motion """
    on_motion() # pylint: disable=no-value-for-parameter
