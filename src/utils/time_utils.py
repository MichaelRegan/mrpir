from datetime import datetime, timedelta
import pytz


def is_after_sundown(time_zone: str) -> bool:
    """
    Determines if the current local time is after sundown (6:00 PM) in the specified time zone.

    Args:
        time_zone (str): The time zone to check against.

    Returns:
        bool: True if the current time is after sundown, False otherwise.
    """
    local_tz = pytz.timezone(time_zone)
    sundown = local_tz.localize(datetime.now().replace(hour=18, minute=0, second=0, microsecond=0))
    now = datetime.now(local_tz)
    return now > sundown


def time_until_sundown(time_zone: str) -> float:
    """
    Calculates the time in seconds until the next sundown (6:00 PM) in the specified time zone.

    Args:
        time_zone (str): The time zone to calculate against.

    Returns:
        float: The number of seconds until the next sundown.
    """
    now = datetime.now(pytz.timezone(time_zone))
    sundown_time = now.replace(hour=18, minute=0, second=0, microsecond=0)
    
    if now > sundown_time:
        # Sundown has already occurred today; calculate time until sundown tomorrow
        sundown_time += timedelta(days=1)
    
    return (sundown_time - now).total_seconds()
