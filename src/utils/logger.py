import os
import logging
import logging.config
import yaml
from queue import Queue
from logging.handlers import QueueHandler, QueueListener

class ExcludeSystemdNotifierFilter(logging.Filter):
    """
    Custom filter to exclude messages from 'sdnotify.SystemdNotifier' with specific content.
    """
    def filter(self, record):
        # Exclude messages from 'sdnotify.SystemdNotifier' with specific content
        if "STATUS=Running" in record.msg or "WATCHDOG=1" in record.msg:
            return False
        return True

class LoggerManager:
    _instance = None

    def __new__(cls, config_path='~/.mrpir/config/log_config.yaml'):
        if cls._instance is None:
            cls._instance = super(LoggerManager, cls).__new__(cls)
            cls._instance._initialize(config_path)
        return cls._instance

    def _initialize(self, config_path):
        # Load logging configuration from a YAML file
        try:
            self._setup_logging(config_path)
            
            # Set up queue-based asynchronous logging after the logger is configured
            self.log_queue = Queue()
            self.queue_handler = QueueHandler(self.log_queue)
            self.listener = QueueListener(self.log_queue, *logging.getLogger().handlers)
            self.listener.start()

        except Exception as e:
            logging.basicConfig(level=logging.INFO)
            logging.error("Failed to load logging configuration, using basic config", exc_info=e)

    def _setup_logging(self, config_path):
        # Define the log directory within the user's home directory
        log_dir = os.path.expanduser('~/.mrpir/logs')

        # Ensure the log directory exists
        os.makedirs(log_dir, exist_ok=True)

        # Adjust the path to the logging configuration file, expanding user directory
        config_path = os.path.expanduser(config_path)

        if os.path.exists(config_path):
            with open(config_path, 'rt', encoding='utf-8') as file:
                try:
                    config = yaml.safe_load(file.read())
                    if config is not None:
                        # Dynamically update the logfile path in the configuration
                        for handler in config.get('handlers', {}).values():
                            if 'filename' in handler:
                                handler['filename'] = os.path.join(log_dir, os.path.basename(handler['filename']))

                        logging.config.dictConfig(config)
                        # Add the custom filter programmatically
                        self._add_custom_filters()

                    else:
                        raise ValueError("Loaded YAML configuration is empty.")
                except yaml.YAMLError as err:
                    logging.basicConfig(level=logging.INFO)
                    logging.error(f"Error parsing YAML file: {err}")
        else:
            logging.basicConfig(level=logging.INFO)
            logging.warning(f"Logging configuration file not found: {config_path}")

    def _add_custom_filters(self):
        # Get the root logger
        root_logger = logging.getLogger()
        
        # Create an instance of the custom filter
        custom_filter = ExcludeSystemdNotifierFilter()
        
        # Add the custom filter to the desired handlers
        for handler in root_logger.handlers:
            handler.addFilter(custom_filter)

    @staticmethod
    def get_logger(name):
        # Ensure the LoggerManager is initialized
        if LoggerManager._instance is None:
            LoggerManager()
        
        logger = logging.getLogger(name)

        # Check if handlers are already added to avoid duplicates
        if not logger.hasHandlers():
            logger.addHandler(LoggerManager._instance.queue_handler)
            
        return logger

    @staticmethod
    def log_info(logger, message, **kwargs):
        logger.info(message, extra=kwargs)

    @staticmethod
    def log_warning(logger, message, **kwargs):
        logger.warning(message, extra=kwargs)

    @staticmethod
    def log_debug(logger, message, **kwargs):
        logger.debug(message, extra=kwargs)

    @staticmethod
    def log_error(logger, message, **kwargs):
        logger.error(message, extra=kwargs)

    @staticmethod
    def log_exception(logger, error):
        logger.error("Exception occurred", exc_info=error)

# Example usage:
# if __name__ == "__main__":
#     logger = LoggerManager.get_logger(__name__)
#     LoggerManager.log_info(logger, "Application started")
#     LoggerManager.log_warning(logger, "This is a warning message")
#     LoggerManager.log_debug(logger, "This is a debug message")
#     LoggerManager.log_error(logger, "This is an error message")

#     try:
#         raise ValueError("An example error")
#     except Exception as e:
#         LoggerManager.log_exception(logger, e)
