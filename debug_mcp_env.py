#!/usr/bin/env python3
"""Debug MCP server environment"""

import os
import sys
from datetime import datetime
import pytz

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp.server.fastmcp import FastMCP

# Create a minimal MCP server for testing
mcp = FastMCP("debug-server")


@mcp.tool()
async def debug_timezone_info() -> str:
    """Debug timezone environment in MCP server"""
    result = []

    # Check current timezone environment
    result.append(f"TZ environment variable: {os.environ.get('TZ', 'Not set')}")
    result.append(f"System timezone (datetime.now()): {datetime.now()}")
    result.append(f"UTC time (datetime.utcnow()): {datetime.utcnow()}")

    # Test NYC timezone conversion
    utc_now = datetime.utcnow().replace(tzinfo=pytz.UTC)
    nyc_tz = pytz.timezone("America/New_York")
    nyc_now = utc_now.astimezone(nyc_tz)
    result.append(f"UTC with tzinfo: {utc_now}")
    result.append(f"NYC timezone: {nyc_now}")
    result.append(f"NYC formatted: {nyc_now.strftime('%H:%M:%S %Z')}")

    # Test the conversion function
    from alpaca_mcp_server.tools.peak_trough_analysis_tool import (
        convert_to_nyc_timezone,
    )

    test_timestamp = "2025-06-12T20:48:00Z"
    converted = convert_to_nyc_timezone(test_timestamp)
    result.append(f"Test conversion: {test_timestamp} -> {converted}")
    result.append(f"Conversion type: {type(converted)}")
    if hasattr(converted, "strftime"):
        result.append(f"Conversion formatted: {converted.strftime('%H:%M:%S %Z')}")

    return "\n".join(result)


if __name__ == "__main__":
    # Run the server in debug mode
    print("Starting debug MCP server...")
    print("This will show timezone information when the tool is called")
    mcp.run()
