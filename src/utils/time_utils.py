from datetime import datetime, timedelta
import pytz

def is_after_sundown(time_zone):
    local_tz = pytz.timezone(time_zone)  # Update to your timezone
    sundown = local_tz.localize(datetime.now().replace(hour=18, minute=0, second=0, microsecond=0))
    now = datetime.now(local_tz)
    return now > sundown

def time_until_sundown(self):
    now = datetime.now(pytz.timezone(self.config.time_zone))
    sundown_time = now.replace(hour=18, minute=0, second=0, microsecond=0)
    if now > sundown_time:
        # Sundown has already occurred today; wait until tomorrow
        sundown_time += timedelta(days=1)
    return (sundown_time - now).total_seconds()
