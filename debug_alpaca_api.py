#!/usr/bin/env python3
"""Debug Alpaca API timestamp format"""

import os
import sys
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()


def test_alpaca_api_format():
    """Test what format timestamps come back in from Alpaca API"""

    api_key = os.getenv("APCA_API_KEY_ID") or os.getenv("ALPACA_API_KEY")
    api_secret = os.getenv("APCA_API_SECRET_KEY") or os.getenv("ALPACA_SECRET_KEY")

    if not api_key or not api_secret:
        print("Missing API credentials")
        return

    session = requests.Session()
    session.headers.update(
        {"APCA-API-KEY-ID": api_key, "APCA-API-SECRET-KEY": api_secret}
    )

    # Get recent bars for AAPL
    now = datetime.utcnow()
    start_date = (now - timedelta(days=1)).strftime("%Y-%m-%d")
    end_date = now.strftime("%Y-%m-%d")

    url = "https://data.alpaca.markets/v2/stocks/bars"
    params = {
        "symbols": "AAPL",
        "timeframe": "1Min",
        "start": start_date,
        "end": end_date,
        "limit": 5,
        "adjustment": "split",
        "feed": "sip",
        "sort": "desc",  # Get recent bars
    }

    try:
        response = session.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        print("Raw API Response (first few bars):")
        print("-" * 60)

        if "bars" in data and "AAPL" in data["bars"]:
            for i, bar in enumerate(data["bars"]["AAPL"][:3]):
                print(f"Bar {i+1}:")
                print(f"  Timestamp (t): {bar['t']} (type: {type(bar['t'])})")
                print(f"  Close (c): {bar['c']}")
                print(f"  Volume (v): {bar['v']}")
                print()

                # Test timezone conversion on this timestamp
                print("  Testing timezone conversion:")
                try:
                    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
                    from alpaca_mcp_server.tools.peak_trough_analysis_tool import (
                        convert_to_nyc_timezone,
                    )

                    converted = convert_to_nyc_timezone(bar["t"])
                    print(f"    Original: {bar['t']}")
                    print(f"    Converted: {converted}")
                    print(f"    Formatted: {converted.strftime('%H:%M:%S %Z')}")
                except Exception as e:
                    print(f"    Conversion error: {e}")
                print()
        else:
            print("No bars found in response")
            print(f"Full response: {data}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_alpaca_api_format()
