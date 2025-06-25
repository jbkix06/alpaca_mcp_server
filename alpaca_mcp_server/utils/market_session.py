"""Quick market session detection for faster trading decisions."""

from .timezone_utils import get_eastern_time, get_market_time_display


def get_current_market_session() -> tuple[str, str, bool]:
    """
    Get current market session with trading instructions.

    Returns:
        Tuple of (session_name, instruction, extended_hours_required)
    """
    now_et, tz_name = get_eastern_time()
    hour = now_et.hour
    minute = now_et.minute
    current_time_et = get_market_time_display()

    if 4 <= hour < 9 or (hour == 9 and minute < 30):
        return ("PRE-MARKET", f"🔴 PRE-MARKET ({current_time_et}) - Use extended_hours=true", True)
    elif (hour == 9 and minute >= 30) or (9 < hour < 16):
        return ("REGULAR", f"🟢 REGULAR HOURS ({current_time_et}) - Normal orders", False)
    elif 16 <= hour < 20:
        return (
            "AFTER-HOURS",
            f"🟡 AFTER-HOURS ({current_time_et}) - Use extended_hours=true",
            True,
        )
    else:
        return ("CLOSED", f"🔵 MARKETS CLOSED ({current_time_et}) - No trading", False)


def is_extended_hours() -> bool:
    """Quick check if extended hours trading is required."""
    _, _, extended_required = get_current_market_session()
    return extended_required


def get_market_status_display() -> str:
    """Get formatted market status for display."""
    _, instruction, _ = get_current_market_session()
    return instruction
