# Alpaca MCP Server - Complete Tools Reference

This document provides a comprehensive reference for all available tools in the Alpaca MCP (Model Context Protocol) Server. These tools enable programmatic access to Alpaca's trading platform for account management, market data, trading operations, and analysis.

## Quick Tool Categories

- **[Account & Portfolio](#account--portfolio-management)** - Account info, positions, balances
- **[Market Data](#market-data--quotes)** - Real-time quotes, historical data, snapshots
- **[Technical Analysis](#technical-analysis)** - Peak/trough analysis, trading signals
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

---

## Getting Started

1. **Check System**: `health_check()` → `get_market_clock()`
2. **Review Account**: `get_account_info()` → `get_positions()`
3. **Market Data**: `get_stock_quote("AAPL")` → `get_stock_snapshots("AAPL,MSFT")`
4. **Technical Analysis**: `get_stock_peak_trough_analysis("AAPL")`
5. **Place Trade**: `place_stock_order("AAPL", "buy", 1, "limit", limit_price=150.00)`

This comprehensive tool set provides everything needed for professional algorithmic trading, from basic market data to advanced technical analysis and order management.