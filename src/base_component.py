# base_component.py

from utils.logger import LoggerManager

class BaseComponent:
    def __init__(self, name):
        self.logger = LoggerManager.get_logger(name)

    def log_info(self, message, **kwargs):
        LoggerManager.log_info(self.logger, message, **kwargs)

    def log_warning(self, message, **kwargs):
        LoggerManager.log_warning(self.logger, message, **kwargs)

    def log_debug(self, message, **kwargs):
        LoggerManager.log_debug(self.logger, message, **kwargs)

    def log_error(self, message, **kwargs):
        LoggerManager.log_error(self.logger, message, **kwargs)

    def handle_exception(self, error, message="An exception occurred"):
        LoggerManager.log_exception(self.logger, error)
