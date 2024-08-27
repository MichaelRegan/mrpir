from sdnotify import SystemdNotifier

class ServiceManager:
    def __init__(self):
        self.notifier = SystemdNotifier()

    def notify_ready(self):
        self.notifier.notify("READY=1")

    def notify_stopping(self):
        self.notifier.notify("STOPPING=1")
