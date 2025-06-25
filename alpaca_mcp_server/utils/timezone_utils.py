"""Timezone utilities for consistent Eastern time handling across the application."""

from datetime import UTC, datetime, timedelta, timezone


def get_eastern_time():
    """
    Get current time in Eastern timezone (EDT/EST).
    
    Returns:
        Tuple of (datetime object in Eastern timezone, timezone name string)
    """
    # Handle EDT (UTC-4) vs EST (UTC-5) automatically
    utc_now = datetime.now(UTC)

    # Simple DST check: March to November is EDT (UTC-4), otherwise EST (UTC-5)
    month = utc_now.month
    if 3 <= month <= 11:  # March through November - EDT
        eastern = timezone(timedelta(hours=-4))
        tz_name = "EDT"
    else:  # December, January, February - EST
        eastern = timezone(timedelta(hours=-5))
        tz_name = "EST"

    eastern_time = utc_now.astimezone(eastern)
    return eastern_time, tz_name


def get_eastern_time_string(format_str: str = "%Y-%m-%d %H:%M:%S %Z") -> str:
    """
    Get current Eastern time as a formatted string.
    
    Args:
        format_str: strftime format string (default: "%Y-%m-%d %H:%M:%S %Z")
        
    Returns:
        Formatted time string with Eastern timezone
    """
    eastern_time, tz_name = get_eastern_time()
    # Replace %Z with the actual timezone name since strftime doesn't handle our custom timezone
    format_with_tz = format_str.replace("%Z", tz_name)
    return eastern_time.strftime(format_with_tz)


def get_market_time_display() -> str:
    """
    Get current time in format suitable for market displays (HH:MM EDT/EST).
    
    Returns:
        Time string in format "HH:MM EDT" or "HH:MM EST"
    """
    eastern_time, tz_name = get_eastern_time()
    return f"{eastern_time.strftime('%H:%M')} {tz_name}"