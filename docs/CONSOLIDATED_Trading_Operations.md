# CONSOLIDATED Trading Operations Guide

## Table of Contents
1. [Core Trading Rules & Safety](#core-trading-rules--safety)
2. [Startup Procedures](#startup-procedures)
3. [Complete Alpaca MCP Tools Reference](#complete-alpaca-mcp-tools-reference)
4. [Trading Strategies](#trading-strategies)
5. [Technical Analysis Tools](#technical-analysis-tools)
6. [Real Trading Lessons](#real-trading-lessons)
7. [Emergency Procedures](#emergency-procedures)
8. [Performance Tracking](#performance-tracking)
9. [Streaming Operations](#streaming-operations)
10. [Tools Access Guide](#tools-access-guide)

---

## Core Trading Rules & Safety

### 🚨 NON-NEGOTIABLE TRADING RULES

#### Order Management Rules
- ❌ **NEVER use market orders** (unless specifically instructed)
- ❌ **NEVER sell for a loss** (unless specifically instructed)  
- ✅ **ALWAYS use limit orders** for precise execution
- ✅ **Use 4 decimal places** for penny stocks ($0.0118 format)
- ✅ **Minimum 1,000 trades/minute** for liquidity requirements

#### Speed Requirements
- ⚡ **React within 2-3 seconds** when profit appears
- ⚡ **Monitor streaming data** every 1-3 seconds during active trades
- ⚡ **Check order fills immediately** after placement
- ⚡ **Document entry price** immediately after fill verification

#### Post-Order Fill Procedure (MANDATORY)
After ANY order fills:
1. `get_orders(status="all", limit=5)` - **Verify actual fill price**
2. `get_positions()` - **Confirm position and entry price**  
3. **Write down and verify fill price** - never rely on memory
4. Start appropriate monitoring (streaming for profits, quotes for losses)

### 🎯 TRADING FOCUS

**Target:** Explosive penny stocks and momentum plays (+20% to +500% moves)
**Range:** $0.01 to $10.00 stocks with extreme volatility
**Liquidity:** Minimum 500-1000 trades/minute requirement
**Execution:** Limit orders for precision, streaming data for speed

### ⚖️ REGULATORY COMPLIANCE

#### Pattern Day Trader (PDT) Rule
- **$25,000 minimum** equity required for unlimited day trades
- **Day trade:** Buy and sell same security on same day
- **Restriction:** 3 day trades per 5 business days if under $25k
- **This account:** PDT enabled with unlimited day trades

#### Risk Disclosures
⚠️ **Day trading involves substantial risk of loss**
⚠️ **Most day traders lose money**
⚠️ **Only trade with capital you can afford to lose**
⚠️ **Paper trading recommended for practice**

---

## Startup Procedures

### 🚀 PARALLEL STARTUP EXECUTION

**COMMAND:** `/startup` - Executes all day trading startup checks in parallel for maximum speed

#### PARALLEL BATCH 1: Core System Health (4 tools)
- `health_check()` - Overall system health
- `resource_server_health()` - Server performance metrics  
- `resource_api_status()` - API connectivity status
- `resource_session_status()` - Current session details

#### PARALLEL BATCH 2: Market Status (4 tools)
- `get_market_clock()` - Basic market status
- `get_extended_market_clock()` - Pre/post market details
- `resource_market_conditions()` - Overall market sentiment
- `resource_market_momentum()` - Market direction analysis

#### PARALLEL BATCH 3: Account & Positions (6 tools)
- `get_account_info()` - Buying power and restrictions
- `resource_account_status()` - Real-time account health
- `get_positions()` - Check for any open positions
- `resource_current_positions()` - Live P&L tracking
- `get_orders(status="open")` - Check for stale orders
- `resource_intraday_pnl()` - Today's performance tracking

#### PARALLEL BATCH 4: Data Quality & Streaming (5 tools)
- `resource_data_quality()` - Feed latency and quality
- `get_stock_stream_buffer_stats()` - Streaming infrastructure
- `list_active_stock_streams()` - Check existing streams
- `get_stock_quote("SPY")` - Test streaming latency
- `clear_stock_stream_buffers()` - Clear old streaming data

#### PARALLEL BATCH 5: Trading Tools & Scanners (6 tools)
- `get_stock_snapshots("SPY,QQQ")` - Market snapshot tool
- `scan_day_trading_opportunities()` - Active stock scanner
- `scan_explosive_momentum()` - High-volatility scanner
- `validate_extended_hours_order("SPY", "limit")` - Order validation
- `get_stock_peak_trough_analysis("SPY")` - Entry/exit signals
- **High-liquidity scanner:** `./trades_per_minute.sh -f combined.lis -t 500`

### 🔍 HIGH-LIQUIDITY STOCK SCANNER (CRITICAL)

**ALWAYS use trades_per_minute.sh script instead of MCP scanner functions:**

```bash
./trades_per_minute.sh -f combined.lis -t 500
```

**Analysis procedure:**
- Scan all 10,112 stocks in combined.lis
- Identify stocks with 1000+ trades/minute (Tier 1 targets)
- Identify stocks with 500-999 trades/minute (Tier 2 targets)
- **REJECT any stocks below 500 trades/minute** (insufficient liquidity)
- Prioritize explosive momentum stocks (>20% change) with adequate liquidity

**Example output analysis:**
```
Symbol  Trades/Min  Change%
------   ---------  -------
TSLA          6436    3.13%  ← TIER 1: Ultra-high liquidity
RBNE          2284   380.9%  ← TIER 1: Explosive momentum  
HOVR          1105   36.48%  ← TIER 1: High momentum
ORCL           994    7.46%  ← TIER 2: Just below 1000
```

### ⚡ 8 AM EDT ALGORITHMIC TRADING FRENZY

**CRITICAL MARKET PHENOMENON:** Every trading day at exactly 8:00 AM EDT, massive algorithmic/institutional trading activity creates extreme volatility.

**What Happens:**
- **Tens of thousands of trades** execute within minutes (40K+ trades common)
- **Extreme price swings** - stocks can move 50-200% in minutes
- **Massive volume spikes** - 10x-50x normal pre-market volume
- **Algorithmic order execution** - institutions break large orders into thousands of small trades
- **High-frequency trading systems** activate simultaneously

**Trading Strategy During 8 AM Frenzy:**
- **DO NOT TRADE** during 8:00-8:10 AM EDT period
- **Algorithms control the market** - human traders get crushed
- **Wait for 8:15 AM** when algorithmic activity subsides
- **Use 8 AM data** to identify which stocks institutions are targeting

---

## Complete Alpaca MCP Tools Reference

### Quick Tool Categories

- **[Account & Portfolio](#account--portfolio-management)** - Account info, positions, balances
- **[Market Data](#market-data--quotes)** - Real-time quotes, historical data, snapshots
- **[Technical Analysis](#technical-analysis)** - Peak/trough analysis, after-hours scanning, streaming analytics
- **[Order Management](#order-management)** - Place orders, check status, cancel orders
- **[Options Trading](#options-trading)** - Options data, contracts, options orders
- **[Streaming Data](#streaming-data)** - Real-time market data streams
- **[Market Information](#market-information)** - Market status, calendar, corporate actions
- **[Watchlists](#watchlist-management)** - Create and manage watchlists
- **[Asset Information](#asset-information)** - Asset details, search, filtering
- **[Extended Hours](#extended-hours-trading)** - Pre/post market trading
- **[System Resources](#system-resources)** - Server health, monitoring, diagnostics

---

## Account & Portfolio Management

### `get_account_info()`
Get current account information including balances, buying power, and account status.

**Returns:** Account summary with cash balance, equity, buying power, and account restrictions

**Example:** `get_account_info()`

---

### `get_positions()`
Get all current positions in the portfolio with P&L calculations.

**Returns:** List of all open positions with symbols, quantities, market values, and unrealized P&L

**Example:** `get_positions()`

---

### `get_open_position(symbol: str)`
Get detailed information about a specific open position.

**Parameters:**
- `symbol` (str): Stock symbol to check (e.g., "AAPL")

**Returns:** Detailed position info including entry price, current value, P&L

**Example:** `get_open_position("AAPL")`

---

### `close_position(symbol: str, qty: str = None, percentage: str = None)`
Close a specific position entirely or partially.

**Parameters:**
- `symbol` (str): Stock symbol to close
- `qty` (str, optional): Specific quantity to close
- `percentage` (str, optional): Percentage of position to close

**Returns:** Order confirmation and execution details

**Example:** `close_position("AAPL", percentage="50")`

---

### `close_all_positions(cancel_orders: bool = False)`
Close all open positions in the portfolio.

**Parameters:**
- `cancel_orders` (bool): Whether to cancel existing orders first

**Returns:** Summary of all positions closed

**Example:** `close_all_positions(cancel_orders=True)`

---

## Market Data & Quotes

### `get_stock_quote(symbol: str)`
Get the latest real-time quote for a stock.

**Parameters:**
- `symbol` (str): Stock symbol (e.g., "AAPL")

**Returns:** Current bid/ask prices, spreads, and quote timestamps

**Example:** `get_stock_quote("AAPL")`

---

### `get_stock_snapshots(symbols: str)`
Get comprehensive market snapshots for multiple stocks.

**Parameters:**
- `symbols` (str): Comma-separated stock symbols (e.g., "AAPL,MSFT,NVDA")

**Returns:** Detailed market data including OHLCV, quotes, and daily statistics

**Example:** `get_stock_snapshots("AAPL,MSFT,NVDA")`

---

### `get_stock_bars(symbol: str, days: int = 5)`
Get historical daily price bars for technical analysis.

**Parameters:**
- `symbol` (str): Stock symbol
- `days` (int): Number of days of history (default: 5)

**Returns:** OHLCV data with technical indicators and trends

**Example:** `get_stock_bars("AAPL", days=10)`

---

### `get_stock_bars_intraday(symbol: str, timeframe: str = "1Min", start_date: str = None, end_date: str = None, limit: int = 10000)`
Get intraday historical bars with professional analysis.

**Parameters:**
- `symbol` (str): Stock symbol
- `timeframe` (str): Bar timeframe ("1Min", "5Min", "15Min", "30Min", "1Hour")
- `start_date` (str, optional): Start date (YYYY-MM-DD)
- `end_date` (str, optional): End date (YYYY-MM-DD)
- `limit` (int): Maximum number of bars

**Returns:** Detailed intraday analysis with momentum, volatility, and trading insights

**Example:** `get_stock_bars_intraday("AAPL", timeframe="5Min", limit=100)`

---

### `get_stock_trades(symbol: str, days: int = 5, limit: int = None)`
Get recent trade history for a stock.

**Parameters:**
- `symbol` (str): Stock symbol
- `days` (int): Number of days of trade history
- `limit` (int, optional): Maximum number of trades

**Returns:** Recent trades with prices, sizes, and timestamps

**Example:** `get_stock_trades("AAPL", days=1, limit=50)`

---

### `get_stock_latest_trade(symbol: str)`
Get the most recent trade for a stock.

**Parameters:**
- `symbol` (str): Stock symbol

**Returns:** Latest trade price, size, and timestamp

**Example:** `get_stock_latest_trade("AAPL")`

---

### `get_stock_latest_bar(symbol: str)`
Get the latest minute bar for a stock.

**Parameters:**
- `symbol` (str): Stock symbol

**Returns:** Most recent OHLCV bar data

**Example:** `get_stock_latest_bar("AAPL")`

---

## Technical Analysis

### `get_stock_peak_trough_analysis(symbols: str, timeframe: str = "1Min", days: int = 1, limit: int = 1000, window_len: int = 11, lookahead: int = 1, delta: float = 0.0, min_peak_distance: int = 5)`
**🔥 NEW TOOL** - Advanced peak and trough analysis using zero-phase Hanning filtering for day trading signals.

**Parameters:**
- `symbols` (str): Stock symbols (e.g., "CGTL" or "AAPL,MSFT,NVDA")
- `timeframe` (str): Bar timeframe ("1Min", "5Min", "15Min", "30Min", "1Hour")
- `days` (int): Historical days to analyze (1-30)
- `limit` (int): Max bars to fetch (1-10000)
- `window_len` (int): Hanning filter smoothing (3-101, must be odd)
- `lookahead` (int): Peak detection sensitivity (1-50)
- `delta` (float): Minimum peak amplitude (0.0 for penny stocks)
- `min_peak_distance` (int): Min bars between peaks

**Returns:** Comprehensive analysis with BUY/LONG and SELL/SHORT signals, support/resistance levels

**Perfect for:** Finding precise entry/exit points, following the trading lesson "SCAN LONGER before entry"

**Example:** `get_stock_peak_trough_analysis("CGTL,HCTI", timeframe="1Min", window_len=11)`

---

### `scan_after_hours_opportunities(symbols: str = "AAPL,MSFT,NVDA,TSLA,GOOGL,AMZN,META,NFLX,COIN,HOOD,AMC,GME,PLTR,SOFI,RIVN,LCID", min_volume: int = 100000, min_percent_change: float = 2.0, max_symbols: int = 15, sort_by: str = "percent_change")`
**🌙 NEW TOOL** - Scan for after-hours trading opportunities with enhanced analytics.

**Parameters:**
- `symbols` (str): Comma-separated symbols for after-hours scanning
- `min_volume` (int): Minimum after-hours volume threshold
- `min_percent_change` (float): Minimum % change from regular session close
- `max_symbols` (int): Maximum results to return
- `sort_by` (str): Sort by "percent_change", "volume", or "price"

**Focuses on:**
1. Extended hours price movements
2. Volume analysis relative to average
3. News-driven momentum detection
4. Liquidity assessment for safe entry/exit

**Returns:** Formatted analysis of after-hours opportunities with risk levels and trading recommendations

**Perfect for:** Finding after-hours movers, earnings plays, news-driven stocks

**Example:** `scan_after_hours_opportunities("AAPL,TSLA,NVDA", min_volume=50000, min_percent_change=1.5)`

---

### `get_enhanced_streaming_analytics(symbol: str, analysis_minutes: int = 15, include_orderbook: bool = True)`
**🔥 NEW TOOL** - Enhanced streaming analytics with real-time calculations.

**Parameters:**
- `symbol` (str): Stock symbol to analyze
- `analysis_minutes` (int): Minutes of historical data to include
- `include_orderbook` (bool): Include bid/ask analysis

**Provides:**
1. Real-time momentum analysis
2. Volume-weighted average price (VWAP)
3. Order flow analysis
4. Support/resistance detection
5. Volatility measurements

**Returns:** Comprehensive real-time analytics with trading signals and monitoring commands

**Perfect for:** Day trading setup, real-time market analysis, momentum confirmation

**Example:** `get_enhanced_streaming_analytics("TSLA", analysis_minutes=10, include_orderbook=True)`

---

### `generate_advanced_technical_plots(symbols: str, timeframe: str = "1Min", days: int = 1, window_len: int = 11, lookahead: int = 1, plot_mode: str = "single")`
**📊 NEW TOOL** - Professional peak/trough analysis plots with publication-quality output.

**Parameters:**
- `symbols` (str): Comma-separated symbols (e.g., "AAPL,MSFT,TSLA")
- `timeframe` (str): "1Min", "5Min", "15Min", "30Min", "1Hour", "1Day"
- `days` (int): Number of trading days (1-30)
- `window_len` (int): Hanning filter window (3-101, must be odd)
- `lookahead` (int): Peak detection sensitivity (1-50)
- `plot_mode` (str): "single", "combined", "overlay", "all"

**Features:**
- **Zero-phase filtering** visualization
- **Peak/trough detection** with actual price annotations
- **Professional styling** with auto-positioned legends
- **Publication-quality** PNG output
- **Trading signals summary** with precise levels

**Returns:** Professional analysis with plot files and trading level summaries

**Example:** `generate_advanced_technical_plots("AAPL,MSFT", plot_mode="overlay")`

---

## Order Management

### `place_stock_order(symbol: str, side: str, quantity: float, order_type: str = "market", time_in_force: str = "day", limit_price: float = None, stop_price: float = None, extended_hours: bool = False, client_order_id: str = None, trail_percent: float = None, trail_price: float = None)`
Place a stock order with full control over order parameters.

**Parameters:**
- `symbol` (str): Stock symbol
- `side` (str): "buy" or "sell"
- `quantity` (float): Number of shares
- `order_type` (str): "market", "limit", "stop", "stop_limit", "trailing_stop"
- `time_in_force` (str): "day", "gtc", "ioc", "fok"
- `limit_price` (float, optional): Limit price for limit orders
- `stop_price` (float, optional): Stop price for stop orders
- `extended_hours` (bool): Allow extended hours trading
- `trail_percent` (float, optional): Trailing stop percentage

**Returns:** Order confirmation with order ID and status

**Example:** `place_stock_order("AAPL", "buy", 10, order_type="limit", limit_price=150.00)`

---

### `get_orders(status: str = "all", limit: int = 10)`
Get orders with specified status.

**Parameters:**
- `status` (str): "all", "open", "closed", "filled", "cancelled"
- `limit` (int): Maximum number of orders to return

**Returns:** List of orders with details and current status

**Example:** `get_orders(status="open", limit=20)`

---

### `cancel_order_by_id(order_id: str)`
Cancel a specific order by its ID.

**Parameters:**
- `order_id` (str): Unique order identifier

**Returns:** Cancellation confirmation

**Example:** `cancel_order_by_id("12345678-1234-1234-1234-123456789012")`

---

### `cancel_all_orders()`
Cancel all open orders.

**Returns:** Summary of cancelled orders

**Example:** `cancel_all_orders()`

---

## Options Trading

### `get_option_contracts(underlying_symbol: str, expiration_date: str = None, strike_price_gte: str = None, strike_price_lte: str = None, type: str = None, limit: int = None)`
Get option contracts for an underlying stock.

**Parameters:**
- `underlying_symbol` (str): Stock symbol (e.g., "AAPL")
- `expiration_date` (str, optional): Specific expiration date
- `strike_price_gte` (str, optional): Minimum strike price
- `strike_price_lte` (str, optional): Maximum strike price
- `type` (str, optional): "call" or "put"
- `limit` (int, optional): Maximum contracts to return

**Returns:** Available option contracts with strikes, expirations, and symbols

**Example:** `get_option_contracts("AAPL", type="call", strike_price_gte="150")`

---

### `get_option_latest_quote(symbol: str)`
Get latest quote for an option contract.

**Parameters:**
- `symbol` (str): Option symbol (e.g., "AAPL230616C00150000")

**Returns:** Option bid/ask prices and Greeks

**Example:** `get_option_latest_quote("AAPL230616C00150000")`

---

### `get_option_snapshot(symbol: str)`
Get comprehensive option snapshot with Greeks.

**Parameters:**
- `symbol` (str): Option symbol

**Returns:** Complete option data including Greeks (Delta, Gamma, Theta, Vega)

**Example:** `get_option_snapshot("AAPL230616C00150000")`

---

### `place_option_market_order(legs: list, order_class: str = None, quantity: int = 1)`
Place single or multi-leg options market order.

**Parameters:**
- `legs` (list): List of option legs with symbols and quantities
- `order_class` (str, optional): Order class for multi-leg strategies
- `quantity` (int): Number of contracts

**Returns:** Option order confirmation

**Example:** `place_option_market_order([{"symbol": "AAPL230616C00150000", "side": "buy"}])`

---

## Streaming Data

### `start_global_stock_stream(symbols: list, data_types: list = ["trades", "quotes"], feed: str = "sip", duration_seconds: int = None, replace_existing: bool = False, buffer_size_per_symbol: int = None)`
Start real-time stock data streaming for day trading.

**Parameters:**
- `symbols` (list): List of stock symbols to stream
- `data_types` (list): Types of data ("trades", "quotes", "bars")
- `feed` (str): Data feed ("sip" or "iex")
- `duration_seconds` (int, optional): Auto-stop after duration
- `replace_existing` (bool): Replace existing streams

**Returns:** Stream configuration and status

**Example:** `start_global_stock_stream(["AAPL", "MSFT"], data_types=["trades", "quotes"])`

---

### `stop_global_stock_stream()`
Stop the global stock streaming session.

**Returns:** Stream stop confirmation

**Example:** `stop_global_stock_stream()`

---

### `add_symbols_to_stock_stream(symbols: list, data_types: list = None)`
Add symbols to existing stock stream.

**Parameters:**
- `symbols` (list): Additional symbols to stream
- `data_types` (list, optional): Data types for new symbols

**Returns:** Updated stream configuration

**Example:** `add_symbols_to_stock_stream(["NVDA", "TSLA"])`

---

### `get_stock_stream_data(symbol: str, data_type: str, recent_seconds: int = None, limit: int = None)`
Get streaming data for analysis.

**Parameters:**
- `symbol` (str): Stock symbol
- `data_type` (str): "trades", "quotes", or "bars"
- `recent_seconds` (int, optional): Get data from last N seconds
- `limit` (int, optional): Maximum records to return

**Returns:** Real-time streaming data for analysis

**Example:** `get_stock_stream_data("AAPL", "trades", recent_seconds=60)`

---

### `list_active_stock_streams()`
List all active streaming subscriptions.

**Returns:** Currently active streams and their configurations

**Example:** `list_active_stock_streams()`

---

### `get_stock_stream_buffer_stats()`
Get detailed streaming buffer statistics.

**Returns:** Memory usage and performance metrics for streams

**Example:** `get_stock_stream_buffer_stats()`

---

### `clear_stock_stream_buffers()`
Clear streaming buffers to free memory.

**Returns:** Buffer clear confirmation

**Example:** `clear_stock_stream_buffers()`

---

## Market Information

### `get_market_clock()`
Get current market status and next open/close times.

**Returns:** Market open/closed status and upcoming session times

**Example:** `get_market_clock()`

---

### `get_market_calendar(start_date: str, end_date: str)`
Get market calendar for specified date range.

**Parameters:**
- `start_date` (str): Start date (YYYY-MM-DD)
- `end_date` (str): End date (YYYY-MM-DD)

**Returns:** Trading days and market hours

**Example:** `get_market_calendar("2023-06-01", "2023-06-30")`

---

### `get_extended_market_clock()`
Enhanced market clock with pre/post market sessions.

**Returns:** Detailed market status including extended hours

**Example:** `get_extended_market_clock()`

---

### `get_corporate_announcements(ca_types: list, since: str, until: str, symbol: str = None, cusip: str = None, date_type: str = None)`
Get corporate action announcements.

**Parameters:**
- `ca_types` (list): Types of corporate actions
- `since` (str): Start date
- `until` (str): End date
- `symbol` (str, optional): Specific symbol
- `cusip` (str, optional): CUSIP identifier

**Returns:** Corporate announcements and events

**Example:** `get_corporate_announcements(["dividend", "split"], "2023-06-01", "2023-06-30")`

---

## Watchlist Management

### `create_watchlist(name: str, symbols: list)`
Create a new watchlist with specified symbols.

**Parameters:**
- `name` (str): Watchlist name
- `symbols` (list): List of stock symbols

**Returns:** Created watchlist details

**Example:** `create_watchlist("Day Trading", ["AAPL", "MSFT", "NVDA"])`

---

### `get_watchlists()`
Get all watchlists for the account.

**Returns:** All watchlists with their symbols

**Example:** `get_watchlists()`

---

### `update_watchlist(watchlist_id: str, name: str = None, symbols: list = None)`
Update an existing watchlist.

**Parameters:**
- `watchlist_id` (str): Watchlist identifier
- `name` (str, optional): New name
- `symbols` (list, optional): New symbol list

**Returns:** Updated watchlist details

**Example:** `update_watchlist("12345", symbols=["AAPL", "MSFT", "NVDA", "TSLA"])`

---

## Asset Information

### `get_all_assets(status: str = None, asset_class: str = None, exchange: str = None, attributes: str = None)`
Get all available assets with optional filtering.

**Parameters:**
- `status` (str, optional): Asset status filter
- `asset_class` (str, optional): Asset class (e.g., "us_equity")
- `exchange` (str, optional): Exchange filter
- `attributes` (str, optional): Additional attributes

**Returns:** List of available trading assets

**Example:** `get_all_assets(asset_class="us_equity", status="active")`

---

### `get_asset_info(symbol: str)`
Get detailed information about a specific asset.

**Parameters:**
- `symbol` (str): Asset symbol

**Returns:** Detailed asset information including exchange and trading status

**Example:** `get_asset_info("AAPL")`

---

## Extended Hours Trading

### `validate_extended_hours_order(symbol: str, order_type: str, extended_hours: bool = None)`
Validate if order can be placed in current market session.

**Parameters:**
- `symbol` (str): Stock symbol
- `order_type` (str): Type of order
- `extended_hours` (bool, optional): Extended hours flag

**Returns:** Validation result and recommendations

**Example:** `validate_extended_hours_order("AAPL", "limit")`

---

### `place_extended_hours_order(symbol: str, side: str, quantity: float, order_type: str = "limit", limit_price: float = None, time_in_force: str = "day", extended_hours: bool = None)`
Place order with automatic extended hours detection.

**Parameters:**
- `symbol` (str): Stock symbol
- `side` (str): "buy" or "sell"
- `quantity` (float): Number of shares
- `order_type` (str): Order type
- `limit_price` (float, optional): Limit price
- `extended_hours` (bool, optional): Auto-detected if None

**Returns:** Order confirmation with extended hours details

**Example:** `place_extended_hours_order("AAPL", "buy", 10, limit_price=150.00)`

---

### `get_extended_hours_info()`
Get comprehensive information about extended hours trading.

**Returns:** Extended hours rules, times, and restrictions

**Example:** `get_extended_hours_info()`

---

## System Resources

### `health_check()`
Quick server health and status check.

**Returns:** Overall system health summary

**Example:** `health_check()`

---

### `resource_account_status()`
Get detailed account status resource.

**Returns:** Account health and status metrics

**Example:** `resource_account_status()`

---

### `resource_current_positions()`
Get current positions resource data.

**Returns:** Position tracking and performance data

**Example:** `resource_current_positions()`

---

### `resource_market_conditions()`
Get current market conditions analysis.

**Returns:** Market sentiment and conditions

**Example:** `resource_market_conditions()`

---

### `resource_market_momentum(symbol: str = "SPY", timeframe_minutes: int = 1, sma_short: int = 5, sma_long: int = 20, analysis_hours: int = 2)`
Get market momentum analysis.

**Parameters:**
- `symbol` (str): Symbol to analyze (default: "SPY")
- `timeframe_minutes` (int): Timeframe in minutes
- `sma_short` (int): Short moving average period
- `sma_long` (int): Long moving average period
- `analysis_hours` (int): Hours of data to analyze

**Returns:** Momentum indicators and trend analysis

**Example:** `resource_market_momentum("SPY", timeframe_minutes=5)`

---

### `resource_intraday_pnl(days_back: int = 0, include_open_positions: bool = True, min_trade_value: float = 0, symbol_filter: str = None)`
Get intraday P&L tracking.

**Parameters:**
- `days_back` (int): Days back to analyze
- `include_open_positions` (bool): Include unrealized P&L
- `min_trade_value` (float): Minimum trade value filter
- `symbol_filter` (str, optional): Symbol filter

**Returns:** Detailed P&L breakdown and performance metrics

**Example:** `resource_intraday_pnl(days_back=1, include_open_positions=True)`

---

### `resource_data_quality(test_symbols: list = None, latency_threshold_ms: float = 500.0, quote_age_threshold_seconds: float = 60.0, spread_threshold_pct: float = 1.0)`
Check data quality and latency.

**Parameters:**
- `test_symbols` (list, optional): Symbols to test
- `latency_threshold_ms` (float): Latency threshold
- `quote_age_threshold_seconds` (float): Quote age threshold
- `spread_threshold_pct` (float): Spread threshold

**Returns:** Data quality metrics and latency analysis

**Example:** `resource_data_quality(test_symbols=["AAPL", "MSFT"])`

---

### `resource_server_health()`
Get server health diagnostics.

**Returns:** Server performance and health metrics

**Example:** `resource_server_health()`

---

### `resource_session_status()`
Get session status information.

**Returns:** Current session details and status

**Example:** `resource_session_status()`

---

### `resource_api_status()`
Get API status and connectivity.

**Returns:** API health and connection status

**Example:** `resource_api_status()`

---

## Trading Strategies

### 🎯 LIGHTNING-FAST PROFIT TAKING (PRIMARY STRATEGY)

**PRIORITY #1: PREVENT DECLINING PEAKS SCENARIOS**

```python
def aggressive_profit_monitoring():
    """Execute IMMEDIATELY on ANY profit opportunity"""
    
    while position_open:
        current_pnl = calculate_unrealized_pnl()
        
        # ANY PROFIT = IMMEDIATE EXIT
        if current_pnl > 0:
            execute_immediate_exit(reason="PROFIT_PRESERVATION")
            break
            
        # Check every 10 seconds when near breakeven
        time.sleep(10)
```

#### Execution Hierarchy
1. **FIRST PROFIT SPIKE → EXIT** (Target: 10-second execution)
2. **SECOND PROFIT SPIKE → EMERGENCY EXIT** (Target: 5-second execution)  
3. **Third opportunity missed → Forced into declining peaks strategy**

### 📈 PEAK/TROUGH ANALYSIS STRATEGY

#### Entry Strategy
- Wait for clear TROUGH signals from `get_stock_peak_trough_analysis()`
- Enter on support bounces, not resistance breaks
- Size positions based on liquidity (trades/minute)
- Always use limit orders at or below ask

#### Exit Strategy (REFINED FROM RBNE LESSONS)
- **Don't exit on first small bounce** - wait for PEAK signal
- Use peak/trough tool for BOTH entry AND exit timing
- Follow signals, not emotions
- Exit patience is as important as entry patience

**INTEGRATED TOOL USAGE:**
1. Peak/trough analysis for signals (60-second cycles)
2. Streaming data for execution timing (when signals appear)
3. **NOT:** Streaming for "checking if profitable"

### 🛑 DECLINING PEAKS EXIT STRATEGY (EMERGENCY ONLY)

⚠️ **WARNING: This is a HIGH-RISK emergency strategy that should be AVOIDED through aggressive profit-taking earlier in the trade.**

#### When to Use
- Stock shows 3+ declining peaks (distribution/liquidation phase)
- Pre-market (4-9:30 AM) or post-market (4-8 PM) preferred
- Existing position needs capital preservation exit
- Institutional selling pressure evident

#### Strategy Execution
```bash
declining_peaks_exit [SYMBOL] [MAX_MULTIPLIER] [PROFIT_CENTS]
```

**Example:** `declining_peaks_exit USEG 3 5` (max 3x position, 5¢ profit target)

#### Critical Rules
- Max 3x position multiplier (not 50x like USEG example)
- Exit immediately when profit target hit (speed critical)
- 30-day blacklist after successful exit (wash sale prevention)
- 5% stop loss below new average cost
- Time limit: 45 minutes maximum

### 🔄 60-SECOND MONITORING CYCLE STRATEGY

**NEW TRADING LESSON:** Concentrate on USEG and the snapshot, peak/trough, intraday, and real-time streaming tools. 

#### Strategy Flow:
1. **Every 60 seconds**: Fetch snapshot data and use peak/trough analysis tool to look for new trough/buy signals
2. **When trough buy signal received**: Use streaming tool to buy at lowest/best trade or quote price
3. **Critical timing**: Monitor pre-market order aggressively and ensure it fills before price goes up
4. **FOMO prevention**: Timing is critical - be alert for immediate execution

#### Execution Steps:
```python
def sixty_second_monitoring_cycle(symbol="USEG"):
    """60-second monitoring cycle for optimal entry timing"""
    
    while True:
        # Step 1: Get snapshot + peak/trough analysis
        snapshot = get_stock_snapshots(symbol)
        peak_trough = get_stock_peak_trough_analysis(symbol)
        
        # Step 2: Check for trough/buy signal
        if has_trough_buy_signal(peak_trough):
            # Step 3: Get real-time streaming data for optimal entry
            stream_data = get_stock_stream_data(symbol, "quotes", recent_seconds=10)
            optimal_price = get_best_bid_ask_price(stream_data)
            
            # Step 4: Place limit order at optimal price
            order = place_stock_order(
                symbol=symbol,
                side="buy",
                quantity=calculate_position_size(),
                order_type="limit",
                limit_price=optimal_price,
                time_in_force="ioc"  # Immediate or cancel
            )
            
            # Step 5: Monitor fill aggressively
            monitor_order_fill_aggressively(order["id"])
            break
        
        # Wait 60 seconds before next cycle
        time.sleep(60)
```

#### Key Tools Sequence:
- `get_stock_snapshots()` + `get_stock_peak_trough_analysis()` (every 60s)
- On trough signal → `get_stock_stream_data()` for real-time pricing
- `place_stock_order()` with optimal entry price from streaming
- Monitor order status until filled

#### Risk Management:
- Must fill before FOMO kicks in
- Use limit orders at streaming bid/ask levels
- Monitor for quick fills in pre-market conditions
- Aggressive order monitoring prevents missed opportunities

---

## Technical Analysis Tools

### 📊 Peak and Trough Analysis Tool

The Peak and Trough Analysis Tool is a professional technical analysis instrument designed for day trading applications. It implements zero-phase Hanning filtering followed by peak detection algorithms to identify precise entry and exit points for trading strategies.

#### Purpose

This tool directly addresses the trading lesson: **"SCAN LONGER before entry - Watch streaming data 60-120 seconds to find better entry price"** by providing sophisticated technical analysis to identify optimal support and resistance levels.

#### Technical Implementation

**Algorithm Flow:**

1. **Data Acquisition**: Fetches historical intraday bar data from Alpaca Markets
2. **Zero-Phase Filtering**: Applies low-pass Hanning window filtering to remove noise while preserving timing
3. **Peak Detection**: Uses advanced algorithms to identify local maxima (peaks) and minima (troughs)
4. **Signal Analysis**: Generates trading recommendations based on current price position relative to recent peaks/troughs

**Key Features:**
- **X/Y Accuracy**: Peak timing from filtered data, price levels from original unfiltered data
- **Configurable Parameters**: Full control over analysis parameters
- **Multi-Symbol Support**: Analyze multiple stocks simultaneously
- **Multiple Timeframes**: Support for 1Min, 5Min, 15Min, 30Min, 1Hour bars
- **Trading Signals**: Clear BUY/LONG, SELL/SHORT, and WATCH recommendations

#### Parameters

**Required Parameters:**
- **symbols** (str): Comma-separated list of stock symbols
  - Examples: `"CGTL"`, `"AAPL,MSFT,NVDA"`

**Optional Parameters:**
- **timeframe** (str, default: "1Min"): Bar timeframe
  - Options: "1Min", "5Min", "15Min", "30Min", "1Hour"
  - Recommendation: Use "1Min" for day trading

- **days** (int, default: 1, range: 1-30): Number of trading days of historical data
  - Example: `days=2` for 2 days of data
  - More days = more historical context

- **limit** (int, default: 1000, range: 1-10000): Maximum number of bars to fetch
  - Controls data volume
  - Higher limit = more analysis depth

- **window_len** (int, default: 11, range: 3-101, must be odd): Hanning filter window length
  - Controls smoothing level
  - Smaller values = less smoothing, more sensitive
  - Larger values = more smoothing, less noise
  - Recommended: 11 for 1Min data, 21 for 5Min+ data

- **lookahead** (int, default: 1, range: 1-50): Peak detection lookahead parameter
  - Controls peak detection sensitivity
  - 1 = most sensitive (finds more peaks)
  - Higher values = less sensitive (finds fewer, stronger peaks)
  - Recommended: 1 for day trading

- **delta** (float, default: 0.0): Minimum peak/trough amplitude threshold
  - Set to 0.0 for penny stocks (no minimum amplitude)
  - Use higher values for filtering small fluctuations
  - Example: 0.01 for stocks >$1.00

- **min_peak_distance** (int, default: 5): Minimum bars between peaks
  - Filters noise by requiring distance between peaks
  - Higher values = fewer, more significant peaks
  - Lower values = more frequent signals

#### Usage Examples

**Basic Analysis:**
```python
# Quick analysis of CGTL with default settings
result = await get_stock_peak_trough_analysis("CGTL")
```

**Multi-Symbol Analysis:**
```python
# Analyze multiple stocks with 5-minute bars
result = await get_stock_peak_trough_analysis(
    symbols="AAPL,MSFT,NVDA",
    timeframe="5Min",
    days=2
)
```

**High-Sensitivity Analysis:**
```python
# More sensitive analysis for scalping
result = await get_stock_peak_trough_analysis(
    symbols="CGTL",
    timeframe="1Min",
    window_len=7,      # Less smoothing
    lookahead=1,       # Most sensitive
    min_peak_distance=3  # Closer peaks allowed
)
```

#### Output Format

The tool returns a comprehensive formatted analysis including:

**Header Information:**
- Analysis parameters used
- Timestamp of analysis
- Symbol list processed

**Per-Symbol Analysis:**
- Total bars analyzed
- Price range (min/max)
- Current price
- Number of peaks and troughs found

**Recent Peaks (Resistance/Sell Signals):**
- Timestamp of each peak
- Original price at peak (executable level)
- Filtered price (detection level)
- Latest peak analysis with distance

**Recent Troughs (Support/Buy Signals):**
- Timestamp of each trough
- Original price at trough (executable level)
- Filtered price (detection level)
- Latest trough analysis with distance

**Trading Signal Summary:**
- **BUY/LONG**: Price rising from recent trough
- **SELL/SHORT**: Price declining from recent peak
- **WATCH**: Price near turning point
- Signal strength percentage
- Distance from latest signal

#### Trading Applications

**Entry Point Identification:**
- **Buy Signals**: When price bounces from trough support
- **Sell Signals**: When price rejects from peak resistance
- **Confirmation**: Use with streaming data for timing

**Risk Management:**
- **Stop Levels**: Place stops below troughs (long) or above peaks (short)
- **Target Levels**: Take profits at opposite signal level
- **Position Sizing**: Use signal strength for position allocation

#### Parameter Tuning Guidelines

**For Penny Stocks (< $1.00):**
```python
get_stock_peak_trough_analysis(
    symbols="CGTL,HCTI",
    timeframe="1Min",
    window_len=11,
    lookahead=1,
    delta=0.0,          # No minimum amplitude
    min_peak_distance=5
)
```

**For Regular Stocks (> $1.00):**
```python
get_stock_peak_trough_analysis(
    symbols="AAPL,MSFT",
    timeframe="1Min", 
    window_len=11,
    lookahead=1,
    delta=0.01,         # Filter small moves
    min_peak_distance=5
)
```

**For Volatile Stocks:**
```python
get_stock_peak_trough_analysis(
    symbols="volatile_stock",
    timeframe="1Min",
    window_len=15,      # More smoothing
    lookahead=2,        # Less sensitive
    min_peak_distance=7  # Wider spacing
)
```

### 📊 Market Data Corrections

#### Pre-Market Data Corrections

**CRITICAL:** Alpaca's snapshot data contains stale/incorrect reference data during pre-market hours that leads to inaccurate percentage calculations.

**Problem:**
- The "Previous Close" field in snapshots shows outdated data (often from days prior)
- This causes incorrect percentage change calculations during pre-market trading
- Other financial data providers (Yahoo Finance, etc.) often have the same issue

**Solution for Pre-Market Analysis:**

When analyzing stocks during pre-market hours, use this interpretation of snapshot data:

```
Today's OHLC: Open/High/Low/Close
                ↑              ↑
         Today's open    Yesterday's ACTUAL close
```

**Correct Pre-Market Calculation:**
- Yesterday's actual close = Last value in "Today's OHLC" (the "Close" field)
- Current price = Latest trade price from snapshot
- Accurate % change = ((Current Price - Yesterday's Close) / Yesterday's Close) × 100

**Example Correction:**
```
Snapshot shows: "Today's OHLC: $6.73 / $9.20 / $5.89 / $7.14"
- Yesterday's actual close: $7.14 (NOT the "Previous Close" field)
- Current price: $15.00
- Correct % change: ($15.00 - $7.14) / $7.14 = +110.08%
```

**This correction is essential until normal market hours begin and Alpaca updates their reference data.**

---

## Real Trading Lessons

### 📚 RBNE TRADING SESSION - June 13, 2025

#### Critical Execution Errors & Lessons

1. **FAILED TO TRACK ENTRY PRICE**
   - **Error:** Placed sell limit at $9.98 thinking it was breakeven
   - **Reality:** Actual fill was $9.98, got lucky with $10.00 execution
   - **Lesson:** ALWAYS write down and verify fill price immediately
   - **Solution:** Create position tracker:
     ```
     POSITION TRACKER:
     Symbol: RBNE
     Entry Time: 08:39:39 EDT
     Entry Price: $9.98 (VERIFIED)
     Quantity: 5,000
     Total Cost: $49,900
     Target Exit: Entry + $0.XX
     ```

2. **POSITION SIZE ERROR: 10x Too Small**
   - **Requested:** $50,000
   - **Executed:** $5,000 (~$49,900)
   - **Impact:** Reduced profit potential by 90%
   - **Formula:** Shares = Capital / Price (Round down for safety)

3. **PREMATURE EXIT: Ignored Peak/Trough Analysis**
   - **My Exit:** $10.00 (first tiny bounce)
   - **Optimal Exit:** $12.95+ (based on peak detection)
   - **Money Left:** $14,750 ($2.95 × 5,000 shares)
   - **Lesson:** Use peak/trough tool for BOTH entry AND exit

#### The Patience Paradox
**The Hardest Part:** Being patient when you have a profit
- Natural instinct: "Take it before it disappears!"
- Professional approach: "Follow the signals, not emotions"

**Two-Phase Patience Required:**
1. **Entry Patience:** ✅ Successfully waited for trough signal
2. **Exit Patience:** ❌ Failed - took first profit opportunity

### 📊 USEG STRATEGY SHIFT LESSONS

#### Speed vs. Analysis Balance

**OLD THINKING (USEG Lessons):**
- "ANY profit = exit immediately"
- "Speed over perfection"
- "Don't be greedy"

**REFINED THINKING (RBNE Lessons):**
- "Use tools to maximize profitable exits"
- "Patient entries deserve patient exits"
- "Follow signals, not emotions"
- "Speed on declining peaks, patience on rising trends"

#### Critical Mindset Shifts
❌ **WRONG:** "Let me analyze if this is the perfect exit"  
✅ **CORRECT:** "PROFIT = SELL NOW" (for declining peaks only)

❌ **WRONG:** "Maybe it will go higher"  
✅ **CORRECT:** "Follow peak/trough signals for rising trends"

❌ **WRONG:** "Let me check the signals first"  
✅ **CORRECT:** "Use signals to guide timing, not override them"

### 🎯 TRADING LESSONS LEARNED - Session Summary

#### 1. Peak/Trough Analysis Tool Enhancement ✅
**Problem**: The MCP peak/trough tool was showing incorrect/stale data (RSLS showing $2.36 when actual was $3.75)

**Solution**: 
- Replaced faulty MCP implementation with proven standalone script functionality
- Enhanced with zero-phase Hanning filtering and trading calendar integration
- Key improvement: Report ORIGINAL prices at peak/trough locations, not filtered values
- Added comprehensive helper functions (HistoricalDataFetcher, process_bars_for_peaks, get_latest_signal)

**Technical Details**:
- Zero-phase low-pass filtering using Hanning window preserves timing while removing noise
- Peak/trough detection on filtered data but trading signals use original unfiltered prices
- 4-decimal precision for penny stocks ($0.0118 format)
- Sample indices and timestamps for verification

#### 2. Position Monitoring Discipline 🚨
**Critical Lesson**: Must follow monitoring rules strictly to capture profit spikes

**Rules Established**:
- **Below purchase price**: Check every 30 seconds with get_stock_quote
- **Above purchase price**: Use aggressive streaming to capture profit spikes
- **Never get complacent** when in profit - continue monitoring until exit

**Mistake Made**: During GNLN trade, failed to continuously stream when above purchase price
- User showed Yahoo Finance chart proving GNLN hit $0.0176 
- I sold at ~$0.0150, missing optimal exit at higher spike
- **User feedback**: "Did you forget to watch the stock? it was much higher at the spike. you were lazy."

**Lesson**: Always maintain discipline with streaming when above purchase price - profit spikes happen fast

#### 3. Trading Execution Best Practices ✅
**Order Types**: Use FOK (Fill or Kill) and IOC (Immediate or Cancel) orders for day trading
- Provides immediate execution or cancellation
- Critical for fast-moving penny stocks

**Precision**: Always use 4-decimal places for penny stocks
- Example: $0.0118 not $0.012
- Ensures accurate calculations and proper order placement

**Liquidity Requirements**: Minimum 1,000 trades per minute for day trading candidates
- Ensures sufficient activity for entry/exit

#### 4. Peak/Trough Signal Interpretation ✅
**Buy Signals (Troughs)**:
- Recent trough (≤3 bars ago) with price within 2% = BUY/LONG signal
- Original unfiltered price at trough location used for entry calculations

**Sell Signals (Peaks)**:
- Recent peak (≤3 bars ago) with price within 2% = SELL/SHORT signal  
- Original unfiltered price at peak location used for exit calculations

**Signal Proximity**: Within 3 bars of latest signal provides highest probability trades

#### 5. Scanner List Analysis ✅
**Process**:
1. Run snapshot analysis to identify active stocks (trades per minute)
2. Run peak/trough analysis to find recent BUY signals (troughs)
3. Prioritize stocks with both high activity AND recent trough signals
4. Execute on best candidate with proper order types

**GNLN Example**: 
- High activity from scanner
- Recent trough signal from peak/trough analysis
- Successful execution with IOC orders
- Profit captured (though not at optimal spike due to monitoring lapse)

### 🎯 Key Success Factors

#### Execution Speed Rankings
1. **LIGHTNING FAST PROFIT-TAKING** (Prevents declining peaks scenarios)
2. **Follow Peak/Trough Signals** (For optimal entry/exit timing)
3. **Speed Over Perfection** (When emergency exit needed)
4. **Small Profits Compound** ($50 taken > $500 missed)
5. **Exit Discipline** (When tools signal exit, execute immediately)

---

## Emergency Procedures

### 🚨 STOP ALL TRADING
```bash
cancel_all_orders()    # Cancel all pending orders
close_all_positions()  # Emergency position exit
stop_global_stock_stream()  # Stop streaming data
```

### 🛑 DECLINING PEAKS EMERGENCY SEQUENCE

#### Phase 1: Pattern Recognition (60-second cycles)
```python
def detect_declining_peaks_pattern(symbol):
    snapshot = get_stock_snapshots(symbol)
    analysis = get_stock_peak_trough_analysis(symbol, window=5)
    
    # Extract last 3 peaks
    peaks = analysis.get_peaks()[-3:]
    
    if len(peaks) >= 3 and peaks_are_declining(peaks):
        return {"pattern_confirmed": True}
    return {"pattern_confirmed": False}
```

#### Phase 2: Position Building with Limits
```python
def execute_averaging_down(symbol, max_multiplier, current_position):
    # Calculate safe position size
    additional_shares = min(
        current_position.qty * max_multiplier,
        available_buying_power * 0.1,  # Max 10% of buying power
        10000 / current_anomalous_price  # Max $10K position
    )
    
    # Execute limit order at anomalous low
    order = place_stock_order(
        symbol=symbol,
        side="buy",
        quantity=additional_shares,
        order_type="limit",
        limit_price=get_best_bid_price(),
        extended_hours=True
    )
```

#### Phase 3: Lightning Fast Exit
```python
def execute_profit_exit(symbol, new_avg_cost, profit_target_cents):
    exit_price = new_avg_cost + (profit_target_cents / 100)
    
    while True:
        stream_data = get_stock_stream_data(symbol, "quotes", recent_seconds=3)
        current_bid = stream_data.current_bid
        
        if current_bid >= exit_price:
            # IMMEDIATE EXECUTION - NO HESITATION
            sell_order = place_stock_order(
                symbol=symbol,
                side="sell",
                quantity=total_position_size,
                order_type="limit",
                limit_price=current_bid,
                extended_hours=True
            )
            break
        
        time.sleep(2)  # Check every 2 seconds
```

### 📋 EMERGENCY SAFETY MECHANISMS

#### Position Size Protection
```python
MAX_POSITION_MULTIPLIERS = {
    "conservative": 2,
    "moderate": 3,
    "aggressive": 5
}

MAX_CAPITAL_RISK = 0.15  # Never risk more than 15% of account
```

#### Time-Based Exits
- Maximum 45 minutes from start to finish
- Force exit if time limit reached

#### Emergency Stop Loss
- 5% stop loss below new average cost
- Immediate market exit if triggered

---

## Performance Tracking

### 📊 Trade Documentation Template

For every trade, document:
```
TRADE LOG:
Symbol: 
Entry Signal: Trough at $X.XX
Entry Fill: $X.XX (VERIFIED)
Position Size: X shares ($XX,XXX)
Peak Signal: $X.XX
Exit Fill: $X.XX
Profit/Loss: $XXX
Peak Accuracy: Did I wait for peak? Y/N
Size Accuracy: Correct position size? Y/N
Speed Score: Exit within target time? Y/N
```

### 🎯 Success Metrics

#### Target Performance
- **Win Rate:** 70%+ (take small profits consistently)
- **Average Profit:** $100-$500 per trade
- **Time to Exit:** 15-45 minutes maximum
- **Risk/Reward:** 1:2 minimum (risk 2¢ to make 4¢)

#### Red Flags to Stop Strategy
- Win rate drops below 60%
- Average holding time exceeds 1 hour
- Stop losses triggered > 20% of trades
- Extended hours liquidity issues

### 📈 Daily Performance Context

#### Ready to Trade Verification
- [ ] ✅ Server health: All systems operational
- [ ] ✅ Market status: Trading session confirmed
- [ ] ✅ Account verified: Adequate buying power, no restrictions
- [ ] ✅ Data feeds: Low latency, high quality streaming
- [ ] ✅ **Liquidity scanner: trades_per_minute.sh executed**
- [ ] ✅ **Qualified targets: Only 500+ trades/minute stocks**
- [ ] ✅ Technical analysis: Peak/trough signals ready
- [ ] ✅ No stale positions/orders: Clean starting state
- [ ] ✅ Risk rules reviewed: Position sizing confirmed

---

## Streaming Operations

### 🌊 Alpaca Stream Script

The Alpaca Stream script is a comprehensive tool for connecting to Alpaca's WebSocket streaming data service. It provides access to real-time market data, allowing you to stream various data types for multiple stock symbols with minimal latency.

#### Features

1. **Multiple Data Types**:
   - Trades: Real-time trade data for stocks
   - Quotes: Bid/ask prices and sizes
   - Minute Bars: 1-minute OHLC candlestick data
   - Updated Bars: Corrections to previously sent minute bars
   - Daily Bars: Daily OHLC candlestick data
   - Trading Statuses: Updates on trading halts and resumptions
   - Trade Corrections and Cancellations: Fixes to previously reported trades

2. **Command-Line Arguments**:
   - `--data-type`: Type of data to stream (trades, quotes, bars, etc.)
   - `--symbols`: List of stock symbols to subscribe to
   - `--symbols-file`: Path to a file containing symbols (one per line)
   - `--feed`: Data feed to use (iex or sip)
   - `--raw`: Option to output raw data instead of formatted data
   - `--duration`: How long to run the script (in seconds)
   - `--silent-timeout`: Seconds without messages before reconnecting

3. **Environment Variables**:
   - Uses `APCA_API_KEY_ID` and `APCA_API_SECRET_KEY` as required

4. **Robust Implementation**:
   - Automatic reconnection system with exponential backoff
   - Proper signal handling for graceful shutdown
   - Asynchronous processing for better performance
   - Event counting for statistics
   - Comprehensive error handling

#### Reconnection System

The script includes an intelligent automatic reconnection system that:

- Monitors the time since the last received message
- Detects stalled connections when no data is received
- Implements exponential backoff for reconnection attempts
- Re-applies all subscriptions after reconnection
- Provides configurable parameters for fine-tuning

#### Symbol Management

The script offers flexible symbol management:

- Command-line symbol specification
- Loading symbols from a text file (one per line)
- Combining symbols from both sources
- Automatic deduplication
- Case-insensitive symbol handling

#### Usage Examples

```bash
# Stream trades for Apple, Microsoft, and Tesla (using SIP feed)
python alpaca_stream.py --data-type trades --symbols AAPL MSFT TSLA

# Stream quotes for Apple using the SIP feed
python alpaca_stream.py --data-type quotes --symbols AAPL --feed sip

# Stream minute bars for SPY and QQQ using IEX feed
python alpaca_stream.py --data-type bars --symbols SPY QQQ --feed iex

# Stream all data types for Apple
python alpaca_stream.py --data-type all --symbols AAPL

# Run for 5 minutes
python alpaca_stream.py --data-type trades --symbols AAPL --duration 300

# Output raw data for debugging
python alpaca_stream.py --data-type trades --symbols AAPL --raw

# Load symbols from a file
python alpaca_stream.py --data-type trades --symbols-file tech_stocks.txt

# Combine file symbols with additional command-line symbols
python alpaca_stream.py --data-type quotes --symbols-file sp500.txt --symbols AAPL MSFT

# Customize reconnection timeout (reconnect after 15 seconds of silence)
python alpaca_stream.py --data-type trades --symbols AAPL --silent-timeout 15
```

#### Output Format

The script formats the output for each data type in a readable format:

**Trades**:
```
Trade: AAPL @ $150.25 - Size: 100 - Exchange: P - Timestamp: 2023-05-25T14:30:25.123456+00:00
```

**Quotes**:
```
Quote: MSFT - Bid: $270.10 x 500 - Ask: $270.15 x 300 - Timestamp: 2023-05-25T14:30:25.123456+00:00
```

**Bars**:
```
Bar: SPY - O: $410.25 H: $410.50 L: $410.10 C: $410.45 - Volume: 5000 - Timestamp: 2023-05-25T14:30:00+00:00
```

When using the `--raw` option, the script outputs the raw data objects for more detailed inspection.

#### Statistics

At the end of the run, the script displays statistics on the number of events received for each data type:

```
Event counters:
  trades: 1250
  quotes: 0
  bars: 0
```

#### Integration

This script is designed to work alongside the TradeManager component, providing the real-time market data needed for optimal trade execution. The two components can be used together for a complete high-frequency trading system:

- **Alpaca Stream Script**: Provides real-time market data
- **TradeManager**: Executes trades with optimal timing

Together, these components form the foundation of a robust, high-performance trading system for volatile markets.

---

## Tools Access Guide

There are now **multiple ways** to discover and use the available tools in the Alpaca MCP Server:

### 📋 **Complete Tools Reference**

**Full Documentation: `MCP_TOOLS_REFERENCE.md`**
- Comprehensive reference with 45+ tools
- Detailed parameters and examples
- Organized by trading categories
- Complete usage patterns and workflows

### 🚀 **Quick Access Methods**

#### **1. Slash Commands (Recommended)**

Type these commands directly in Claude Code:

- **`/tools`** - List all available tools with descriptions
- **`/trading`** - Day trading tools quick reference  
- **`/analysis`** - Technical analysis tools and parameters

**How it works:** Slash commands are stored in `.claude/commands/` folder and become available in Claude Code when you type `/`

#### **2. MCP Prompt**

Use the MCP prompt function:

```
list_all_tools()
```

**What it does:** Returns a formatted reference of all available tools organized by category with examples

#### **3. Direct Tool Categories**

**Account & Portfolio:**
- `get_account_info()`, `get_positions()`, `close_position()`

**Market Data:**
- `get_stock_quote()`, `get_stock_snapshots()`, `get_stock_bars_intraday()`

**🔥 Technical Analysis:**
- `get_stock_peak_trough_analysis()` - **NEW** Peak/trough analysis tool

**Order Management:**
- `place_stock_order()`, `get_orders()`, `cancel_all_orders()`

**Streaming Data:**
- `start_global_stock_stream()`, `get_stock_stream_data()`

### 🎯 **Recommended Usage**

#### **For New Users:**
1. Start with `/tools` slash command for overview
2. Use `list_all_tools()` MCP prompt for detailed reference
3. Check `MCP_TOOLS_REFERENCE.md` for complete documentation

#### **For Day Trading:**
1. Use `/trading` slash command for essential workflow
2. Focus on `get_stock_peak_trough_analysis()` for entry points
3. Use streaming tools for real-time monitoring

#### **For Technical Analysis:**
1. Use `/analysis` slash command for analysis tools
2. Experiment with different parameters for `get_stock_peak_trough_analysis()`
3. Combine with streaming data for live signals

### 📚 **Documentation Hierarchy**

1. **Quick Access:** Slash commands (`/tools`, `/trading`, `/analysis`)
2. **Interactive:** MCP prompt (`list_all_tools()`)
3. **Complete Reference:** `MCP_TOOLS_REFERENCE.md` file
4. **Specific Tool:** `PEAK_TROUGH_ANALYSIS_TOOL.md` for detailed technical analysis

### 🛠 **Implementation Details**

#### **Slash Commands Location:**
```
.claude/commands/
├── tools.md          # Complete tools listing
├── trading.md        # Day trading workflow
└── analysis.md       # Technical analysis tools
```

#### **MCP Server Registration:**
- **Tools:** Registered with `@mcp.tool()` decorator
- **Prompts:** Registered with `@mcp.prompt()` decorator
- **Access:** Available through Claude Desktop, Cursor, VSCode

#### **Tool Naming Convention:**
All stock-related tools follow the pattern:
- `get_stock_*` - Data retrieval tools
- `place_stock_*` - Order placement tools  
- `start_*_stock_*` - Streaming tools

### 🎉 **New Features Highlighted**

#### **Peak/Trough Analysis Tool**
- **Function:** `get_stock_peak_trough_analysis()`
- **Purpose:** Zero-phase Hanning filtering + peak detection
- **Trading Integration:** Perfect for "SCAN LONGER before entry" lesson
- **Returns:** BUY/LONG and SELL/SHORT signals with precise price levels

#### **Multiple Access Methods**
- **Slash Commands:** Quick workflow references
- **MCP Prompts:** Interactive tool listing
- **Complete Docs:** Comprehensive reference guide

### 💡 **Pro Tips**

1. **Bookmark** `/tools` for quick reference during trading
2. **Use** `get_stock_peak_trough_analysis()` before entering positions
3. **Combine** multiple tools for complete trading workflows
4. **Check** `health_check()` before starting trading sessions
5. **Always use** limit orders with `place_stock_order()`

This multi-layered approach ensures users can quickly find the right tools for their trading needs, whether they want a quick reference or complete documentation.

---

## Tool Usage Patterns

### Day Trading Workflow
1. **Market Analysis**: `get_market_clock()` → `get_stock_snapshots("CGTL,HCTI")`
2. **Technical Analysis**: `get_stock_peak_trough_analysis("CGTL", timeframe="1Min")`
3. **Streaming Setup**: `start_global_stock_stream(["CGTL"], ["trades", "quotes"])`
4. **Order Placement**: `place_stock_order("CGTL", "buy", 1000, "limit", limit_price=1.25)`
5. **Monitoring**: `get_stock_stream_data("CGTL", "trades", recent_seconds=60)`
6. **Position Management**: `get_positions()` → `close_position("CGTL", percentage="100")`

### Options Trading Workflow
1. **Find Contracts**: `get_option_contracts("AAPL", type="call")`
2. **Get Quotes**: `get_option_latest_quote("AAPL230616C00150000")`
3. **Place Order**: `place_option_market_order([{"symbol": "AAPL230616C00150000", "side": "buy"}])`

### Portfolio Management
1. **Account Review**: `get_account_info()` → `get_positions()`
2. **Performance**: `resource_intraday_pnl()` → `resource_current_positions()`
3. **Risk Management**: `get_orders("open")` → `cancel_all_orders()`

### 60-Second Monitoring Cycle
1. **Analysis Cycle**: `get_stock_snapshots("USEG")` + `get_stock_peak_trough_analysis("USEG")`
2. **Signal Detection**: Check for trough/buy signals
3. **Real-Time Entry**: `get_stock_stream_data("USEG", "quotes")` for optimal pricing
4. **Order Execution**: `place_stock_order()` with streaming-derived limit price
5. **Aggressive Monitoring**: Watch order fill until executed

---

## Getting Started

1. **Check System**: `health_check()` → `get_market_clock()`
2. **Review Account**: `get_account_info()` → `get_positions()`
3. **Market Data**: `get_stock_quote("AAPL")` → `get_stock_snapshots("AAPL,MSFT")`
4. **Technical Analysis**: `get_stock_peak_trough_analysis("AAPL")`
5. **Place Trade**: `place_stock_order("AAPL", "buy", 1, "limit", limit_price=150.00)`

This comprehensive tool set provides everything needed for professional algorithmic trading, from basic market data to advanced technical analysis and order management.

---

## 🚀 Day Trading Flow Ready

1. **Scanner** → Use `./trades_per_minute.sh -f combined.lis -t 500`
2. **Filter** → Only trade stocks with 1000+ trades/minute (500+ minimum)
3. **Analysis** → Use `get_stock_peak_trough_analysis()` for entry signals  
4. **Streaming** → Start `start_global_stock_stream()` for real-time monitoring
5. **Execute** → Place limit orders with `place_stock_order()`
6. **Monitor** → Check fills and track with streaming data
7. **Exit** → Follow peak/trough signals for rising trends, immediate exit for declining peaks

---

**🚀 ONLY BEGIN DAY TRADING WHEN ALL ITEMS ARE CHECKED ✅**

**Remember:** Speed + Signals = Success. Follow the tools, trust the process, document everything.

---

*Built from real trading sessions and lessons learned. Updated June 15, 2025.*
