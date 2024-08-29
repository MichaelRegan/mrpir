import sdnotify
from utils.logger import logger

class ServiceManager:
    def __init__(self, config):
        self.config = config
        self.notifier = sdnotify.SystemdNotifier()

    def notify_startup(self):
        self.notifier.notify("READY=1")
        logger.info("Service started and notified systemd")

    def notify_status(self, status):
        self.notifier.notify(f"STATUS={status}")
        logger.info(f"Service status updated: {status}")

    def notify_shutdown(self):
        self.notifier.notify("STOPPING=1")
        logger.info("Service is shutting down")
