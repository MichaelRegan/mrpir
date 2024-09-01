import sdnotify
from utils.logger import logger


class ServiceManager:
    """
    Manages communication with systemd, handling notifications for startup,
    status updates, and shutdown.

    Attributes:
        config (dict): Configuration settings for the service.
        notifier (sdnotify.SystemdNotifier): The notifier used to communicate with systemd.
    """

    def __init__(self, config):
        """
        Initializes the ServiceManager with the given configuration.

        Args:
            config (dict): Configuration settings for the service.
        """
        self.config = config
        self.notifier = sdnotify.SystemdNotifier()

    def notify_startup(self):
        """
        Notifies systemd that the service has started and is ready.
        Logs the startup notification.
        """
        self.notifier.notify("READY=1")
        logger.info("Service started and notified systemd")

    def notify_status(self, status):
        """
        Notifies systemd of the current status of the service.
        Logs the status update.

        Args:
            status (str): The current status of the service to be sent to systemd.
        """
        self.notifier.notify(f"STATUS={status}")
        logger.info(f"Service status updated: {status}")

    def notify_shutdown(self):
        """
        Notifies systemd that the service is stopping.
        Logs the shutdown notification.
        """
        self.notifier.notify("STOPPING=1")
        logger.info("Service is shutting down")
