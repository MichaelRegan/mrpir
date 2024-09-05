"""
Time-based event scheduling utility that supports callbacks for sunup, sundown, and custom times based on geographic location and date.
"""

from datetime import datetime, timedelta
import pytz  # pylint: disable=import-error
import threading
from astral import LocationInfo
from astral.sun import sun
from base_component import BaseComponent

class TimeEvents(BaseComponent):
    """
    Schedules callbacks to be fired at specific time events (e.g., sunup, sundown) and delays.

    Attributes:
        config (dict): Configuration settings for time events, including location details.
        location (LocationInfo): The geographic location for calculating sunup and sundown times.
    """

    def __init__(self, config):
        super().__init__(__name__)
        """
        Initializes the TimeEvents class with the given configuration.

        Args:
            config (dict): Configuration settings for time events, including location details.
        """
        self.config = config
        self.location = LocationInfo(config.location_name, config.region, "UTC", config.latitude, config.longitude)
        self.local_tz = pytz.timezone(self.location.timezone)
        self.timers = []  # List to keep track of active timers

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
        
        self.log_debug(f"Calculated event time for {event}: {event_time}")
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
        self.log_debug("Scheduling callback in {total_delay} seconds for event '{event}'")

        def delayed_execution():
            callback()  # Execute the callback
            self.log_debug(f"Callback for event {event} executed, rescheduling for next day")
            # Reschedule the callback for the next day's event
            self._schedule_recurring_event(event, callback, delay_seconds)

        timer = threading.Timer(total_delay, delayed_execution)
        self.timers.append(timer)  # Keep track of the timer
        timer.start()

    def _schedule_test_event(self, event: str, callback, delay_seconds: float) -> None:
        """
        Schedules a callback to be fired at the specified event time and reschedules it for the next day.

        Args:
            event (str): The event type ('sunup' or 'sundown').
            callback (callable): The function to call after the delay.
            delay_seconds (float): The delay in seconds after the event to wait before firing the callback.
        """

        def delayed_execution():
            try:
                if callable(callback):
                    callback()
                else:            
                    self.log_error(f"Callback for event '{event}' is not callable")
            except Exception as e:
                self.log_error(f"Error in callback execution: {e}")

            self.log_debug(f"Callback for event {event} executed, rescheduling for next day")
            # Reschedule the callback for the next day's event
            self._schedule_test_event(event, callback, delay_seconds)

        timer = threading.Timer(5, delayed_execution)
        self.timers.append(timer)  # Keep track of the timer
        timer.start()

    def get_timezone(self) -> str:
        """
        Returns the time zone associated with the scheduler's location.

        Returns:
            str: The time zone name (e.g., 'America/New_York').
        """
        timezone = self.local_tz.zone
        self.log_debug(f"Timezone for location '{self.location.name}': {timezone}")
        return timezone

    def start(self) -> None:
        """
        Starts the time event scheduling process.
        """
        self.log_info(f"TimeEvents started at location '{self.location.name}'")

    def stop(self) -> None:
        """
        Stops the time event scheduling process.
        """
        self.log_info(f"TimeEvents stopped at location '{self.location.name}'")
        for timer in self.timers:
            timer.cancel()
        self.timers.clear()  # Clear the list of timers

        
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
