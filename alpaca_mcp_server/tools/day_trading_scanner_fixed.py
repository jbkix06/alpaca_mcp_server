"""Fixed day trading scanner with corrected parsing logic."""

import logging
from datetime import datetime
from ..tools.market_data_tools import get_stock_snapshots

logger = logging.getLogger(__name__)


async def scan_day_trading_opportunities(
    symbols: str = "SPY,QQQ,IWM,AAPL,MSFT,NVDA,TSLA,AMC,GME,PLTR,SOFI,RIVN,LCID,NIO,XPEV,BABA,META,GOOGL,AMZN,NFLX",
    min_trades_per_minute: int = 50,
    min_percent_change: float = 5.0,
    max_symbols: int = 20,
    sort_by: str = "trades",  # "trades", "percent_change", or "volume"
) -> str:
    """
    Scan for active day-trading opportunities using real-time market snapshots.

    Focused on the two key metrics from stock_analyzer.c:
    1. Trades per minute (activity/liquidity indicator)
    2. Percent change (momentum indicator)

    Args:
        symbols: Comma-separated symbols to scan (default: popular day-trading stocks)
        min_trades_per_minute: Minimum trades in current minute bar (default: 50)
        min_percent_change: Minimum absolute % change from reference (default: 5.0%)
        max_symbols: Maximum results to return (default: 20)
        sort_by: Sort results by "trades", "percent_change", or "volume"

    Returns:
        Formatted string with top day-trading opportunities ranked by activity
    """
    try:
        # Get real-time snapshots for all symbols
        snapshot_data = await get_stock_snapshots(symbols)

        # Parse snapshot data to extract key metrics
        opportunities = []

        # Split by symbol sections using "## " as delimiter
        sections = snapshot_data.split("## ")

        for section in sections[1:]:  # Skip header
            lines = section.strip().split("\n")
            if not lines:
                continue

            # Extract symbol from first line
            symbol = lines[0].split(" ")[0].strip()
            print(f"Processing {symbol}...")

            # Initialize all metrics
            latest_trade_price = 0.0
            minute_bar_close = 0.0
            minute_volume = 0
            daily_change_pct = 0.0
            prev_close = 0.0
            daily_high = 0.0
            daily_low = 0.0

            # Parse line by line with simple string matching
            for line in lines:
                line = line.strip()

                # Latest Trade Price: • Price: $140.95
                if line.startswith("• Price: $"):
                    latest_trade_price = float(line.replace("• Price: $", ""))
                    print(f"  {symbol}: Latest trade price = ${latest_trade_price}")

                # Minute Bar OHLC: • OHLC: $140.88 / $140.94 / $140.88 / $140.92
                elif line.startswith("• OHLC: $"):
                    parts = line.replace("• OHLC: $", "").split(" / $")
                    if len(parts) >= 4:
                        minute_bar_close = float(parts[3])
                        print(f"  {symbol}: Minute bar close = ${minute_bar_close}")

                # Minute Volume: • Volume: 8,837.0
                elif line.startswith("• Volume:") and "," in line:
                    vol_text = line.replace("• Volume: ", "").replace(",", "")
                    try:
                        minute_volume = int(float(vol_text))
                        print(f"  {symbol}: Minute volume = {minute_volume:,}")
                    except Exception as e:
                        print(f"  {symbol}: Volume parse error: {e}")

                # Daily Change: • Daily Change: -0.78% ($-1.13)
                elif line.startswith("• Daily Change:") and "%" in line:
                    pct_text = line.split("%")[0].replace("• Daily Change: ", "")
                    try:
                        daily_change_pct = abs(float(pct_text))
                        print(f"  {symbol}: Daily change = {daily_change_pct}%")
                    except Exception as e:
                        print(f"  {symbol}: Daily change parse error: {e}")

                # Previous Close: • Previous Close: $143.96
                elif line.startswith("• Previous Close: $"):
                    prev_close = float(line.replace("• Previous Close: $", ""))
                    print(f"  {symbol}: Previous close = ${prev_close}")

                # Daily OHLC: • Today's OHLC: $144.61 / $144.99 / $141.87 / $142.83
                elif line.startswith("• Today's OHLC: $"):
                    parts = line.replace("• Today's OHLC: $", "").split(" / $")
                    if len(parts) >= 4:
                        daily_high = float(parts[1])
                        daily_low = float(parts[2])
                        print(f"  {symbol}: Daily range = ${daily_low} - ${daily_high}")

            # Determine current price (prefer minute bar close, fallback to latest trade)
            current_price = (
                minute_bar_close if minute_bar_close > 0 else latest_trade_price
            )

            # Calculate realistic trades per minute estimate
            if minute_volume > 0 and current_price > 0:
                # Estimate average shares per trade based on stock price
                if current_price > 100:  # High-priced stocks (NVDA, GOOGL, etc.)
                    avg_shares_per_trade = 100
                elif current_price > 20:  # Mid-priced stocks (AAPL, MSFT, etc.)
                    avg_shares_per_trade = 150
                elif current_price > 5:  # Lower-priced stocks
                    avg_shares_per_trade = 300
                else:  # Penny stocks
                    avg_shares_per_trade = 1000

                trades_per_minute = max(1, minute_volume // avg_shares_per_trade)
            else:
                trades_per_minute = 0

            # Calculate percent change (use daily change or calculate from prev close)
            percent_change = daily_change_pct
            if current_price > 0 and prev_close > 0:
                calculated_change = abs((current_price - prev_close) / prev_close * 100)
                percent_change = max(percent_change, calculated_change)

            print(
                f"  {symbol}: FINAL - Price=${current_price:.2f}, Volume={minute_volume:,}, Trades_est={trades_per_minute}, Change={percent_change:.2f}%"
            )

            # Apply filters and add to opportunities
            if (
                trades_per_minute >= min_trades_per_minute
                and percent_change >= min_percent_change
                and current_price > 0
                and minute_volume > 0
            ):
                opportunities.append(
                    {
                        "symbol": symbol,
                        "price": current_price,
                        "trades_per_minute": trades_per_minute,
                        "volume": minute_volume,
                        "percent_change": percent_change,
                        "daily_high": daily_high,
                        "daily_low": daily_low,
                        "prev_close": prev_close,
                        "breakout_ratio": (
                            (current_price / daily_high * 100) if daily_high > 0 else 0
                        ),
                    }
                )
                print(f"  {symbol}: ADDED TO OPPORTUNITIES!")
            else:
                print(
                    f"  {symbol}: FILTERED OUT - trades:{trades_per_minute}>={min_trades_per_minute}? {trades_per_minute >= min_trades_per_minute}, change:{percent_change:.2f}>={min_percent_change}? {percent_change >= min_percent_change}"
                )

        # Sort opportunities
        if sort_by == "trades":
            opportunities.sort(key=lambda x: x["trades_per_minute"], reverse=True)
        elif sort_by == "percent_change":
            opportunities.sort(key=lambda x: x["percent_change"], reverse=True)
        elif sort_by == "volume":
            opportunities.sort(key=lambda x: x["volume"], reverse=True)

        # Limit results
        opportunities = opportunities[:max_symbols]

        if not opportunities:
            return f"""# 🔍 Day Trading Scanner - No Opportunities Found

**Scan Time:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Filters Applied:**
• Minimum Trades/Min: {min_trades_per_minute}
• Minimum % Change: {min_percent_change}%

**Symbols Scanned:** {len(symbols.split(","))}
**Opportunities Found:** 0

**Suggestions:**
• Lower min_trades_per_minute threshold (try 10-25)
• Reduce min_percent_change requirement (try 1-3%)
• Scan during more active market hours
• Try different symbol universe
"""

        # Format results
        result = f"""# 🔥 Day Trading Scanner Results

**Scan Time:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Sorted By:** {sort_by.replace("_", " ").title()}
**Opportunities Found:** {len(opportunities)} (from {len(symbols.split(","))} symbols)

## 📊 Top Opportunities

"""

        for i, opp in enumerate(opportunities, 1):
            # Determine momentum indicator
            if opp["percent_change"] > 10:
                momentum = "🚀 EXPLOSIVE"
            elif opp["percent_change"] > 7:
                momentum = "🔥 STRONG"
            elif opp["percent_change"] > 5:
                momentum = "📈 ACTIVE"
            else:
                momentum = "⚡ MODERATE"

            # Breakout indicator
            breakout_status = ""
            if opp["breakout_ratio"] > 95:
                breakout_status = " | 🎯 NEAR HIGH"
            elif opp["breakout_ratio"] > 90:
                breakout_status = " | 📊 BREAKOUT"

            result += f"""### {i}. {opp["symbol"]} - {momentum}{breakout_status}
• **Price:** ${opp["price"]:.2f}
• **Trades/Min:** {opp["trades_per_minute"]:,} 
• **% Change:** {opp["percent_change"]:+.1f}%
• **Volume:** {opp["volume"]:,}
• **Range:** ${opp["daily_low"]:.2f} - ${opp["daily_high"]:.2f}
• **Prev Close:** ${opp["prev_close"]:.2f}

"""

        # Add summary statistics
        avg_trades = sum(o["trades_per_minute"] for o in opportunities) / len(
            opportunities
        )
        avg_change = sum(o["percent_change"] for o in opportunities) / len(
            opportunities
        )
        total_volume = sum(o["volume"] for o in opportunities)

        result += f"""## 📈 Scanner Summary
• **Average Trades/Min:** {avg_trades:.0f}
• **Average % Change:** {avg_change:.1f}%
• **Total Volume:** {total_volume:,}
• **Most Active:** {opportunities[0]["symbol"] if sort_by == "trades" else "N/A"}
• **Biggest Mover:** {max(opportunities, key=lambda x: x["percent_change"])["symbol"]}

## ⚡ Quick Actions
• **Peak Analysis:** `get_stock_peak_trough_analysis("{",".join(o["symbol"] for o in opportunities[:5])}")`
• **Real-time Stream:** `start_global_stock_stream(["{'", "'.join(o["symbol"] for o in opportunities[:10])}"], ["trades", "quotes"])`
• **Detailed Snapshots:** `get_stock_snapshots("{",".join(o["symbol"] for o in opportunities[:5])}")`
"""

        return result

    except Exception as e:
        logger.error(f"Error in day trading scanner: {e}")
        return f"Error scanning for day trading opportunities: {str(e)}"


async def scan_explosive_momentum(
    symbols: str = "CVAC,CGTL,GNLN,NEHC,SOUN,RIOT,MARA,COIN,HOOD,RBLX",
    min_percent_change: float = 15.0,
) -> str:
    """
    Quick scanner for explosive momentum moves like NEHC.

    Focused on extreme % changes and volume spikes.
    """
    return await scan_day_trading_opportunities(
        symbols=symbols,
        min_trades_per_minute=10,  # Lower threshold for explosive moves
        min_percent_change=min_percent_change,
        max_symbols=10,
        sort_by="percent_change",
    )
