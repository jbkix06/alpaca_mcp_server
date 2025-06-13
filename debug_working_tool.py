#!/usr/bin/env python3
"""Debug the working intraday tool to understand its data structure."""

import asyncio
from alpaca_mcp_server.tools.market_data_tools import get_stock_bars_intraday


async def debug_working_tool():
    """Debug what the working tool actually returns."""

    print("=== Testing Working Intraday Tool ===")

    # Call the working tool
    result = await get_stock_bars_intraday(symbol="SPY", timeframe="1Min", limit=50)

    print("Result type:", type(result))
    print("Result length:", len(result))
    print("\nFirst 500 characters:")
    print(result[:500])
    print("\n" + "=" * 50)

    # Check if it mentions specific price values we can extract
    lines = result.split("\n")
    print("Number of lines:", len(lines))

    # Look for price data patterns
    price_lines = []
    for line in lines:
        if "$" in line and (
            "Open:" in line or "Close:" in line or "High:" in line or "Low:" in line
        ):
            price_lines.append(line.strip())

    print(f"\nFound {len(price_lines)} price data lines:")
    for line in price_lines[-10:]:  # Show last 10
        print(f"  {line}")


if __name__ == "__main__":
    asyncio.run(debug_working_tool())
