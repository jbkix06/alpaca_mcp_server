#!/usr/bin/env python3
"""Debug script to test market momentum resource directly."""

import asyncio
from datetime import datetime, timedelta
import pytz
from alpaca_mcp_server.config.settings import get_stock_historical_client
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit


async def debug_market_momentum():
    """Test the market momentum data fetching logic directly."""

    symbol = "SPY"
    timeframe_minutes = 1
    analysis_hours = 2

    print(f"Testing market momentum for {symbol}")
    print(f"Timeframe: {timeframe_minutes} minutes")
    print(f"Analysis hours: {analysis_hours}")
    print("-" * 50)

    try:
        # Get the client
        data_client = get_stock_historical_client()
        print("✓ Got historical data client")

        # Calculate time range - PROBLEM IS HERE
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=analysis_hours)

        print(f"Start time (UTC): {start_time}")
        print(f"End time (UTC): {end_time}")

        # Convert to Eastern time for comparison
        eastern = pytz.timezone("US/Eastern")
        end_time_et = end_time.replace(tzinfo=pytz.UTC).astimezone(eastern)
        start_time_et = start_time.replace(tzinfo=pytz.UTC).astimezone(eastern)

        print(f"Start time (ET): {start_time_et}")
        print(f"End time (ET): {end_time_et}")

        # Check if this is during market hours
        is_weekday = end_time_et.weekday() < 5
        is_market_hours = 9 <= end_time_et.hour <= 16
        print(f"Is weekday: {is_weekday}")
        print(f"Is market hours (9-16 ET): {is_market_hours}")
        print(f"Current ET hour: {end_time_et.hour}")

        # Map minutes to TimeFrame
        if timeframe_minutes == 1:
            timeframe = TimeFrame.Minute
        elif timeframe_minutes == 5:
            timeframe = TimeFrame(5, TimeFrameUnit.Minute)
        elif timeframe_minutes == 15:
            timeframe = TimeFrame(15, TimeFrameUnit.Minute)
        elif timeframe_minutes == 30:
            timeframe = TimeFrame(30, TimeFrameUnit.Minute)
        elif timeframe_minutes == 60:
            timeframe = TimeFrame.Hour
        else:
            timeframe = TimeFrame.Minute

        print(f"Using timeframe: {timeframe}")

        # Create the request
        request = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=timeframe,
            start=start_time,
            end=end_time,
        )

        print("Making API request...")

        # Make the API call
        bars = data_client.get_stock_bars(request)
        print("✓ API call successful")

        # Check the response
        symbol_bars = list(bars[symbol]) if symbol in bars else []
        print(f"Bars received for {symbol}: {len(symbol_bars)}")

        if len(symbol_bars) > 0:
            print(f"First bar timestamp: {symbol_bars[0].timestamp}")
            print(f"Last bar timestamp: {symbol_bars[-1].timestamp}")
            print(f"First bar close: ${symbol_bars[0].close}")
            print(f"Last bar close: ${symbol_bars[-1].close}")
        else:
            print("❌ NO BARS RECEIVED!")
            print("This is the root cause of the market momentum error.")

            # Let's try a different approach - use market-aware date range
            print("\n" + "=" * 50)
            print("TRYING MARKET-AWARE DATE RANGE...")

            # Use Eastern timezone for market-aware calculations
            now_et = datetime.now(eastern)
            print(f"Current ET time: {now_et}")

            # If market is closed, go back to last trading day
            if not (
                is_weekday and 4 <= now_et.hour <= 20
            ):  # Extended hours 4 AM - 8 PM ET
                print("Market appears closed, finding last trading day...")
                days_back = 1
                while days_back <= 7:
                    check_date = now_et - timedelta(days=days_back)
                    if check_date.weekday() < 5:  # Found a weekday
                        print(f"Using {check_date.strftime('%Y-%m-%d')} as trading day")
                        # Set times for that trading day
                        start_time_et = check_date.replace(
                            hour=9, minute=30, second=0, microsecond=0
                        )
                        end_time_et = check_date.replace(
                            hour=16, minute=0, second=0, microsecond=0
                        )
                        break
                    days_back += 1
            else:
                # Market is open or in extended hours
                if now_et.hour < 9:
                    # Before market open, use yesterday's data
                    yesterday = now_et - timedelta(days=1)
                    while yesterday.weekday() >= 5:  # Skip weekends
                        yesterday -= timedelta(days=1)
                    start_time_et = yesterday.replace(
                        hour=14, minute=0, second=0, microsecond=0
                    )  # Last 2 hours of yesterday
                    end_time_et = yesterday.replace(
                        hour=16, minute=0, second=0, microsecond=0
                    )
                else:
                    # During or after market hours, use today's data
                    end_time_et = now_et
                    start_time_et = now_et - timedelta(hours=analysis_hours)
                    # But don't go before market open
                    market_open = now_et.replace(
                        hour=9, minute=30, second=0, microsecond=0
                    )
                    if start_time_et < market_open:
                        start_time_et = market_open

            # Convert back to UTC for API call
            start_time_utc = start_time_et.astimezone(pytz.UTC).replace(tzinfo=None)
            end_time_utc = end_time_et.astimezone(pytz.UTC).replace(tzinfo=None)

            print(f"New start time (ET): {start_time_et}")
            print(f"New end time (ET): {end_time_et}")
            print(f"New start time (UTC): {start_time_utc}")
            print(f"New end time (UTC): {end_time_utc}")

            # Try the new request
            request2 = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=timeframe,
                start=start_time_utc,
                end=end_time_utc,
            )

            print("Making second API request with market-aware times...")
            bars2 = data_client.get_stock_bars(request2)
            symbol_bars2 = list(bars2[symbol]) if symbol in bars2 else []
            print(f"Bars received with market-aware timing: {len(symbol_bars2)}")

            if len(symbol_bars2) > 0:
                print(f"✓ SUCCESS! First bar: {symbol_bars2[0].timestamp}")
                print(f"✓ SUCCESS! Last bar: {symbol_bars2[-1].timestamp}")
                print(f"✓ SUCCESS! First bar close: ${symbol_bars2[0].close}")
                print(f"✓ SUCCESS! Last bar close: ${symbol_bars2[-1].close}")
            else:
                print("❌ Still no bars - there may be an API or connectivity issue")

    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(debug_market_momentum())
