import os
import time
import string
import yaml
import logging
import logging.config
from numbers import Number
from gpiozero import MotionSensor
from paho.mqtt import client as mqttpub
from decouple import UndefinedValueError, config
import subprocess
#import systemd.journal

# Setup the logger
with open(os.path.abspath(os.path.dirname(__file__)) + '/logging.yml', 'r') as f:
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
    CONFIG_PAYLOAD = '{"name": "' + MQTT_DEVICE + '_motion' + '", "device_class": "motion", "unique_id": "' + MQTT_CLIENT_ID + '_' + MQTT_DEVICE + '_id' + '", "state_topic": "homeassistant/binary_sensor/' + MQTT_DEVICE + '/state"}'
    TOPIC = 'homeassistant/binary_sensor/' + MQTT_DEVICE + '/state'

except UndefinedValueError as err:
    logger.exception("Error reading settings from .env file")
    exit()

# Get optional setting from local .env file
try:
   XSCREENSAVER_SUPPORT = config ("XSCREENSAVER_SUPPORT", cast=bool)

except UndefinedValueError as err:
    logger.warning('Warning: XSCREENSAVER_SUPPORT was not provided, using defaul value of False')
    XSCREENSAVER_SUPPORT = False
    
except Exception as err:
    logger.exception("Error reading XSCREENSAVER_SUPPORT, using defaul value of False")
    XSCREENSAVER_SUPPORT = False

# Get optional setting from local .env file
try:
   MQTT_PORT = config ("MQTT_PORT", cast=int)

except UndefinedValueError as err:
    logger.warning('Warning: MQTT_PORT was not provided, using defaul value of 1883')
    MQTT_PORT = 1883
    
except Exception as err:
    logger.exception("Error reading MQTT_PORT, using defaul value of 1883")
    MQTT_PORT = 1883

# Get optional setting from local .env file
try:
    PIR_PIN = config ("PIR_PIN")

except UndefinedValueError as err:
    logger.warning('Error getting PIR_PIN from .env file, using defaul value of 23')
    PIR_PIN = 23
    
except Exception as err:
    logger.exception('Error getting PIR_PIN from .env file, using defaul value of 23')
    PIR_PIN = 23

# Get optional setting from local .env file ***** Need to update this block *******
try:
    LOGGING_LEVEL = config ("LOGGING_LEVEL", cast=int) * 10

except UndefinedValueError as err:
    logger.exception('Error getting LOGGING_LEVEL from .env file, using defaul value of WARNING log level')
    LOGGING_LEVEL = 10

finally:
    logger.setLevel(LOGGING_LEVEL)

logger.info(str(logger.getEffectiveLevel))

# When connecting to MQTT, set flags on err
def on_connect(client, userdata, flags, rc):
    if rc!=0:
        client.mqtt_connection_error = True
        client.mqtt_connection_error_rc = rc

# Capture reporting when disconnecting from MQTT
def on_disconnect(client, userdata, rc):
    if (rc):
        logger.warning("Disconnecting on error: " + str(rc))
        exit()
    else:  
        logger.info("Diconnecting from MQTT broker: " + MQTT_BROKER)

# Log MQTT messages if set to DEBUG
def on_log(client, userdata, level, buf):
    if (logger.getEffectiveLevel == logging.DEBUG):
        logger.debug(buf)

# Connect to the MQTT broker and setup callbacks
def connect_mqtt():
    # Set Connecting Client ID
    mqttpub.Client.mqtt_connection_error = False
    mqttpub.Client.mqtt_connection_error_rc = 0
    mqttpub.Client.xscreensaver_support = XSCREENSAVER_SUPPORT

    myclient = mqttpub.Client(MQTT_CLIENT_ID)
    myclient.on_connect = on_connect
    myclient.on_disconnect = on_disconnect
    myclient.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    myclient.connect(MQTT_BROKER, MQTT_PORT, keepalive=45)
    myclient.loop_start()

    # Give some time for the connection to be established
    while not myclient.is_connected() and not myclient.mqtt_connection_error:
        time.sleep(1)
    
    myclient.loop_stop()
    if (myclient.mqtt_connection_error):
        raise Exception('Connection Error', myclient.mqtt_connection_error_rc)
    
    return myclient

# Publish MQTT message
def publish(client, msg):
    result = client.publish(TOPIC, msg)
    # result: [0, 1]
    status = result[0]
    if status != 0:
        logger.warning(f"Failed to send message to topic {TOPIC}")

# Take action when PIR senses motion
def on_motion():
    try:
        if (myclient.xscreensaver_support):
            logger.debug("Turn off screen saver")
            completed_process = subprocess.run(["/usr/bin/xscreensaver-command", "-deactivate"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if (completed_process.returncode):
                logger.warning("Xscreensaver error.", completed_process.stderr)

#        os.system("/usr/bin/xscreensaver-command -display " + '":0.0"' + " -deactivate >> /home/pi/xscreensaver.log")
        logger.debug("Motion Detected")
        publish(myclient, "ON")

    except Exception as err:
        logger.error(str(err))
    
def on_no_motion():
    logger.debug("motion off")
    publish(myclient, "OFF")

try:
    logger.info("Connecting to MQTT")
    myclient = connect_mqtt()
 
except Exception as inst:
    logger.exception('! Paho.mqtt error code: ')
    exit()

else:
    logger.info("Connected to MQTT")
    myclient.on_log = on_log

try:
    # Publish the home assistant autodiscovery entry for this motion sensor
    myclient.publish(CONFIG_TOPIC, CONFIG_PAYLOAD)
    logger.info("Connecting to PIR on pin: %s" % PIR_PIN)
    pir = MotionSensor(PIR_PIN)
    pir.when_motion = on_motion
    pir.when_no_motion = on_no_motion

    logger.info("waiting for motion")
    myclient.loop_start()
    myclient.loop_forever()

except KeyboardInterrupt:
    logger.info ('Execution stopped by user')

except Exception as err:
    logger.error(str(err))

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
    exit("Terminated")