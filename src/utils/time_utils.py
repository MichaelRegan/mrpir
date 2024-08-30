"""
Time utilities module.
This module provides utility functions for handling time operations,
including checking if the current time is after sundown.
"""

from datetime import datetime
import pytz

def is_after_sundown(timezone='America/Los_Angeles', sundown_hour=18, sundown_minute=0):
    """
    Determine if the current time is after sundown in a specified timezone.

    Args:
        timezone (str): The timezone to check against. Default is 'America/Los_Angeles'.
        sundown_hour (int): The hour when sundown is considered to occur. Default is 18 (6 PM).
        sundown_minute (int): The minute when sundown is considered to occur. Default is 0.

    Returns:
        bool: True if the current time is after sundown, False otherwise.
    """
    local_tz = pytz.timezone(timezone)
    sundown = local_tz.localize(
        datetime.now().replace(hour=sundown_hour,
                               minute=sundown_minute,
                               second=0,
                               microsecond=0))
    now = datetime.now(local_tz)
    return now > sundown
