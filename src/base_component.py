"""
BaseComponent module that provides logging functionalities for derived classes.
"""

from utils import LoggerManager


class BaseComponent:
    """
    Provides a base class for components that require logging functionalities.
    """
    def __init__(self, name):
        """
        Initializes the BaseComponent with a logger.

        Args:
            name (str): The name of the logger.
        """
        self.logger = LoggerManager.get_logger(name)

    def log_info(self, message, **kwargs):
        """
        Logs an informational message.

        Args:
            message (str): The message to log.
        """
        LoggerManager.log_info(self.logger, message, **kwargs)

    def log_warning(self, message, **kwargs):
        """
        Logs a warning message.

        Args:
            message (str): The message to log.
        """
        LoggerManager.log_warning(self.logger, message, **kwargs)

    def log_debug(self, message, **kwargs):
        """
        Logs a debug message.

        Args:
            message (str): The message to log.
        """
        LoggerManager.log_debug(self.logger, message, **kwargs)

    def log_error(self, message, **kwargs):
        """
        Logs an error message.

        Args:
            message (str): The message to log.
        """
        LoggerManager.log_error(self.logger, message, **kwargs)

    def handle_exception(self, error, message="An exception occurred"):
        """
        Handles an exception by logging it.

        Args:
            error (Exception): The exception to log.
            message (str): The message to log with the exception.
        """
        LoggerManager.log_exception(self.logger, error)
