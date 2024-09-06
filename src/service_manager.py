"""
Manages communication with systemd, handling notifications for startup,
status updates, and shutdown.
"""

import sdnotify  # pylint: disable=import-error
from base_component import BaseComponent  # pylint: disable=import-error


class ServiceManager(BaseComponent):
    """
    Manages communication with systemd, handling notifications for startup,
    status updates, and shutdown.

    Attributes:
        config (dict): Configuration settings for the service.
        notifier (sdnotify.SystemdNotifier): Notifier to communicate with systemd.
    """

    def __init__(self, config):
        """
        Initializes the ServiceManager with the given configuration.

        Args:
            config (dict): Configuration settings for the service.
        """
        super().__init__(__name__)
        self.config = config
        self.notifier = sdnotify.SystemdNotifier()
        self.notify_starting()

    def notify_starting(self) -> None:
        """
        Notify systemd that the service is starting.
        Logs the starting notification.
        """
        self.notifier.notify("STATUS=Starting")
        self.log_info("Service is starting")

    def notify_status(self, status: str) -> None:
        """
        Notify systemd of the current status of the service.
        Logs the status update.

        Args:
            status (str): The current status of the service.
        """
        self.notifier.notify(f"STATUS={status}")
        self.log_info(f"Service status updated: {status}")

    def notify_ready(self) -> None:
        """
        Notify systemd that the service is ready.
        Logs the ready notification.
        """
        self.notifier.notify("READY=1")
        self.log_info("Service is ready")

    def notify_running(self) -> None:
        """
        Notify systemd that the service is running.
        Logs the running notification.
        """
        self.notifier.notify("STATUS=Running")
        self.log_info("Service is running")

    def notify_stopping(self) -> None:
        """
        Notify systemd that the service is stopping.
        Logs the stopping notification.
        """
        self.notifier.notify("STOPPING=1")
        self.log_info("Service is stopping")

    def notify_watchdog(self) -> None:
        """
        Notify systemd that the service is still alive.
        """
        self.notifier.notify("WATCHDOG=1")

    def notify_reloading(self) -> None:
        """
        Notify systemd that the service is reloading.
        Logs the reloading notification.
        """
        self.notifier.notify("RELOADING=1")
        self.log_info("Service is reloading")
