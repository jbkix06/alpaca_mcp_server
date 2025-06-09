"""Market data tools for Alpaca MCP Server."""

from typing import Optional, Union, List
from datetime import datetime, timedelta
import pytz
from ..config.settings import get_stock_historical_client

# Alpaca imports for market data
from alpaca.data.requests import (
    StockLatestQuoteRequest,
    StockBarsRequest,
    StockTradesRequest,
    StockLatestTradeRequest,
    StockLatestBarRequest,
)
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from alpaca.data.enums import DataFeed, Adjustment
from alpaca.common.enums import SupportedCurrencies


def get_smart_date_range():
    """
    Get a smart date range for intraday data that considers market hours and days.

    Returns:
        tuple: (start_date, end_date, is_market_open) in YYYY-MM-DD format
    """
    eastern = pytz.timezone("US/Eastern")
    now_et = datetime.now(eastern)

    # Check if today is a weekday (Monday=0, Sunday=6)
    is_weekday = now_et.weekday() < 5

    # Market hours: 9:30 AM - 4:00 PM ET (regular), 4:00 AM - 8:00 PM ET (extended)
    market_open = now_et.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = now_et.replace(hour=16, minute=0, second=0, microsecond=0)

    is_market_hours = market_open <= now_et <= market_close
    is_market_open = is_weekday and is_market_hours

    if is_weekday and now_et.hour >= 4:
        # Today, if it's a weekday and after 4 AM ET
        return now_et.strftime("%Y-%m-%d"), now_et.strftime("%Y-%m-%d"), is_market_open
    else:
        # Most recent trading day
        days_back = 1
        while days_back <= 7:  # Look back up to a week
            check_date = now_et - timedelta(days=days_back)
            if check_date.weekday() < 5:  # Found a weekday
                date_str = check_date.strftime("%Y-%m-%d")
                return date_str, date_str, False
            days_back += 1

        # Fallback: last Friday
        last_friday = now_et - timedelta(days=(now_et.weekday() + 3) % 7)
        date_str = last_friday.strftime("%Y-%m-%d")
        return date_str, date_str, False


async def get_stock_quote(symbol: str) -> str:
    """
    Retrieves and formats the latest quote for a stock.

    Args:
        symbol (str): Stock ticker symbol (e.g., AAPL, MSFT)

    Returns:
        str: Formatted string containing ask/bid prices, sizes, and timestamp
    """
    try:
        client = get_stock_historical_client()
        request_params = StockLatestQuoteRequest(symbol_or_symbols=symbol)
        quotes = client.get_stock_latest_quote(request_params)

        if symbol in quotes:
            quote = quotes[symbol]
            return f"""Latest Quote for {symbol}:
------------------------
Ask Price: ${quote.ask_price:.2f}
Bid Price: ${quote.bid_price:.2f}
Ask Size: {quote.ask_size}
Bid Size: {quote.bid_size}
Timestamp: {quote.timestamp}"""
        else:
            return f"No quote data found for {symbol}."

    except Exception as e:
        return f"Error fetching quote for {symbol}: {str(e)}"


async def get_stock_bars(symbol: str, days: int = 5) -> str:
    """
    Retrieves and formats historical price bars for a stock.

    Args:
        symbol (str): Stock ticker symbol (e.g., AAPL, MSFT)
        days (int): Number of trading days to look back (default: 5)

    Returns:
        str: Formatted string containing historical OHLCV data with daily changes
    """
    try:
        client = get_stock_historical_client()

        # Calculate start date
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days + 5)  # Add extra days for weekends

        request_params = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=TimeFrame.Day,
            start=start_date,
            end=end_date,
            limit=days,
        )

        bars_data = client.get_stock_bars(request_params)

        if symbol in bars_data and bars_data[symbol]:
            bars = bars_data[symbol]
            result = (
                f"Historical Price Bars for {symbol} (Last {len(bars)} trading days):\n"
            )
            result += "=" * 60 + "\n"

            for bar in bars:
                # Calculate daily change
                daily_change = (
                    (float(bar.close) - float(bar.open)) / float(bar.open)
                ) * 100
                change_indicator = (
                    "📈" if daily_change > 0 else "📉" if daily_change < 0 else "➡️"
                )

                result += f"""Date: {bar.timestamp.strftime('%Y-%m-%d')}
Open: ${float(bar.open):.2f}
High: ${float(bar.high):.2f}
Low: ${float(bar.low):.2f}
Close: ${float(bar.close):.2f}
Volume: {bar.volume:,}
Daily Change: {change_indicator} {daily_change:+.2f}%
------------------------------
"""
            return result
        else:
            return f"No bar data found for {symbol}."

    except Exception as e:
        return f"Error fetching bars for {symbol}: {str(e)}"


async def get_stock_bars_intraday(
    symbol: str,
    timeframe: str = "1Min",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 10000,
    adjustment: str = "raw",
    feed: str = "sip",
    currency: str = "USD",
    sort: str = "asc",
) -> str:
    """
    Retrieves comprehensive intraday historical bars with professional analysis.

    Args:
        symbol (str): Stock ticker symbol(s) - can be comma-separated (e.g., AAPL, MSFT or AAPL,MSFT,GOOGL)
        timeframe (str): Timeframe for bars (1Min, 5Min, 15Min, 30Min, 1Hour)
        start_date (Optional[str]): Start date in YYYY-MM-DD format (default: today)
        end_date (Optional[str]): End date in YYYY-MM-DD format (default: now)
        limit (int): Maximum number of bars to return per symbol (default: 10000)
        adjustment (str): Price adjustment type (raw, split, dividend, all)
        feed (str): Data feed (sip, iex, otc)
        currency (str): Currency for international symbols
        sort (str): Sort order (asc, desc)

    Returns:
        str: Comprehensive formatted analysis with professional insights
    """
    try:
        client = get_stock_historical_client()

        # Parse symbols - handle comma-separated list
        if "," in symbol:
            symbol_list = [s.strip().upper() for s in symbol.split(",")]
        else:
            symbol_list = [symbol.strip().upper()]

        # Parse timeframe
        timeframe_map = {
            "1Min": TimeFrame.Minute,
            "5Min": TimeFrame(5, TimeFrameUnit.Minute),
            "15Min": TimeFrame(15, TimeFrameUnit.Minute),
            "30Min": TimeFrame(30, TimeFrameUnit.Minute),
            "1Hour": TimeFrame.Hour,
            "1Day": TimeFrame.Day,
        }

        if timeframe not in timeframe_map:
            return f"Invalid timeframe: {timeframe}. Valid options: {list(timeframe_map.keys())}"

        tf = timeframe_map[timeframe]

        # Parse dates - the SDK requires timezone-aware datetime objects
        eastern = pytz.timezone("US/Eastern")

        if start_date and end_date:
            # User provided both dates
            start = eastern.localize(
                datetime.strptime(start_date, "%Y-%m-%d").replace(hour=4, minute=0)
            )
            end = eastern.localize(
                datetime.strptime(end_date, "%Y-%m-%d").replace(hour=20, minute=0)
            )
        elif start_date:
            # User provided start date only
            start = eastern.localize(
                datetime.strptime(start_date, "%Y-%m-%d").replace(hour=4, minute=0)
            )
            end = datetime.now(eastern)
        elif end_date:
            # User provided end date only
            end = eastern.localize(
                datetime.strptime(end_date, "%Y-%m-%d").replace(hour=20, minute=0)
            )
            # Default to same day
            start = eastern.localize(
                datetime.strptime(end_date, "%Y-%m-%d").replace(hour=4, minute=0)
            )
        else:
            # No dates provided - use smart defaults
            smart_start, smart_end, is_market_open = get_smart_date_range()
            start = eastern.localize(
                datetime.strptime(smart_start, "%Y-%m-%d").replace(hour=4, minute=0)
            )
            if is_market_open:
                # Market is open, use current time
                end = datetime.now(eastern)
            else:
                # Market closed, use end of trading day
                end = eastern.localize(
                    datetime.strptime(smart_end, "%Y-%m-%d").replace(hour=20, minute=0)
                )

        # Parse enums
        adjustment_enum = getattr(Adjustment, adjustment.upper(), Adjustment.RAW)
        feed_enum = getattr(DataFeed, feed.upper(), DataFeed.SIP)
        currency_enum = getattr(
            SupportedCurrencies, currency.upper(), SupportedCurrencies.USD
        )

        request_params = StockBarsRequest(
            symbol_or_symbols=symbol_list,
            timeframe=tf,
            start=start,
            end=end,
            limit=limit,
            adjustment=adjustment_enum,
            feed=feed_enum,
            currency=currency_enum,
        )

        bars_data = client.get_stock_bars(request_params)

        # Check if we have any data at all
        if not bars_data.data:
            return f"""No intraday data found for symbols {', '.join(symbol_list)} in timeframe {timeframe}.

Possible reasons:
• Market is closed or symbols traded on non-trading day (weekends/holidays)
• Invalid symbol(s) - check ticker spelling
• {feed.upper()} feed may have limited data for these symbols
• Time range may be outside available data period

Suggestions:
• Try a recent trading day (Monday-Friday)
• Use SIP feed for most comprehensive data
• Verify symbols are valid and actively traded
• Check if market was open during specified time range"""

        # For single symbol, provide detailed analysis
        if len(symbol_list) == 1:
            symbol = symbol_list[0]
            if symbol not in bars_data.data or not bars_data.data[symbol]:
                return f"""No intraday data found for {symbol} in timeframe {timeframe}.

Possible reasons:
• Market is closed or {symbol} traded on non-trading day (weekends/holidays)
• Invalid symbol - check ticker spelling for {symbol}
• {feed.upper()} feed may have limited data for {symbol}
• Time range may be outside available data period

Suggestions:
• Try a recent trading day (Monday-Friday)
• Use SIP feed for most comprehensive data
• Verify {symbol} is valid and actively traded
• Check if market was open during specified time range"""

            bars = list(bars_data.data[symbol])

            # Professional analysis starts here
            result = f"""# Professional Intraday Analysis: {symbol}
        
## Market Data Summary
Symbol: {symbol}
Timeframe: {timeframe}
Period: {start.strftime('%Y-%m-%d %H:%M')} to {end.strftime('%Y-%m-%d %H:%M')} ET
Total Bars: {len(bars)}
Data Feed: {feed.upper()}
Adjustment: {adjustment.title()}

"""

            if len(bars) < 2:
                return result + "Insufficient data for analysis."

            # Calculate key metrics
            first_bar = bars[0]
            last_bar = bars[-1]
            open_price = float(first_bar.open)
            close_price = float(last_bar.close)

            # Find high and low
            high_price = max(float(bar.high) for bar in bars)
            low_price = min(float(bar.low) for bar in bars)

            # Calculate returns
            total_return = ((close_price - open_price) / open_price) * 100

            # Volume analysis
            total_volume = sum(bar.volume for bar in bars)
            avg_volume = total_volume / len(bars)

            # Recent bars for momentum
            recent_bars = bars[-min(10, len(bars)) :]
            recent_prices = [float(bar.close) for bar in recent_bars]

            # Simple momentum calculation
            if len(recent_prices) >= 3:
                early_avg = sum(recent_prices[: len(recent_prices) // 2]) / (
                    len(recent_prices) // 2
                )
                late_avg = sum(recent_prices[len(recent_prices) // 2 :]) / (
                    len(recent_prices) - len(recent_prices) // 2
                )
                momentum = "BULLISH" if late_avg > early_avg else "BEARISH"
            else:
                momentum = "NEUTRAL"

            result += f"""## Key Metrics
Period Return: {total_return:+.2f}%
Opening Price: ${open_price:.2f}
Closing Price: ${close_price:.2f}
Session High: ${high_price:.2f}
Session Low: ${low_price:.2f}
Range: ${high_price - low_price:.2f} ({((high_price - low_price) / open_price) * 100:.2f}%)

## Volume Analysis
Total Volume: {total_volume:,} shares
Average Volume per Bar: {avg_volume:,.0f} shares
Volume Trend: {'Heavy' if total_volume > avg_volume * len(bars) * 1.5 else 'Normal' if total_volume > avg_volume * len(bars) * 0.8 else 'Light'}

## Technical Analysis
Short-term Momentum: {momentum}
Volatility: {'High' if (high_price - low_price) / open_price > 0.03 else 'Moderate' if (high_price - low_price) / open_price > 0.015 else 'Low'}
Price Action: {'Trending Up' if close_price > open_price else 'Trending Down' if close_price < open_price else 'Sideways'}

"""

            # Recent bars detail
            result += f"## Recent Price Action (Last {min(5, len(bars))} bars):\n"
            for bar in bars[-5:]:
                bar_change = (
                    (float(bar.close) - float(bar.open)) / float(bar.open)
                ) * 100
                trend_arrow = (
                    "🟢" if bar_change > 0.5 else "🔴" if bar_change < -0.5 else "🟡"
                )

                result += f"""{trend_arrow} {bar.timestamp.strftime('%H:%M')} | O:${float(bar.open):.2f} H:${float(bar.high):.2f} L:${float(bar.low):.2f} C:${float(bar.close):.2f} | Vol:{bar.volume:,} | {bar_change:+.2f}%
"""

            # Trading insights
            result += f"""
## Trading Insights

Support/Resistance Levels:
• Resistance: ${high_price:.2f} (session high)
• Support: ${low_price:.2f} (session low)

Volume Analysis:
• {'Strong institutional interest' if total_volume > avg_volume * len(bars) * 2 else 'Normal trading activity' if total_volume > avg_volume * len(bars) else 'Below average volume - limited interest'}

Momentum Signals:
• {momentum} momentum detected in recent bars
• {'Consider long positions on pullbacks' if momentum == 'BULLISH' and total_return > 1 else 'Monitor for reversal signals' if momentum == 'BEARISH' and total_return < -1 else 'Wait for clearer directional signals'}

Risk Considerations:
• Intraday volatility: {((high_price - low_price) / open_price) * 100:.2f}%
• {'High risk - tight stops recommended' if (high_price - low_price) / open_price > 0.03 else 'Moderate risk - normal position sizing' if (high_price - low_price) / open_price > 0.015 else 'Lower risk - suitable for larger positions'}

Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

            return result

        else:
            # Multiple symbols - provide summary analysis
            result = f"""# Intraday Analysis: Multiple Symbols
            
## Summary
Symbols: {', '.join(symbol_list)}
Timeframe: {timeframe}
Period: {start.strftime('%Y-%m-%d %H:%M')} to {end.strftime('%Y-%m-%d %H:%M')} ET
Data Feed: {feed.upper()}

"""

            # Analyze each symbol
            for symbol in symbol_list:
                if symbol not in bars_data.data or not bars_data.data[symbol]:
                    result += f"\n## {symbol} - No Data Available\n"
                    continue

                bars = list(bars_data.data[symbol])
                if len(bars) < 2:
                    result += f"\n## {symbol} - Insufficient Data\n"
                    continue

                # Calculate key metrics for each symbol
                first_bar = bars[0]
                last_bar = bars[-1]
                open_price = float(first_bar.open)
                close_price = float(last_bar.close)

                # Find high and low
                high_price = max(float(bar.high) for bar in bars)
                low_price = min(float(bar.low) for bar in bars)

                # Calculate returns
                total_return = ((close_price - open_price) / open_price) * 100

                # Volume analysis
                total_volume = sum(bar.volume for bar in bars)
                avg_volume_per_bar = total_volume / len(bars)

                # Recent momentum
                recent_bars = bars[-min(5, len(bars)) :]
                recent_change = (
                    (float(recent_bars[-1].close) - float(recent_bars[0].open))
                    / float(recent_bars[0].open)
                ) * 100

                result += f"""## {symbol}
                
### Performance
• Period Return: {total_return:+.2f}%
• Open: ${open_price:.2f} → Close: ${close_price:.2f}
• High: ${high_price:.2f} | Low: ${low_price:.2f}
• Range: ${high_price - low_price:.2f} ({((high_price - low_price) / open_price) * 100:.2f}%)

### Volume
• Total: {total_volume:,} shares
• Avg/Bar: {avg_volume_per_bar:,.0f} shares
• Bars: {len(bars)}

### Recent Action (Last {len(recent_bars)} bars)
• Momentum: {recent_change:+.2f}%
• Last Price: ${float(last_bar.close):.2f}
• Last Volume: {last_bar.volume:,}

---
"""

            # Add summary rankings
            result += "\n## Summary Rankings\n\n"

            # Collect metrics for ranking
            symbol_metrics = []
            for symbol in symbol_list:
                if symbol in bars_data.data and bars_data.data[symbol]:
                    bars = list(bars_data.data[symbol])
                    if len(bars) >= 2:
                        first_bar = bars[0]
                        last_bar = bars[-1]
                        total_return = (
                            (float(last_bar.close) - float(first_bar.open))
                            / float(first_bar.open)
                        ) * 100
                        total_volume = sum(bar.volume for bar in bars)
                        volatility = (
                            (
                                max(float(bar.high) for bar in bars)
                                - min(float(bar.low) for bar in bars)
                            )
                            / float(first_bar.open)
                            * 100
                        )

                        symbol_metrics.append(
                            {
                                "symbol": symbol,
                                "return": total_return,
                                "volume": total_volume,
                                "volatility": volatility,
                                "last_price": float(last_bar.close),
                            }
                        )

            # Sort by return
            symbol_metrics.sort(key=lambda x: x["return"], reverse=True)

            result += "### By Performance\n"
            for i, m in enumerate(symbol_metrics[:10], 1):
                result += f"{i}. {m['symbol']}: {m['return']:+.2f}% (${m['last_price']:.2f})\n"

            # Sort by volume
            symbol_metrics.sort(key=lambda x: x["volume"], reverse=True)

            result += "\n### By Volume\n"
            for i, m in enumerate(symbol_metrics[:10], 1):
                result += f"{i}. {m['symbol']}: {m['volume']:,} shares\n"

            # Sort by volatility
            symbol_metrics.sort(key=lambda x: x["volatility"], reverse=True)

            result += "\n### By Volatility\n"
            for i, m in enumerate(symbol_metrics[:10], 1):
                result += f"{i}. {m['symbol']}: {m['volatility']:.2f}% range\n"

            return result

    except Exception as e:
        return f"Error fetching intraday data: {str(e)}"


async def get_stock_snapshots(symbols: Union[str, List[str]]) -> str:
    """
    Get comprehensive market snapshots for one or more stocks.

    Args:
        symbols: Single symbol string or list of symbols

    Returns:
        str: Comprehensive market data with analysis
    """
    try:
        client = get_stock_historical_client()

        # Handle single symbol or list
        if isinstance(symbols, str):
            if "," in symbols:
                symbol_list = [s.strip().upper() for s in symbols.split(",")]
            else:
                symbol_list = [symbols.upper()]
        else:
            symbol_list = [s.upper() for s in symbols]

        # Get snapshot data using correct method
        from alpaca.data.requests import StockSnapshotRequest

        request_params = StockSnapshotRequest(symbol_or_symbols=symbol_list)
        snapshots = client.get_stock_snapshot(request_params)

        if not snapshots:
            return f"No snapshot data found for symbols: {', '.join(symbol_list)}"

        result = "# Market Snapshots\n"
        result += f"Symbols: {', '.join(symbol_list)}\n"
        result += f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        for symbol in symbol_list:
            if symbol in snapshots:
                snapshot = snapshots[symbol]

                # Extract data safely with correct attribute names
                latest_trade = getattr(snapshot, "latest_trade", None)
                latest_quote = getattr(snapshot, "latest_quote", None)
                minute_bar = getattr(snapshot, "minute_bar", None)
                daily_bar = getattr(snapshot, "daily_bar", None)
                previous_daily_bar = getattr(
                    snapshot, "previous_daily_bar", None
                )  # Correct attribute name

                result += f"""## {symbol} - Complete Market Data

### Latest Trade
"""
                if latest_trade:
                    result += f"""• Price: ${float(latest_trade.price):.2f}
• Size: {latest_trade.size:,} shares
• Time: {latest_trade.timestamp.strftime('%H:%M:%S')}
• Exchange: {getattr(latest_trade, 'exchange', 'N/A')}
"""
                else:
                    result += "• No recent trade data available\n"

                result += "\n### Latest Quote\n"
                if latest_quote:
                    spread = float(latest_quote.ask_price) - float(
                        latest_quote.bid_price
                    )
                    spread_pct = (spread / float(latest_quote.ask_price)) * 100

                    result += f"""• Bid: ${float(latest_quote.bid_price):.2f} (Size: {latest_quote.bid_size:,})
• Ask: ${float(latest_quote.ask_price):.2f} (Size: {latest_quote.ask_size:,})
• Spread: ${spread:.2f} ({spread_pct:.2f}%)
• Time: {latest_quote.timestamp.strftime('%H:%M:%S')}
"""
                else:
                    result += "• No current quote data available\n"

                result += "\n### Current Minute Bar\n"
                if minute_bar:
                    minute_change = (
                        (float(minute_bar.close) - float(minute_bar.open))
                        / float(minute_bar.open)
                    ) * 100
                    result += f"""• OHLC: ${float(minute_bar.open):.2f} / ${float(minute_bar.high):.2f} / ${float(minute_bar.low):.2f} / ${float(minute_bar.close):.2f}
• Volume: {minute_bar.volume:,}
• Change: {minute_change:+.2f}%
• Time: {minute_bar.timestamp.strftime('%H:%M')}
"""
                else:
                    result += "• No current minute bar data\n"

                result += "\n### Daily Performance\n"
                if daily_bar:
                    daily_range = float(daily_bar.high) - float(daily_bar.low)
                    daily_range_pct = (daily_range / float(daily_bar.open)) * 100

                    result += f"""• Today's OHLC: ${float(daily_bar.open):.2f} / ${float(daily_bar.high):.2f} / ${float(daily_bar.low):.2f} / ${float(daily_bar.close):.2f}
• Volume: {daily_bar.volume:,}
• Range: ${daily_range:.2f} ({daily_range_pct:.2f}%)
"""

                    # Calculate daily change if previous close is available
                    if previous_daily_bar:
                        daily_change = (
                            (float(daily_bar.close) - float(previous_daily_bar.close))
                            / float(previous_daily_bar.close)
                        ) * 100
                        result += f"""• Daily Change: {daily_change:+.2f}% (${float(daily_bar.close) - float(previous_daily_bar.close):+.2f})
• Previous Close: ${float(previous_daily_bar.close):.2f}
"""

                        # Add performance indicators
                        result += "\n### Performance Indicators\n"
                        if daily_change > 3:
                            result += (
                                "• Strong Upward Movement - Consider momentum plays\n"
                            )
                        elif daily_change > 1:
                            result += "• Positive Momentum - Watch for continuation\n"
                        elif daily_change < -3:
                            result += (
                                "• Significant Decline - Risk management critical\n"
                            )
                        elif daily_change < -1:
                            result += "• Negative Pressure - Monitor for reversal\n"
                        else:
                            result += "• Consolidating - Await directional break\n"
                    else:
                        # Calculate intraday change without previous close
                        intraday_change = (
                            (float(daily_bar.close) - float(daily_bar.open))
                            / float(daily_bar.open)
                        ) * 100
                        result += f"""• Intraday Change: {intraday_change:+.2f}%
• Previous Close: Not available
"""

                        result += "\n### Performance Indicators\n"
                        if intraday_change > 2:
                            result += "• Strong Intraday Performance\n"
                        elif intraday_change > 0.5:
                            result += "• Positive Intraday Movement\n"
                        elif intraday_change < -2:
                            result += "• Weak Intraday Performance\n"
                        elif intraday_change < -0.5:
                            result += "• Negative Intraday Movement\n"
                        else:
                            result += "• Neutral Intraday Action\n"

                else:
                    result += "• Daily bar data not available\n"

                result += "\n" + "=" * 50 + "\n"

            else:
                result += f"## {symbol} - No Data Available\n"
                result += "• Symbol may be invalid or data unavailable\n\n"

        return result

    except Exception as e:
        return f"Error fetching snapshots: {str(e)}"


async def get_stock_trades(
    symbol: str, days: int = 5, limit: Optional[int] = None
) -> str:
    """
    Retrieves historical trades for a stock.

    Args:
        symbol (str): Stock ticker symbol
        days (int): Number of days to look back (default: 5)
        limit (Optional[int]): Maximum number of trades to return

    Returns:
        str: Formatted string containing recent trades
    """
    try:
        client = get_stock_historical_client()

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        request_params = StockTradesRequest(
            symbol_or_symbols=symbol, start=start_date, end=end_date, limit=limit or 100
        )

        trades_data = client.get_stock_trades(request_params)

        if symbol in trades_data and trades_data[symbol]:
            trades = list(trades_data[symbol])

            result = f"Recent Trades for {symbol} (Last {len(trades)} trades):\n"
            result += "=" * 50 + "\n"

            for trade in trades[-10:]:  # Show last 10 trades
                result += f"""Time: {trade.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
Price: ${float(trade.price):.2f}
Size: {trade.size:,} shares
Exchange: {getattr(trade, 'exchange', 'N/A')}
------------------------------
"""
            return result
        else:
            return f"No trade data found for {symbol}."

    except Exception as e:
        return f"Error fetching trades for {symbol}: {str(e)}"


async def get_stock_latest_trade(symbol: str) -> str:
    """
    Gets the latest trade for a stock.

    Args:
        symbol (str): Stock ticker symbol

    Returns:
        str: Formatted string containing the latest trade information
    """
    try:
        client = get_stock_historical_client()
        request_params = StockLatestTradeRequest(symbol_or_symbols=symbol)
        trades = client.get_stock_latest_trade(request_params)

        if symbol in trades:
            trade = trades[symbol]
            return f"""Latest Trade for {symbol}:
-----------------------
Price: ${float(trade.price):.2f}
Size: {trade.size:,} shares
Time: {trade.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
Exchange: {getattr(trade, 'exchange', 'N/A')}"""
        else:
            return f"No recent trade data found for {symbol}."

    except Exception as e:
        return f"Error fetching latest trade for {symbol}: {str(e)}"


async def get_stock_latest_bar(symbol: str) -> str:
    """
    Gets the latest minute bar for a stock.

    Args:
        symbol (str): Stock ticker symbol

    Returns:
        str: Formatted string containing the latest bar information
    """
    try:
        client = get_stock_historical_client()
        request_params = StockLatestBarRequest(symbol_or_symbols=symbol)
        bars = client.get_stock_latest_bar(request_params)

        if symbol in bars:
            bar = bars[symbol]
            bar_change = ((float(bar.close) - float(bar.open)) / float(bar.open)) * 100

            return f"""Latest Minute Bar for {symbol}:
-----------------------------
Time: {bar.timestamp.strftime('%Y-%m-%d %H:%M')}
Open: ${float(bar.open):.2f}
High: ${float(bar.high):.2f}
Low: ${float(bar.low):.2f}
Close: ${float(bar.close):.2f}
Volume: {bar.volume:,}
Change: {bar_change:+.2f}%"""
        else:
            return f"No recent bar data found for {symbol}."

    except Exception as e:
        return f"Error fetching latest bar for {symbol}: {str(e)}"
