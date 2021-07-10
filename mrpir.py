import logging
from numbers import Number
import string
from gpiozero import MotionSensor
from signal import pause
from paho.mqtt import client as mqttpub
import time
from decouple import UndefinedValueError, config
import os

myclient = ""
pir = ""

# Setup the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
#ch = logging.StreamHandler();
ch = logging.FileHandler('/tmp/mrpir.log')
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

try:
    # Place user and password in local .env file
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

try:
   MQTT_PORT = config ("MQTT_PORT", cast=int)

except UndefinedValueError as err:
    logger.warning('Warning: MQTT_PORT was not provided, using defaul value of 1883')
    
except Exception as err:
    logger.exception("Error reading MQTT_PORT, using defaul value of 1883")
    exit()

finally:   
    MQTT_PORT = 1883

try:
    PIR_PIN = config ("PIR_PIN")

except UndefinedValueError as err:
    logger.warning('Error getting PIR_PIN from .env file, using defaul value of 23')
    
except Exception as err:
    logger.exception('Error getting PIR_PIN from .env file, using defaul value of 23')
    exit()

finally:
    PIR_PIN = 23

try:
    LOGGING_LEVEL = config ("LOGGING_LEVEL", cast=int) * 10

except UndefinedValueError as err:
    logger.exception('Error getting LOGGING_LEVEL from .env file, using defaul value of WARNING log level')
    LOGGING_LEVEL = 10

finally:
    logger.setLevel(LOGGING_LEVEL)

mqttpub.Client.mqtt_connection_error = False
mqttpub.Client.mqtt_connection_error_rc = 0
#mqttpub.Client.LOGGING_LEVEL = LOGGING_LEVEL

print(str(logger.getEffectiveLevel))

def on_connect(client, userdata, flags, rc):
    if rc==0:
        client.connected_flag=True #set flag
        #logger.debug("connected OK Returned code =", rc)
        #client.subscribe("$SYS/#")
    else:
        #logger.debug("Bad connection Returned code = ", rc)
        client.mqtt_connection_error = True
        client.mqtt_connection_error_rc = rc

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.

def on_disconnect(client, userdata, rc):
    logger.warning("disconnecting reason: " + str(rc))
#    client.loop_stop()
    exit()

def on_log(client, userdata, level, buf):
    logger.info(buf)

def connect_mqtt():
    # Set Connecting Client ID
    myclient = mqttpub.Client(MQTT_CLIENT_ID)
    myclient.on_connect = on_connect
    myclient.on_disconnect = on_disconnect
    myclient.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    myclient.connect(MQTT_BROKER, MQTT_PORT, keepalive=45)
    myclient.loop_start()
    while not myclient.is_connected() and not myclient.mqtt_connection_error:
        time.sleep(1)
    myclient.loop_stop()
    if (myclient.mqtt_connection_error):
        raise Exception('Connection Error', myclient.mqtt_connection_error_rc)
    return myclient

def publish(client, msg):
    result = client.publish(TOPIC, msg)
    # result: [0, 1]
    status = result[0]
#    if status == 0:
#        logger.debug(f"Send `{msg}` to topic `{TOPIC}`")
#    else:
#        logger.debug(f"Failed to send message to topic {TOPIC}")

def on_motion():
    try:
        logger.info("Turn off screen saver")
        os.system("/usr/bin/xscreensaver-command -display " + '":0.0"' + " -deactivate >> /home/pi/xscreensaver.log")
        logger.info("Motion Detected")
        publish(myclient, "ON")
    except Exception as err:
        logger.error(str(err))
    
def on_no_motion():
    logger.info("motion off")
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
#    logger.info("publish config")
    myclient.publish(CONFIG_TOPIC, CONFIG_PAYLOAD)
    logger.info("Connecting to PIR on pin: %s" % PIR_PIN)
    pir = MotionSensor(PIR_PIN)
    pir.when_motion = on_motion
    pir.when_no_motion = on_no_motion
    logger.info("waiting for motion")
#    pause()
    myclient.loop_start()
    myclient.loop_forever()

except KeyboardInterrupt:
    logger.info (' ')
    logger.info ('Disconnecting from MQTT broker...')

finally:
    if myclient.is_connected():
        myclient.disconnect()
        myclient.loop_start()
        while myclient.is_connected():
            time.sleep(1)
    
    myclient.loop_stop()
    pir.close()
    logger.info ('Done')

