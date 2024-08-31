from datetime import datetime
import pytz

def is_after_sundown(time_zone):
    local_tz = pytz.timezone(time_zone)  # Update to your timezone
    sundown = local_tz.localize(datetime.now().replace(hour=18, minute=0, second=0, microsecond=0))
    now = datetime.now(local_tz)
    return now > sundown
