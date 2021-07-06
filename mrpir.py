from numbers import Number
from gpiozero import MotionSensor
from signal import pause
from paho.mqtt import client as mqttpub
import time
from decouple import config

myclient = ""
pir = ""

# Place user and password in local .env file
MQTT_USER = config('MQTT_USER_NAME')
MQTT_PASSWORD = config('MQTT_PASSWORD')
MQTT_DEVICE = config('MQTT_DEVICE')
MQTT_CLIENT_ID = config ("MQTT_CLIENT_ID")
MQTT_BROKER = config ("MQTT_BROKER")
MQTT_PORT = config ("MQTT_PORT", cast=int)

PIR_PIN = config ("PIR_PIN")

CONFIG_TOPIC = "homeassistant/binary_sensor/" + MQTT_DEVICE + "/config"
CONFIG_PAYLOAD = '{"name": "' + MQTT_DEVICE + '", "device_class": "motion", "state_topic": "homeassistant/binary_sensor/' + MQTT_DEVICE + '/state"}'
TOPIC = "homeassistant/binary_sensor/' + MQTT_DEVICE + '/state"

def on_connect(client, userdata, flags, rc):
    if rc==0:
        client.connected_flag=True #set flag
        print("connected OK Returned code =",rc)
        #client.subscribe("$SYS/#")
    else:
        print("Bad connection Returned code = ",rc)

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.

def on_disconnect(client, userdata, rc):
    print("disconnecting reason  ",str(rc))
    client.loop_stop()

def connect_mqtt():
    # Set Connecting Client ID
    myclient = mqttpub.Client(MQTT_CLIENT_ID)
    myclient.on_connect = on_connect
    myclient.on_disconnect = on_disconnect
    myclient.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    myclient.loop_start()
    myclient.connect(MQTT_BROKER, MQTT_PORT)
    while not myclient.is_connected():
        time.sleep(1)
    myclient.loop_stop()
    return myclient

def publish(client, msg):
    result = client.publish(TOPIC, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{TOPIC}`")
    else:
        print(f"Failed to send message to topic {TOPIC}")

def on_motion():
    print("motion detected")
    publish(myclient, "ON")
    
def on_no_motion():
    print("motion off")
    publish(myclient, "OFF")


try:
    print("Connecting to MQTT")
    myclient = connect_mqtt()

except:
    print("connection failed")
    exit(1)

try:
    print("publish config")
    myclient.publish(CONFIG_TOPIC, CONFIG_PAYLOAD)
    print("Connecting to PIR on pin:", PIR_PIN)
    pir = MotionSensor(PIR_PIN)
    pir.when_motion = on_motion
    pir.when_no_motion = on_no_motion
    print ("waiting for motion")
#    pause()
    myclient.loop_start()
    time.sleep(1)
    myclient.loop_forever()

except KeyboardInterrupt:
    print (' ')
    print ('Disconnecting from MQTT broker...')

finally:
    myclient.loop_start()
    myclient.disconnect()
    while myclient.is_connected():
        time.sleep(1)
    print("connect done")
    myclient.loop_stop()
    pir.close()
    print ('done')

