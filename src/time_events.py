"""
Time-based event scheduling utility that supports callbacks for sunup, sundown, and custom times based on geographic location and date.
"""

from datetime import datetime, timedelta
import pytz  # pylint: disable=import-error
import threading
import logging
from astral import LocationInfo
from astral.sun import sun

logger = logging.getLogger(__name__)

class TimeEvents:
    """
    Schedules callbacks to be fired at specific time events (e.g., sunup, sundown) and delays.

    Attributes:
        config (dict): Configuration settings for time events, including location details.
        location (LocationInfo): The geographic location for calculating sunup and sundown times.
    """

    def __init__(self, config):
        """
        Initializes the TimeEvents class with the given configuration.

        Args:
            config (dict): Configuration settings for time events, including location details.
        """
        self.config = config
        self.location = LocationInfo(config['location_name'], config['region'], "UTC", config['latitude'], config['longitude'])
        self.local_tz = pytz.timezone(self.location.timezone)
        logger.debug("Initialized TimeEvents at location '%s'", self.location.name)

    def _calculate_event_time(self, event: str) -> datetime:
        """
        Determines the time of the specified event (sunup, sundown) based on the geographic location.

        Args:
            event (str): The event type ('sunup' or 'sundown').

        Returns:
            datetime: A datetime object representing the event time.
        """
        s = sun(self.location.observer, date=datetime.now(self.local_tz))

        if event == 'sundown':
            event_time = s['sunset']
        elif event == 'sunup':
            event_time = s['sunrise']
        else:
            raise ValueError(f"Invalid event type '{event}'. Use 'sunup' or 'sundown'.")
        
        logger.debug("Calculated event time for '%s': %s", event, event_time)
        return event_time

    def schedule_sunup_callback(self, callback, delay_seconds: float = 0) -> None:
        """
        Schedules a callback to be fired after the sunup time and the specified delay.

        Args:
            callback (callable): The function to call after the delay.
            delay_seconds (float): The delay in seconds after the event to wait before firing the callback.
        """
        self._schedule_recurring_event('sunup', callback, delay_seconds)

    def schedule_sundown_callback(self, callback, delay_seconds: float = 0) -> None:
        """
        Schedules a callback to be fired after the sundown time and the specified delay.

        Args:
            callback (callable): The function to call after the delay.
            delay_seconds (float): The delay in seconds after the event to wait before firing the callback.
        """
        self._schedule_recurring_event('sundown', callback, delay_seconds)

    def _schedule_recurring_event(self, event: str, callback, delay_seconds: float) -> None:
        """
        Schedules a callback to be fired at the specified event time and reschedules it for the next day.

        Args:
            event (str): The event type ('sunup' or 'sundown').
            callback (callable): The function to call after the delay.
            delay_seconds (float): The delay in seconds after the event to wait before firing the callback.
        """
        event_time = self._calculate_event_time(event)
        now = datetime.now(self.local_tz)

        if now > event_time:
            # If the current time is after the event time, schedule for tomorrow
            event_time += timedelta(days=1)

        total_delay = (event_time - now).total_seconds() + delay_seconds
        logger.debug("Scheduling callback in %d seconds for event '%s'", total_delay, event)

        def delayed_execution():
            callback()  # Execute the callback
            logger.debug("Callback for event '%s' executed, rescheduling for next day", event)
            # Reschedule the callback for the next day's event
            self._schedule_recurring_event(event, callback, delay_seconds)

        threading.Timer(total_delay, delayed_execution).start()

    def get_timezone(self) -> str:
        """
        Returns the time zone associated with the scheduler's location.

        Returns:
            str: The time zone name (e.g., 'America/New_York').
        """
        timezone = self.local_tz.zone
        logger.debug("Timezone for location '%s': %s", self.location.name, timezone)
        return timezone

    def start(self) -> None:
        """
        Starts the time event scheduling process.
        """
        logger.info("TimeEvents started at location '%s'", self.location.name)

    def stop(self) -> None:
        """
        Stops the time event scheduling process.
        """
        logger.info("TimeEvents stopped at location '%s'", self.location.name)

# Example usage:
# def sunup_callback():
#     print("Sunup event triggered.")

# def sundown_callback():
#     print("Sundown event triggered.")

# config = {
#     'location_name': 'New York',
#     'region': 'USA',
#     'latitude': 40.7128,
#     'longitude': -74.0060
# }

# time_events = TimeEvents(config)
# time_events.schedule_sunup_callback(sunup_callback, delay_seconds=1800)  # 30 minutes after sunup
# time_events.schedule_sundown_callback(sundown_callback, delay_seconds=3600)  # 1 hour after sundown
# time_events.start()
