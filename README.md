# mrpir
Python script to support a PIR sensor on SBC's and publish over MQTT with Home Assistant discovery support

The following environment variables are used and should be stored in an .env file:

MQTT_USER_NAME=xyz
MQTT_PASSWORD=xyz
MQTT_DEVICE=xyz
MQTT_CLIENT_ID=xyz
MQTT_PORT=1883 or other if configured differently
MQTT_BROKER=servername or IP of the MQTT broker
PIR_PIN=signal pin connected to the presense sensor
MQTT_LOGGING=0 or 1 
