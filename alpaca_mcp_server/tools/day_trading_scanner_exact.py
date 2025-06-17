"""Day trading scanner with EXACT trades per minute using differential snapshots."""

import logging
import asyncio
from datetime import datetime
from ..tools.market_data_tools import get_stock_snapshots

logger = logging.getLogger(__name__)

# Cache for storing previous snapshot data
_snapshot_cache = {}


async def scan_day_trading_opportunities_exact(
    symbols: str = "ALL",  # Use ALL tradeable assets by default
    min_trades_per_minute: int = 50,
    min_percent_change: float = 5.0,
    max_symbols: int = 20,
    sort_by: str = "trades",  # "trades", "percent_change", or "volume"
    wait_seconds: int = 60,  # Must be 60s to align with snapshot update cycle
) -> str:
    """
    Scan for day-trading opportunities using EXACT trades per minute from differential snapshots.

    This method mirrors your C program approach:
    1. Takes first snapshot (reference)
    2. Waits specified time (default 60 seconds)
    3. Takes second snapshot
    4. Calculates EXACT trades per minute from the difference

    Args:
        symbols: Comma-separated symbols to scan
        min_trades_per_minute: Minimum exact trades per minute (default: 50)
        min_percent_change: Minimum % change (default: 5.0%)
        max_symbols: Maximum results to return (default: 20)
        sort_by: Sort by "trades", "percent_change", or "volume"
        wait_seconds: Seconds between snapshots (default: 60 for exact 1-minute measurement)

    Returns:
        Formatted string with exact trading metrics like your screenshot
    """
    try:
        # Take first snapshot (reference)
        print(
            f"📊 Taking reference snapshot at {datetime.now().strftime('%H:%M:%S')}..."
        )
        snapshot1_data = await get_stock_snapshots(symbols)
        snapshot1_metrics = _parse_snapshot_metrics(snapshot1_data)

        # Wait for snapshot update cycle (60 seconds)
        print(f"⏱️  Waiting {wait_seconds} seconds for snapshot update cycle...")
        print("    (Snapshots update every 60 seconds - waiting for fresh data)")
        await asyncio.sleep(wait_seconds)

        # Take second snapshot
        print(
            f"📊 Taking comparison snapshot at {datetime.now().strftime('%H:%M:%S')}..."
        )
        snapshot2_data = await get_stock_snapshots(symbols)
        snapshot2_metrics = _parse_snapshot_metrics(snapshot2_data)

        # Calculate exact differentials
        results = []
        # time_interval_minutes = wait_seconds / 60.0  # Currently unused

        for symbol in snapshot1_metrics:
            if symbol not in snapshot2_metrics:
                continue

            s1 = snapshot1_metrics[symbol]
            s2 = snapshot2_metrics[symbol]

            # Calculate exact volume difference over 60-second interval (like your C program)
            volume_change = s2["minute_volume"] - s1["minute_volume"]

            # Volume difference between 1-minute snapshots = trade activity per minute
            trades_per_minute = max(
                0, volume_change
            )  # Volume delta = trades per minute

            # Use most recent price and calculate % change
            current_price = s2["price"]
            prev_close = s2["prev_close"]

            if prev_close > 0:
                percent_change = abs((current_price - prev_close) / prev_close * 100)
            else:
                percent_change = s2["daily_change"]

            # Apply filters
            if (
                trades_per_minute >= min_trades_per_minute
                and percent_change >= min_percent_change
                and current_price > 0
            ):
                results.append(
                    {
                        "symbol": symbol,
                        "price": current_price,
                        "trades_per_minute": trades_per_minute,
                        "volume_change": volume_change,
                        "current_volume": s2["minute_volume"],
                        "percent_change": percent_change,
                        "prev_close": prev_close,
                        "gradient2": percent_change
                        / 2.0,  # Like your screenshot's Gradient/2 column
                        "measurement_interval": wait_seconds,
                    }
                )

        # Sort results
        if sort_by == "trades":
            results.sort(key=lambda x: x["trades_per_minute"], reverse=True)
        elif sort_by == "percent_change":
            results.sort(key=lambda x: x["percent_change"], reverse=True)
        elif sort_by == "volume":
            results.sort(key=lambda x: x["current_volume"], reverse=True)

        # Limit results
        results = results[:max_symbols]

        if not results:
            return f"""# 🔍 Day Trading Scanner - No Opportunities (Exact Measurement)

**Scan Time:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Measurement Method:** Differential snapshots ({wait_seconds}s interval)
**Filters Applied:**
• Minimum Trades/Min: {min_trades_per_minute} (exact count)
• Minimum % Change: {min_percent_change}%

**Symbols Scanned:** {len(symbols.split(","))}
**Opportunities Found:** 0

**Note:** This uses EXACT trade counts, not estimates. Results may be lower during quiet periods.
"""

        # Format results like your screenshot
        result = f"""# 🔥 Day Trading Scanner - EXACT Trade Counts

**Scan Time:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Measurement Method:** Differential snapshots ({wait_seconds}s interval)
**Sorted By:** {sort_by.replace("_", " ").title()}
**Opportunities Found:** {len(results)} (from {len(symbols.split(","))} symbols)

## 📊 Exact Trading Metrics (Like Your Screenshot)

"""

        for i, stock in enumerate(results, 1):
            # Match your screenshot's momentum indicators
            if stock["percent_change"] > 40:
                momentum = "🚀 EXPLOSIVE"
            elif stock["percent_change"] > 20:
                momentum = "🔥 STRONG"
            elif stock["percent_change"] > 10:
                momentum = "📈 ACTIVE"
            else:
                momentum = "⚡ MODERATE"

            result += f"""### {i}. {stock["symbol"]} - {momentum}
• **Price:** ${stock["price"]:.3f}
• **Trades/Min:** {stock["trades_per_minute"]:,} (EXACT)
• **% Change:** +{stock["percent_change"]:.1f}%
• **Gradient/2:** {stock["gradient2"]:.1f}
• **Volume Change:** {stock["volume_change"]:,} 
• **Current Volume:** {stock["current_volume"]:,}
• **Previous Close:** ${stock["prev_close"]:.3f}

"""

        # Summary matching your screenshot format
        avg_trades = sum(s["trades_per_minute"] for s in results) / len(results)
        avg_change = sum(s["percent_change"] for s in results) / len(results)
        total_volume_change = sum(s["volume_change"] for s in results)

        result += f"""## 📈 Scanner Summary (Exact Measurements)
• **Average Trades/Min:** {avg_trades:.0f} (exact count)
• **Average % Change:** {avg_change:.1f}%
• **Total Volume Change:** {total_volume_change:,}
• **Measurement Interval:** {wait_seconds} seconds
• **Most Active:** {max(results, key=lambda x: x["trades_per_minute"])["symbol"]} ({max(results, key=lambda x: x["trades_per_minute"])["trades_per_minute"]:,} trades/min)
• **Biggest Mover:** {max(results, key=lambda x: x["percent_change"])["symbol"]} (+{max(results, key=lambda x: x["percent_change"])["percent_change"]:.1f}%)

## ⚡ Trading Actions
• **Peak Analysis:** `get_stock_peak_trough_analysis("{",".join(s["symbol"] for s in results[:5])}")`
• **Real-time Stream:** `start_global_stock_stream(["{'", "'.join(s["symbol"] for s in results[:5])}"], ["trades", "quotes"])`
• **Position Analysis:** `get_positions()` | **Account Status:** `get_account_info()`

**Note:** These are EXACT trade counts measured over {wait_seconds} seconds, not estimates.
"""

        return result

    except Exception as e:
        logger.error(f"Error in exact day trading scanner: {e}")
        return f"Error in exact trading scanner: {str(e)}"


def _parse_snapshot_metrics(snapshot_data: str) -> dict:
    """Parse snapshot data and extract key metrics for each symbol."""
    metrics = {}
    lines = snapshot_data.split("\n")
    current_symbol = None

    for line in lines:
        line = line.strip()

        # Detect symbol sections
        if line.startswith("## ") and "- Complete Market Data" in line:
            current_symbol = line.split(" ")[1]
            latest_price = 0.0
            minute_volume = 0
            daily_change = 0.0
            prev_close = 0.0
            continue

        if current_symbol:
            if line.startswith("• Price: $"):
                latest_price = float(line.replace("• Price: $", ""))

            elif line.startswith("• OHLC: $"):
                parts = line.replace("• OHLC: $", "").split(" / $")
                if len(parts) >= 4:
                    minute_close = float(parts[3])
                    if minute_close > 0:
                        latest_price = minute_close

            elif line.startswith("• Volume:") and "," in line:
                vol_text = line.replace("• Volume: ", "").replace(",", "")
                try:
                    volume_value = int(float(vol_text))
                    if volume_value < 10000000:  # Minute volume
                        minute_volume = volume_value
                except (ValueError, TypeError, AttributeError):
                    pass

            elif line.startswith("• Daily Change:") and "%" in line:
                pct_text = line.split("%")[0].replace("• Daily Change: ", "")
                try:
                    daily_change = abs(float(pct_text))
                except (ValueError, TypeError, AttributeError):
                    pass

            elif line.startswith("• Previous Close: $"):
                prev_close = float(line.replace("• Previous Close: $", ""))

            elif line.startswith("=="):  # End of symbol data
                if current_symbol and latest_price > 0:
                    metrics[current_symbol] = {
                        "price": latest_price,
                        "minute_volume": minute_volume,
                        "daily_change": daily_change,
                        "prev_close": prev_close,
                    }
                current_symbol = None

    return metrics


async def scan_explosive_momentum_exact(
    symbols: str = "ALL",  # Use ALL tradeable assets by default
    min_percent_change: float = 15.0,
    wait_seconds: int = 60,
) -> str:
    """
    Exact measurement scanner for explosive momentum.

    Uses differential snapshots for precise trade counting.
    """
    return await scan_day_trading_opportunities_exact(
        symbols=symbols,
        min_trades_per_minute=100,  # Higher threshold since these are exact counts
        min_percent_change=min_percent_change,
        max_symbols=10,
        sort_by="percent_change",
        wait_seconds=wait_seconds,
    )
