# Python script for the Python Demo Service

if __name__ == '__main__':
    import os
    import sys
    import time
    import signal # pylint: disable=import-error
    import sdnotify
    import logging # pylint: disable=import-error
    import logging.config # pylint: disable=import-error
    from decouple import UndefinedValueError, config # pylint: disable=import-error
    # import logging.config # pylint: disable=import-error
    import paho.mqtt.client as mqtt # pylint: disable=import-error
    import yaml # pylint: disable=import-error

class Pirservice:

    # Private variables
    _systemd_notify = None
    _mqtt_client = None
    _logger = None
    
    shutdown_requested = False
    
    def __init__(self):
        signal.signal(signal.SIGINT, self.request_shutdown)
        signal.signal(signal.SIGTERM, self.request_shutdown)
        logger = logging.getLogger('mrpir')
        
        time.sleep(5)
        # Tell systemd that our service is ready
        Pirservice._systemd_notify = sdnotify.SystemdNotifier()
        Pirservice._mqtt_client = mqtt.Client("myclientrandomeid")
        Pirservice._systemd_notify.notify("READY=1")

        # Setup logging
        with open(os.path.abspath(os.path.dirname(__file__)) + '/logging.yml', 'r', encoding='UTF-8') as f:
            logger_config = yaml.safe_load(f.read())
            logging.config.dictConfig(logger_config)
        
        Pirservice._logger = logging.getLogger('mrpir')

        # Read in reuited settings from local .env file
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
            sys.exit(0)

        print("mqtt_user: %s", MQTT_USER)

    def __delattr__(self):
        shutdown_requested = False

    def can_run(self):
        """ can run for SIGINT """
        return not self.shutdown_requested
    
    def request_shutdown(self, *args):
        """ request shutdown for SIGINT """
        print('Request to shutdown received, stopping')
        # self.pir.close()
        self.shutdown_requested = True
        Pirservice._systemd_notify.notify("STOPPING=1")


pirservice = Pirservice()

while pirservice.can_run():
    print('Hello from the MRPIR Service')
    time.sleep(5)
