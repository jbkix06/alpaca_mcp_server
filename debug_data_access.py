#!/usr/bin/env python3
"""Debug the difference between data access methods."""

import asyncio
from alpaca_mcp_server.config.settings import get_stock_historical_client
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.data.enums import DataFeed
from datetime import datetime
import pytz


async def debug_data_access():
    """Test different ways to access the bar data."""

    client = get_stock_historical_client()
    eastern = pytz.timezone("US/Eastern")

    # Use the exact same parameters as the working tool
    start = eastern.localize(
        datetime.strptime(
            datetime.now(eastern).strftime("%Y-%m-%d"), "%Y-%m-%d"
        ).replace(hour=4, minute=0)
    )
    end = datetime.now(eastern)

    print(f"Using date range: {start} to {end}")

    request_params = StockBarsRequest(
        symbol_or_symbols="SPY",
        timeframe=TimeFrame.Minute,
        start=start,
        end=end,
        limit=50,
        adjustment="raw",
        feed=DataFeed.SIP,
        currency="USD",
    )

    print("Making API call...")
    bars_data = client.get_stock_bars(request_params)

    print(f"bars_data type: {type(bars_data)}")
    print(f"bars_data attributes: {dir(bars_data)}")

    # Test direct access (what I was doing wrong)
    print("\n=== Testing Direct Access (bars_data['SPY']) ===")
    try:
        direct_bars = bars_data["SPY"]
        print(f"Direct access result: {len(list(direct_bars))} bars")
    except Exception as e:
        print(f"Direct access failed: {e}")

    # Test .data access (what the working tool does)
    print("\n=== Testing .data Access (bars_data.data['SPY']) ===")
    try:
        if hasattr(bars_data, "data"):
            print("✓ bars_data has .data attribute")
            print(f"bars_data.data type: {type(bars_data.data)}")
            print(
                f"bars_data.data keys: {list(bars_data.data.keys()) if bars_data.data else 'None'}"
            )

            if bars_data.data and "SPY" in bars_data.data:
                data_bars = list(bars_data.data["SPY"])
                print(f"✓ SUCCESS: .data access result: {len(data_bars)} bars")

                if data_bars:
                    print(
                        f"First bar: {data_bars[0].timestamp} - Close: ${data_bars[0].close}"
                    )
                    print(
                        f"Last bar: {data_bars[-1].timestamp} - Close: ${data_bars[-1].close}"
                    )
            else:
                print("❌ No SPY data in bars_data.data")
        else:
            print("❌ bars_data has no .data attribute")
    except Exception as e:
        print(f"❌ .data access failed: {e}")

    # Test other possible attributes
    print("\n=== Other Attributes ===")
    for attr in dir(bars_data):
        if not attr.startswith("_"):
            try:
                value = getattr(bars_data, attr)
                print(f"{attr}: {type(value)}")
            except:
                print(f"{attr}: <error accessing>")


if __name__ == "__main__":
    asyncio.run(debug_data_access())
