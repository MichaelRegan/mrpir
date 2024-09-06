"""
LoggerManager module providing a singleton logger with configuration capabilities.
"""

import os
import logging
import logging.config
from queue import Queue
from logging.handlers import QueueHandler, QueueListener
import yaml


class ExcludeSystemdNotifierFilter(logging.Filter):
    """
    Custom filter to exclude messages from 'sdnotify.SystemdNotifier' with specific content.
    """
    def filter(self, record):
        """Filter out messages containing specific content."""
        if "STATUS=Running" in record.msg or "WATCHDOG=1" in record.msg:
            return False
        return True


class LoggerManager:
    """Singleton class to manage logging configuration and provide loggers."""
    _instance = None

    def __new__(cls, config_path='~/.mrpir/config/log_config.yaml'):
        if cls._instance is None:
            cls._instance = super(LoggerManager, cls).__new__(cls)
            cls._instance._initialize(config_path)
        return cls._instance

    def _initialize(self, config_path):
        """
        Initialize the LoggerManager with logging configuration.
        Args:
            config_path (str): Path to the logging configuration file.
        """
        try:
            self._setup_logging(config_path)
            self.log_queue = Queue()
            self.queue_handler = QueueHandler(self.log_queue)
            self.listener = QueueListener(
                self.log_queue, *logging.getLogger().handlers
            )
            self.listener.start()
        except (OSError, yaml.YAMLError) as error:
            logging.basicConfig(level=logging.INFO)
            logging.error(
                "Failed to load logging configuration, using basic config",
                exc_info=error
            )

    def _setup_logging(self, config_path):
        """
        Set up logging configuration from a YAML file.
        Args:
            config_path (str): Path to the logging configuration file.
        """
        log_dir = os.path.expanduser('~/.mrpir/logs')
        os.makedirs(log_dir, exist_ok=True)
        config_path = os.path.expanduser(config_path)

        if os.path.exists(config_path):
            with open(config_path, 'rt', encoding='utf-8') as file:
                config = yaml.safe_load(file.read())
                if config:
                    for handler in config.get('handlers', {}).values():
                        if 'filename' in handler:
                            handler['filename'] = os.path.join(
                                log_dir, os.path.basename(handler['filename'])
                            )
                    logging.config.dictConfig(config)
                    self._add_custom_filters()
                else:
                    raise ValueError("Loaded YAML configuration is empty.")
        else:
            logging.basicConfig(level=logging.INFO)
            logging.warning(f"Logging configuration file not found: {config_path}")

    def _add_custom_filters(self):
        """Add custom filters to the root logger."""
        root_logger = logging.getLogger()
        custom_filter = ExcludeSystemdNotifierFilter()
        for handler in root_logger.handlers:
            handler.addFilter(custom_filter)

    @staticmethod
    def get_logger(name):
        """
        Get a logger with the specified name.
        Args:
            name (str): The name of the logger.
        Returns:
            logging.Logger: Configured logger instance.
        """
        if LoggerManager._instance is None:
            LoggerManager()

        logger = logging.getLogger(name)
        if not logger.hasHandlers():
            logger.addHandler(LoggerManager._instance.queue_handler)
        return logger

    @staticmethod
    def log_info(logger, message, **kwargs):
        """
        Log an informational message.
        Args:
            logger (logging.Logger): Logger instance.
            message (str): The message to log.
        """
        logger.info(message, extra=kwargs)

    @staticmethod
    def log_warning(logger, message, **kwargs):
        """
        Log a warning message.
        Args:
            logger (logging.Logger): Logger instance.
            message (str): The message to log.
        """
        logger.warning(message, extra=kwargs)

    @staticmethod
    def log_debug(logger, message, **kwargs):
        """
        Log a debug message.
        Args:
            logger (logging.Logger): Logger instance.
            message (str): The message to log.
        """
        logger.debug(message, extra=kwargs)

    @staticmethod
    def log_error(logger, message, **kwargs):
        """
        Log an error message.
        Args:
            logger (logging.Logger): Logger instance.
            message (str): The message to log.
        """
        logger.error(message, extra=kwargs)

    @staticmethod
    def log_exception(logger, error):
        """
        Log an exception message.
        Args:
            logger (logging.Logger): Logger instance.
            error (Exception): The exception to log.
        """
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
