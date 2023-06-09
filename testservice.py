# Python script for the Python Demo Service

if __name__ == '__main__':
    import os
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
    _systemd_notify = None
    _mqtt_client = None
    _logger = None
    _mqtt_connection_error = False
    _mqtt_connection_error_rc = 0
    
    shutdown_requested = False
    
    def __init__(self):
        signal.signal(signal.SIGINT, self.request_shutdown)
        signal.signal(signal.SIGTERM, self.request_shutdown)
        _logger = logging.getLogger('mrpir')
        
        time.sleep(1)
        # Tell systemd that our service is ready
        Pirservice._systemd_notify = sdnotify.SystemdNotifier()

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
        _logger.setLevel(self.LOGGING_LEVEL)
        _logger.info(str(_logger.getEffectiveLevel))

        Pirservice._systemd_notify.notify("Status=Setting up MQTT Client")
        # Setup MQTT
        Pirservice._mqtt_client = mqtt.Client(self.MQTT_CLIENT_ID)
        Pirservice._mqtt_client.enable_logger()
        Pirservice._mqtt_client.on_connect = self.on_connect
        Pirservice._mqtt_client.on_disconnect = self.on_disconnect
        Pirservice._mqtt_client.on_log = self.on_log
        Pirservice._mqtt_client.username_pw_set(self.MQTT_USER, self.MQTT_PASSWORD)
        

        # Finally, notify systemd
        Pirservice._systemd_notify.notify("READY=1")

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self._logger.info("Connected to MQTT broker")
            self._mqtt_client.subscribe(self.TOPIC)
            self._mqtt_client.publish(self.CONFIG_TOPIC, self.CONFIG_PAYLOAD, retain=True)
        else:
            self._logger.error("Failed to connect to MQTT broker with error code %s", rc)

    def on_disconnect(self, client, userdata, rc): # pylint: disable=unused-argument
        if rc != 0:
            self._logger.warning("Unexpected disconnection from MQTT broker")

    def on_log(self, client, userdata, level, buf): # pylint: disable=unused-argument # pylint: disable=invalid-name 
        self._logger.debug("MQTT log: %s", buf)

    def __del__(self):
        shutdown_requested = False
        # pir.close()

    def can_run(self):
        """ can run for SIGINT """
        return not self.shutdown_requested
    
    def request_shutdown(self, *args):
        """ request shutdown for SIGINT """
        print('Request to shutdown received, stopping')
        # self.pir.close()
        self.shutdown_requested = True
        Pirservice._systemd_notify.notify("STOPPING=1")

    def connect_mqtt(self):
        """ Connect to the MQTT broker and setup callbacks """
        # Set Connecting Client ID
        Pirservice._mqtt_client.connect(self.MQTT_BROKER, self.MQTT_PORT, keepalive=45)
        # self._mqtt_client.connect(self.MQTT_BROKER, self.MQTT_PORT, keepalive=45)

        self._mqtt_client.enable_logger()
        self._mqtt_client.loop_start()

        # Give some time for the connection to be established
        while not self._mqtt_client.is_connected() and not self._mqtt_connection_error:
            time.sleep(1)

        self._mqtt_client.loop_stop()
        if self._mqtt_connection_error:
            raise ConnectionError('Connection Error', self._mqtt_connection_error_rc)

        return self._mqtt_client


    def on_motion():
        Pirservice._logger.info("Motion detected")
        pirservice.connect_mqtt()
        Pirservice._mqtt_client.publish(Pirservice.TOPIC, "ON", retain=True)

    def on_no_motion():
        Pirservice._logger.info("No motion detected")
        pirservice.connect_mqtt()
        Pirservice._mqtt_client.publish(Pirservice.TOPIC, "OFF", retain=True)

pirservice = Pirservice()
Pirservice._systemd_notify.notify("Status=entering main loop")
# Pirservice._logger.info('entering main loop')

try:
    pir = MotionSensor(pirservice.PIR_PIN)
    pir.when_motion = pirservice.on_motion
    pir.when_no_motion = pirservice.on_no_motion

    while pirservice.can_run():
        # blocking... should use wait_for_motion(timeout=5)
        pir.wait_for_motion(timeout=5)
        Pirservice._systemd_notify.notify("WATCHDOG=1")
        pir.wait_for_no_motion(timeout=15)
        Pirservice._systemd_notify.notify("WATCHDOG=1")

finally:
    pir.close()