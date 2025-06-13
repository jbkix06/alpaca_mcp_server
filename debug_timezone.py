#!/usr/bin/env python3
"""Debug timezone handling"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_timezone_conversion():
    """Test the timezone conversion function directly"""

    # Simulate an Alpaca timestamp in UTC (this is what Alpaca returns)
    utc_timestamp = "2025-06-12T20:48:00+00:00"

    print(f"Original timestamp: {utc_timestamp}")

    # Test the conversion function from the peak_trough_analysis_tool
    from alpaca_mcp_server.tools.peak_trough_analysis_tool import (
        convert_to_nyc_timezone,
    )

    converted = convert_to_nyc_timezone(utc_timestamp)
    print(f"Converted timestamp: {converted}")
    print(f"Type: {type(converted)}")

    if hasattr(converted, "strftime"):
        formatted = converted.strftime("%H:%M:%S %Z")
        print(f"Formatted: {formatted}")

    # Test different input formats
    print("\nTesting different input formats:")

    # ISO format with Z
    test1 = "2025-06-12T20:48:00Z"
    conv1 = convert_to_nyc_timezone(test1)
    print(f"ISO with Z: {test1} -> {conv1}")

    # ISO format without timezone
    test2 = "2025-06-12T20:48:00"
    conv2 = convert_to_nyc_timezone(test2)
    print(f"ISO no tz: {test2} -> {conv2}")

    # Test what happens when MCP serializes this
    print(f"\nString representation: {str(converted)}")
    print(f"ISO format: {converted.isoformat()}")


if __name__ == "__main__":
    test_timezone_conversion()
