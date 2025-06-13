"""Differential trade scanner - exact trade counting like the C program."""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Optional
import os
import requests

logger = logging.getLogger(__name__)

# Global cache for storing previous snapshot data (like C program's cache)
_trade_cache: Dict[str, Dict] = {}
_scanner_task: Optional[asyncio.Task] = None
_scanner_running = False
_latest_results: Dict = {}


async def start_differential_trade_scanner(
    symbols: str = "NEHC,HCTI,GNLN,SOAR,CGTL,CVAC,KLTO,GTI,IPA,YHC,IXHL,ORCL,NIVF,ZENA,VOYG,UVIX,QUBT,TSLA,AAPL,MSFT,NVDA,AMC,GME,PLTR,RIVN,LCID,NKLA,MULN,AIHS,HSDT,PROG,ATER,IRNT,EXPR,CLOV,WISH,AFRM,UPST,DKNG,SKLZ,ROOT,LMND,GOEV,RIDE,WKHS,BLNK,CHPT,SENS,BNGO,OCGN",
    min_trades_per_minute: int = 50,
    min_percent_change: float = 5.0,
    update_interval: int = 60,
    max_symbols: int = 50,
) -> str:
    """
    Start the differential trade scanner in the background.

    This mirrors the C program functionality:
    1. Takes snapshots every 60 seconds
    2. Calculates exact trade count differences
    3. Caches previous values for comparison
    4. Runs continuously in background

    Args:
        symbols: Comma-separated symbols to monitor
        min_trades_per_minute: Minimum trade count difference to include
        min_percent_change: Minimum % change to include
        update_interval: Seconds between scans (default: 60)
        max_symbols: Maximum results to track

    Returns:
        Status message about scanner startup
    """
    global _scanner_task, _scanner_running

    try:
        # Stop existing scanner if running
        if _scanner_running and _scanner_task:
            await stop_differential_trade_scanner()

        # Start new background scanner
        _scanner_task = asyncio.create_task(
            _background_scanner_loop(
                symbols,
                min_trades_per_minute,
                min_percent_change,
                update_interval,
                max_symbols,
            )
        )
        _scanner_running = True

        return f"""# 🚀 Differential Trade Scanner Started

**Scanner Status:** Running in background
**Update Interval:** {update_interval} seconds (like C program)
**Symbols Monitored:** {len(symbols.split(','))} symbols
**Filters:** {min_trades_per_minute}+ trades/min, {min_percent_change}%+ change

## 📊 Monitoring
The scanner is now running continuously and will:
• Take snapshots every {update_interval} seconds
• Calculate exact trade count differences (like C program)
• Cache previous values for differential analysis
• Update results automatically

## 🔍 View Results
• **Current Results:** `get_differential_trade_results()`
• **Stop Scanner:** `stop_differential_trade_scanner()`
• **Scanner Status:** `get_differential_scanner_status()`

**Note:** First results will be available after {update_interval} seconds when the first differential is calculated.
"""

    except Exception as e:
        logger.error(f"Error starting differential trade scanner: {e}")
        return f"Error starting scanner: {str(e)}"


async def stop_differential_trade_scanner() -> str:
    """Stop the background differential trade scanner."""
    global _scanner_task, _scanner_running, _latest_results

    try:
        if _scanner_task and _scanner_running:
            _scanner_task.cancel()
            try:
                await _scanner_task
            except asyncio.CancelledError:
                pass
            _scanner_running = False
            _scanner_task = None

            return "# ⏹️ Differential Trade Scanner Stopped\n\n**Status:** Scanner stopped successfully\n**Cache:** Preserved for next startup"
        else:
            return "# ℹ️ Scanner Status\n\n**Status:** No scanner currently running"

    except Exception as e:
        logger.error(f"Error stopping scanner: {e}")
        return f"Error stopping scanner: {str(e)}"


async def get_differential_trade_results(
    sort_by: str = "trades_change", max_results: int = 20
) -> str:
    """
    Get the latest results from the differential trade scanner.

    Args:
        sort_by: Sort by "trades_change", "percent_change", or "volume_change"
        max_results: Maximum results to return

    Returns:
        Formatted results like the C program's HTML output
    """
    global _latest_results

    try:
        if not _latest_results:
            return """# 📊 Differential Trade Scanner Results

**Status:** No results available yet
**Reason:** Scanner may not be running or waiting for first differential calculation

**Actions:**
• Start scanner: `start_differential_trade_scanner()`
• Check status: `get_differential_scanner_status()`
"""

        results = _latest_results.get("opportunities", [])
        scan_time = _latest_results.get("scan_time", "Unknown")
        total_scanned = _latest_results.get("total_scanned", 0)

        if not results:
            return f"""# 📊 Differential Trade Scanner Results

**Scan Time:** {scan_time}
**Status:** No opportunities found
**Symbols Scanned:** {total_scanned}
**Filters Applied:** Active scanner filters

**Note:** Results update every 60 seconds with exact trade count differences
"""

        # Sort results
        if sort_by == "trades_change":
            results.sort(key=lambda x: x.get("trades_change", 0), reverse=True)
        elif sort_by == "percent_change":
            results.sort(key=lambda x: x.get("percent_change", 0), reverse=True)
        elif sort_by == "volume_change":
            results.sort(key=lambda x: x.get("volume_change", 0), reverse=True)

        # Limit results
        results = results[:max_results]

        # Format like C program HTML output
        output = f"""# 🔥 Differential Trade Scanner Results (Live)

**Scan Time:** {scan_time}
**Method:** Exact trade count differences (like C program)
**Sorted By:** {sort_by.replace('_', ' ').title()}
**Opportunities Found:** {len(results)} (from {total_scanned} symbols)

## 📊 Active Trading Opportunities

"""

        for i, stock in enumerate(results, 1):
            # Momentum indicators like the HTML table
            pct_change = stock.get("percent_change", 0)
            if pct_change > 50:
                momentum = "🚀 EXPLOSIVE"
            elif pct_change > 20:
                momentum = "🔥 STRONG"
            elif pct_change > 10:
                momentum = "📈 ACTIVE"
            else:
                momentum = "⚡ MODERATE"

            output += f"""### {i}. {stock.get('symbol', 'N/A')} - {momentum}
• **Price:** ${stock.get('price', 0):.3f}
• **Trades/Min:** {stock.get('trades_change', 0):,} (EXACT difference)
• **% Change:** {stock.get('percent_change', 0):+.1f}%
• **Gradient/2:** {stock.get('gradient2', 0):.1f}
• **Volume Change:** {stock.get('volume_change', 0):,}
• **Current Trades:** {stock.get('current_trades', 0):,}
• **Previous Close:** ${stock.get('prev_close', 0):.3f}

"""

        # Summary statistics
        avg_trades = (
            sum(s.get("trades_change", 0) for s in results) / len(results)
            if results
            else 0
        )
        avg_change = (
            sum(s.get("percent_change", 0) for s in results) / len(results)
            if results
            else 0
        )
        total_volume_change = sum(s.get("volume_change", 0) for s in results)

        output += f"""## 📈 Scanner Summary
• **Average Trades/Min:** {avg_trades:.0f} (exact differences)
• **Average % Change:** {avg_change:.1f}%
• **Total Volume Change:** {total_volume_change:,}
• **Scanner Status:** {'🟢 Running' if _scanner_running else '🔴 Stopped'}
• **Most Active:** {max(results, key=lambda x: x.get('trades_change', 0))['symbol'] if results else 'N/A'} ({max(results, key=lambda x: x.get('trades_change', 0)).get('trades_change', 0):,} trades/min)
• **Biggest Mover:** {max(results, key=lambda x: x.get('percent_change', 0))['symbol'] if results else 'N/A'} ({max(results, key=lambda x: x.get('percent_change', 0)).get('percent_change', 0):+.1f}%)

## ⚡ Trading Actions
• **Peak Analysis:** `get_stock_peak_trough_analysis("{','.join(s['symbol'] for s in results[:5])}")`
• **Start Streaming:** `start_global_stock_stream(["{'\", \"'.join(s['symbol'] for s in results[:5])}"], ["trades", "quotes"])`
• **Account Status:** `get_account_info()` | **Positions:** `get_positions()`

**Note:** This shows exact trade count differences calculated every 60 seconds, matching the C program methodology.
"""

        return output

    except Exception as e:
        logger.error(f"Error getting differential results: {e}")
        return f"Error retrieving results: {str(e)}"


async def get_differential_scanner_status() -> str:
    """Get the current status of the differential trade scanner."""
    global _scanner_running, _trade_cache, _latest_results

    try:
        cache_size = len(_trade_cache)
        last_scan = (
            _latest_results.get("scan_time", "Never") if _latest_results else "Never"
        )
        opportunities_count = (
            len(_latest_results.get("opportunities", [])) if _latest_results else 0
        )

        status_emoji = "🟢" if _scanner_running else "🔴"

        return f"""# 📊 Differential Trade Scanner Status

**Status:** {status_emoji} {'Running' if _scanner_running else 'Stopped'}
**Method:** Exact trade count differences (like C program)
**Last Scan:** {last_scan}
**Cache Size:** {cache_size} symbols
**Opportunities Found:** {opportunities_count}

## 📈 Scanner Details
• **Update Frequency:** Every 60 seconds
• **Calculation Method:** Current trades - Previous trades (cached)
• **Data Source:** Alpaca minute bar trade counts
• **Background Mode:** {'✅ Active' if _scanner_running else '❌ Inactive'}

## 🔧 Available Commands
• **Start Scanner:** `start_differential_trade_scanner()`
• **Stop Scanner:** `stop_differential_trade_scanner()`
• **View Results:** `get_differential_trade_results()`

**Note:** Scanner uses the same methodology as the C program for exact trade counting.
"""

    except Exception as e:
        logger.error(f"Error getting scanner status: {e}")
        return f"Error getting status: {str(e)}"


async def _background_scanner_loop(
    symbols: str,
    min_trades_per_minute: int,
    min_percent_change: float,
    update_interval: int,
    max_symbols: int,
) -> None:
    """Background loop that runs the differential trade scanner continuously."""
    global _trade_cache, _latest_results

    symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]

    while _scanner_running:
        try:
            logger.info(f"Differential scanner: Processing {len(symbol_list)} symbols")

            # Get current snapshot data (like C program's API call)
            current_data = await _fetch_snapshot_data(symbol_list)

            if not current_data:
                logger.warning("No snapshot data received, retrying next cycle")
                await asyncio.sleep(update_interval)
                continue

            # Process each symbol and calculate differences
            opportunities = []
            scan_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            for symbol in symbol_list:
                if symbol not in current_data:
                    continue

                current_metrics = current_data[symbol]

                # Get cached previous values
                if symbol in _trade_cache:
                    prev_metrics = _trade_cache[symbol]

                    # Calculate exact differences (like C program)
                    trades_change = current_metrics.get("trades", 0) - prev_metrics.get(
                        "trades", 0
                    )
                    volume_change = current_metrics.get("volume", 0) - prev_metrics.get(
                        "volume", 0
                    )

                    # Calculate % change
                    current_price = current_metrics.get("price", 0)
                    prev_close = current_metrics.get("prev_close", 0)

                    if prev_close > 0:
                        percent_change = abs(
                            (current_price - prev_close) / prev_close * 100
                        )
                    else:
                        percent_change = current_metrics.get("daily_change", 0)

                    # Apply filters (like C program's filters)
                    if (
                        trades_change >= min_trades_per_minute
                        and percent_change >= min_percent_change
                        and current_price > 0
                    ):

                        opportunities.append(
                            {
                                "symbol": symbol,
                                "price": current_price,
                                "trades_change": trades_change,
                                "current_trades": current_metrics.get("trades", 0),
                                "volume_change": volume_change,
                                "percent_change": percent_change,
                                "gradient2": percent_change / 2.0,
                                "prev_close": prev_close,
                            }
                        )

                # Update cache (like C program's cache update)
                _trade_cache[symbol] = current_metrics.copy()

            # Store results
            _latest_results = {
                "opportunities": opportunities,
                "scan_time": scan_time,
                "total_scanned": len(symbol_list),
            }

            logger.info(
                f"Differential scanner: Found {len(opportunities)} opportunities"
            )

            # Wait for next cycle
            await asyncio.sleep(update_interval)

        except asyncio.CancelledError:
            logger.info("Differential scanner: Cancelled")
            break
        except Exception as e:
            logger.error(f"Error in differential scanner loop: {e}")
            await asyncio.sleep(update_interval)  # Continue despite errors


async def _fetch_snapshot_data(symbols: list) -> dict:
    """Fetch snapshot data from Alpaca API (like C program's curl call)."""
    try:
        # Get API credentials
        api_key = os.getenv("APCA_API_KEY_ID") or os.getenv("ALPACA_API_KEY")
        secret_key = os.getenv("APCA_API_SECRET_KEY") or os.getenv("ALPACA_SECRET_KEY")

        if not api_key or not secret_key:
            logger.error("API credentials not found")
            return {}

        # Build URL like C program
        symbols_str = ",".join(symbols)
        url = f"https://data.alpaca.markets/v2/stocks/snapshots?symbols={symbols_str}"

        headers = {
            "APCA-API-KEY-ID": api_key,
            "APCA-API-SECRET-KEY": secret_key,
            "accept": "application/json",
        }

        # Make API call (like C program's curl)
        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code != 200:
            logger.error(f"API request failed: {response.status_code}")
            return {}

        data = response.json()

        # Extract metrics like C program
        results = {}

        for symbol, snapshot in data.items():
            if not snapshot:
                continue

            # Extract like C program's JSON parsing
            latest_trade = snapshot.get("latestTrade", {})
            minute_bar = snapshot.get("minuteBar", {})
            daily_bar = snapshot.get("dailyBar", {})
            prev_daily_bar = snapshot.get("prevDailyBar", {})

            # Get trade count from minute bar 'n' field (like C program line 686)
            minute_trades = minute_bar.get("n", 0)
            minute_volume = minute_bar.get("v", 0)

            # Get price (like C program)
            price = latest_trade.get("p", 0)
            if not price and minute_bar.get("c"):
                price = minute_bar.get("c", 0)

            # Get daily data
            daily_change = daily_bar.get("c", 0) if daily_bar else 0
            prev_close = prev_daily_bar.get("c", 0) if prev_daily_bar else 0

            if (
                price > 0 and minute_trades >= 50
            ):  # C program filter: minute_trades < 50 continue (line 687)
                results[symbol] = {
                    "price": price,
                    "trades": minute_trades,
                    "volume": minute_volume,
                    "daily_change": daily_change,
                    "prev_close": prev_close,
                }

        return results

    except Exception as e:
        logger.error(f"Error fetching snapshot data: {e}")
        return {}
