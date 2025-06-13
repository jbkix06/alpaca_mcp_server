"""Main MCP server implementation with prompt-driven architecture."""

from mcp.server.fastmcp import FastMCP
from .config.settings import settings

# Import all tool modules
from .tools import (
    account_tools,
    position_tools,
    order_tools,
    market_data_tools,
    market_info_tools,
    options_tools,
    watchlist_tools,
    asset_tools,
    corporate_action_tools,
    streaming_tools,
)
from .tools.peak_trough_analysis_tool import (
    analyze_peaks_and_troughs as peak_trough_analysis,
)

# Import modules will be done locally in tool functions to avoid name conflicts

# Import all prompt modules
from .prompts import (
    list_trading_capabilities as ltc_module,
    account_analysis_prompt,
    position_management_prompt,
    market_analysis_prompt,
    tools_reference_prompt,
    startup_prompt,
    scan_prompt,
)

# Import resource modules
from .resources import (
    account_resources,
    market_resources,
    position_resources,
    portfolio_resources,
    streaming_resources,
    market_momentum,
    intraday_pnl,
    data_quality,
    server_health,
    session_status,
    api_monitor,
)

# Create the FastMCP server instance
mcp = FastMCP(
    name=settings.server_name,
    version=settings.version,
    dependencies=["alpaca-py>=0.40.1", "python-dotenv>=1.1.0"],
)

# ============================================================================
# PROMPTS - Guided Trading Workflows (Highest Leverage)
# ============================================================================


@mcp.prompt()
async def list_trading_capabilities() -> str:
    """List all Alpaca trading capabilities with guided workflows."""
    return await ltc_module.list_trading_capabilities()


@mcp.prompt()
async def account_analysis() -> str:
    """Complete portfolio health check with actionable insights."""
    return await account_analysis_prompt.account_analysis()


@mcp.prompt()
async def position_management(symbol: str = None) -> str:
    """Strategic position review and optimization."""
    return await position_management_prompt.position_management(symbol)


@mcp.prompt()
async def market_analysis(
    symbols: list = None, timeframe: str = "1Day", analysis_type: str = "comprehensive"
) -> str:
    """Real-time market analysis with trading opportunities."""
    return await market_analysis_prompt.market_analysis(
        symbols, timeframe, analysis_type
    )


@mcp.prompt()
async def list_all_tools() -> str:
    """List all available MCP tools with descriptions and usage examples."""
    return await tools_reference_prompt.list_all_tools()


# Duplicate registration removed - see line 925 for the actual startup prompt


# ============================================================================
# TOOLS - Individual Trading Actions (Composed by Prompts)
# ============================================================================


# Account & Position Management Tools
@mcp.tool()
async def get_account_info() -> str:
    """Get current account information including balances and status."""
    return await account_tools.get_account_info()


@mcp.tool()
async def get_positions() -> str:
    """Get all current positions in the portfolio."""
    return await account_tools.get_positions()


@mcp.tool()
async def get_open_position(symbol: str) -> str:
    """Get details for a specific open position."""
    return await account_tools.get_open_position(symbol)


@mcp.tool()
async def close_position(symbol: str, qty: str = None, percentage: str = None) -> str:
    """Close a specific position."""
    return await position_tools.close_position(symbol, qty, percentage)


@mcp.tool()
async def close_all_positions(cancel_orders: bool = False) -> str:
    """Close all open positions."""
    return await position_tools.close_all_positions(cancel_orders)


# Market Data Tools
@mcp.tool()
async def get_stock_quote(symbol: str) -> str:
    """Get latest quote for a stock."""
    return await market_data_tools.get_stock_quote(symbol)


@mcp.tool()
async def get_stock_snapshots(symbols: str) -> str:
    """Get comprehensive market snapshots."""
    return await market_data_tools.get_stock_snapshots(symbols)


@mcp.tool()
async def get_stock_bars(symbol: str, days: int = 5) -> str:
    """Get historical price bars."""
    return await market_data_tools.get_stock_bars(symbol, days)


@mcp.tool()
async def get_stock_bars_intraday(
    symbol: str,
    timeframe: str = "1Min",
    start_date: str = None,
    end_date: str = None,
    limit: int = 10000,
) -> str:
    """Get intraday historical bars with analysis."""
    return await market_data_tools.get_stock_bars_intraday(
        symbol, timeframe, start_date, end_date, limit
    )


@mcp.tool()
async def get_stock_trades(symbol: str, days: int = 5, limit: int = None) -> str:
    """Get recent trades for a stock."""
    return await market_data_tools.get_stock_trades(symbol, days, limit)


@mcp.tool()
async def get_stock_latest_trade(symbol: str) -> str:
    """Get the latest trade for a stock."""
    return await market_data_tools.get_stock_latest_trade(symbol)


@mcp.tool()
async def get_stock_latest_bar(symbol: str) -> str:
    """Get the latest minute bar for a stock."""
    return await market_data_tools.get_stock_latest_bar(symbol)


# Market Info Tools
@mcp.tool()
async def get_market_clock() -> str:
    """Get current market status and next open/close times."""
    return await market_info_tools.get_market_clock()


@mcp.tool()
async def get_market_calendar(start_date: str, end_date: str) -> str:
    """Get market calendar for specified date range."""
    return await market_info_tools.get_market_calendar(start_date, end_date)


# Options Tools
@mcp.tool()
async def get_option_contracts(
    underlying_symbol: str,
    expiration_date: str = None,
    strike_price_gte: str = None,
    strike_price_lte: str = None,
    type: str = None,
    limit: int = None,
) -> str:
    """Get option contracts for underlying symbol."""
    return await options_tools.get_option_contracts(
        underlying_symbol,
        expiration_date,
        strike_price_gte,
        strike_price_lte,
        type,
        None,
        None,
        limit,
    )


@mcp.tool()
async def get_option_latest_quote(symbol: str) -> str:
    """Get latest quote for an option contract."""
    return await options_tools.get_option_latest_quote(symbol)


@mcp.tool()
async def get_option_snapshot(symbol: str) -> str:
    """Get comprehensive option snapshot with Greeks."""
    return await options_tools.get_option_snapshot(symbol)


# Stock Technical Analysis Tool
@mcp.tool()
async def get_stock_peak_trough_analysis(
    symbols: str,
    timeframe: str = "1Min",
    days: int = 1,
    limit: int = 1000,
    window_len: int = 11,
    lookahead: int = 1,
    delta: float = 0.0,
    min_peak_distance: int = 5,
) -> str:
    """
    Get stock peak and trough analysis for day trading signals using zero-phase Hanning filtering.

    This professional technical analysis tool:
    1. Fetches intraday bar data for specified symbols
    2. Applies zero-phase low-pass Hanning filtering to remove noise
    3. Detects peaks/troughs using advanced algorithms
    4. Returns precise entry/exit levels for day trading

    Perfect for identifying support/resistance levels and timing entries based on
    yesterday's trading lessons: "SCAN LONGER before entry" - this tool provides
    the technical analysis to find optimal entry points.

    Args:
        symbols: Stock symbols (e.g., "CGTL" or "AAPL,MSFT,NVDA")
        timeframe: "1Min", "5Min", "15Min", "30Min", "1Hour" (default: "1Min")
        days: Historical days to analyze (1-30, default: 1)
        limit: Max bars to fetch (1-10000, default: 1000)
        window_len: Hanning filter smoothing (3-101, default: 11)
        lookahead: Peak detection sensitivity (1-50, default: 1)
        delta: Minimum peak amplitude (default: 0.0 for penny stocks)
        min_peak_distance: Min bars between peaks (default: 5)

    Returns detailed analysis with BUY/LONG and SELL/SHORT signals.
    """
    return await peak_trough_analysis(
        symbols, timeframe, days, limit, window_len, lookahead, delta, min_peak_distance
    )


# Day Trading Scanner Tools
@mcp.tool()
async def scan_day_trading_opportunities(
    symbols: str = "SPY,QQQ,IWM,AAPL,MSFT,NVDA,TSLA,AMC,GME,PLTR,SOFI,RIVN,LCID,NIO,XPEV,BABA,META,GOOGL,AMZN,NFLX",
    min_trades_per_minute: int = 50,
    min_percent_change: float = 5.0,
    max_symbols: int = 20,
    sort_by: str = "trades",
) -> str:
    """
    Scan for active day-trading opportunities using real-time market snapshots.

    Focused on two key metrics from professional trading analysis:
    1. Trades per minute (activity/liquidity indicator)
    2. Percent change (momentum indicator)

    Perfect for finding explosive moves like NEHC and high-activity stocks for day trading.
    Uses existing get_stock_snapshots tool for real-time data.

    Args:
        symbols: Comma-separated symbols to scan (default: popular day-trading stocks)
        min_trades_per_minute: Minimum trades in current minute bar (default: 50)
        min_percent_change: Minimum absolute % change from reference (default: 5.0%)
        max_symbols: Maximum results to return (default: 20)
        sort_by: Sort results by "trades", "percent_change", or "volume"

    Returns:
        Formatted analysis with top day-trading opportunities ranked by activity and momentum.
    """
    from .tools.day_trading_scanner import (
        scan_day_trading_opportunities as scanner_func,
    )

    return await scanner_func(
        symbols, min_trades_per_minute, min_percent_change, max_symbols, sort_by
    )


@mcp.tool()
async def scan_explosive_momentum(
    symbols: str = "CVAC,CGTL,GNLN,NEHC,SOUN,RIOT,MARA,COIN,HOOD,RBLX",
    min_percent_change: float = 15.0,
) -> str:
    """
    Quick scanner for explosive momentum moves like NEHC.

    Optimized for finding extreme percentage movers with high activity.
    Lower trade threshold but higher % change requirement for explosive stocks.

    Args:
        symbols: Comma-separated symbols (default: volatile/momentum stocks)
        min_percent_change: Minimum absolute % change (default: 15.0% for explosive moves)

    Returns:
        Top explosive momentum opportunities sorted by % change.
    """
    from .tools.day_trading_scanner import scan_explosive_momentum as explosive_func

    return await explosive_func(symbols, min_percent_change)


# Differential Trade Scanner Tools (Background Scanner Like C Program)
@mcp.tool()
async def start_differential_trade_scanner(
    symbols: str = "SPY,QQQ,AAPL,MSFT,NVDA,TSLA,AMC,GME,PLTR,NIVF,HCTI,GNLN,IXHL,CVAC,CGTL",
    min_trades_per_minute: int = 50,
    min_percent_change: float = 5.0,
    update_interval: int = 60,
    max_symbols: int = 20,
) -> str:
    """
    Start the differential trade scanner in the background (like the C program).

    This mirrors the C program functionality:
    1. Takes snapshots every 60 seconds
    2. Calculates exact trade count differences
    3. Caches previous values for comparison
    4. Runs continuously in background

    Perfect for continuous monitoring of trade activity using exact differential calculations
    like the stock_analyzer.c program. Extracts trade counts from minute bar 'n' field.

    Args:
        symbols: Comma-separated symbols to monitor
        min_trades_per_minute: Minimum trade count difference to include
        min_percent_change: Minimum % change to include
        update_interval: Seconds between scans (default: 60)
        max_symbols: Maximum results to track

    Returns:
        Status message about scanner startup
    """
    return await start_differential_trade_scanner(
        symbols, min_trades_per_minute, min_percent_change, update_interval, max_symbols
    )


@mcp.tool()
async def stop_differential_trade_scanner() -> str:
    """
    Stop the background differential trade scanner.

    Gracefully stops the background scanner while preserving the cache
    for next startup (like the C program's cache persistence).

    Returns:
        Status message about scanner shutdown
    """
    return await stop_differential_trade_scanner()


@mcp.tool()
async def get_differential_trade_results(
    sort_by: str = "trades_change", max_results: int = 20
) -> str:
    """
    Get the latest results from the differential trade scanner.

    Returns live results from the background scanner with exact trade count
    differences calculated like the C program methodology.

    Args:
        sort_by: Sort by "trades_change", "percent_change", or "volume_change"
        max_results: Maximum results to return

    Returns:
        Formatted results like the C program's HTML output with exact trade counts
    """
    return await get_differential_trade_results(sort_by, max_results)


@mcp.tool()
async def get_differential_scanner_status() -> str:
    """
    Get the current status of the differential trade scanner.

    Shows scanner health, cache size, last scan time, and background task status.
    Perfect for monitoring the background scanner's operation like the C program.

    Returns:
        Comprehensive status information about the differential scanner
    """
    return await get_differential_scanner_status()


# After-Hours and Enhanced Analytics Tools
@mcp.tool()
async def scan_after_hours_opportunities(
    symbols: str = "AAPL,MSFT,NVDA,TSLA,GOOGL,AMZN,META,NFLX,COIN,HOOD,AMC,GME,PLTR,SOFI,RIVN,LCID",
    min_volume: int = 100000,
    min_percent_change: float = 2.0,
    max_symbols: int = 15,
    sort_by: str = "percent_change",
) -> str:
    """
    Scan for after-hours trading opportunities with enhanced analytics.

    Focuses on:
    1. Extended hours price movements
    2. Volume analysis relative to average
    3. News-driven momentum detection
    4. Liquidity assessment for safe entry/exit

    Args:
        symbols: Comma-separated symbols for after-hours scanning
        min_volume: Minimum after-hours volume threshold
        min_percent_change: Minimum % change from regular session close
        max_symbols: Maximum results to return
        sort_by: Sort results by "percent_change", "volume", or "price"

    Returns:
        Formatted analysis of after-hours opportunities
    """
    from .tools.after_hours_scanner import (
        scan_after_hours_opportunities as scanner_func,
    )

    return await scanner_func(
        symbols, min_volume, min_percent_change, max_symbols, sort_by
    )


@mcp.tool()
async def get_enhanced_streaming_analytics(
    symbol: str, analysis_minutes: int = 15, include_orderbook: bool = True
) -> str:
    """
    Enhanced streaming analytics with real-time calculations.

    Provides:
    1. Real-time momentum analysis
    2. Volume-weighted average price (VWAP)
    3. Order flow analysis
    4. Support/resistance detection
    5. Volatility measurements

    Args:
        symbol: Stock symbol to analyze
        analysis_minutes: Minutes of historical data to include
        include_orderbook: Include bid/ask analysis

    Returns:
        Comprehensive real-time analytics
    """
    from .tools.after_hours_scanner import (
        get_enhanced_streaming_analytics as analytics_func,
    )

    return await analytics_func(symbol, analysis_minutes, include_orderbook)


# Watchlist Tools
@mcp.tool()
async def create_watchlist(name: str, symbols: list) -> str:
    """Create a new watchlist with specified symbols."""
    return await watchlist_tools.create_watchlist(name, symbols)


@mcp.tool()
async def get_watchlists() -> str:
    """Get all watchlists for the account."""
    return await watchlist_tools.get_watchlists()


@mcp.tool()
async def update_watchlist(
    watchlist_id: str, name: str = None, symbols: list = None
) -> str:
    """Update an existing watchlist."""
    return await watchlist_tools.update_watchlist(watchlist_id, name, symbols)


# Asset Tools
@mcp.tool()
async def get_all_assets(
    status: str = None,
    asset_class: str = None,
    exchange: str = None,
    attributes: str = None,
) -> str:
    """Get all available assets with optional filtering."""
    return await asset_tools.get_all_assets(status, asset_class, exchange, attributes)


@mcp.tool()
async def get_asset_info(symbol: str) -> str:
    """Get detailed information about a specific asset."""
    return await asset_tools.get_asset_info(symbol)


# Corporate Actions Tools
@mcp.tool()
async def get_corporate_announcements(
    ca_types: list,
    since: str,
    until: str,
    symbol: str = None,
    cusip: str = None,
    date_type: str = None,
) -> str:
    """Get corporate action announcements for specified criteria."""
    return await corporate_action_tools.get_corporate_announcements(
        ca_types, since, until, symbol, cusip, date_type
    )


# Real-time Streaming Tools (Critical for Day Trading)
@mcp.tool()
async def start_global_stock_stream(
    symbols: list,
    data_types: list = ["trades", "quotes"],
    feed: str = "sip",
    duration_seconds: int = None,
    buffer_size_per_symbol: int = None,
    replace_existing: bool = False,
) -> str:
    """Start global real-time stock data stream for day trading."""
    return await streaming_tools.start_global_stock_stream(
        symbols,
        data_types,
        feed,
        duration_seconds,
        buffer_size_per_symbol,
        replace_existing,
    )


@mcp.tool()
async def stop_global_stock_stream() -> str:
    """Stop the global stock streaming session."""
    return await streaming_tools.stop_global_stock_stream()


@mcp.tool()
async def add_symbols_to_stock_stream(symbols: list, data_types: list = None) -> str:
    """Add symbols to existing stock stream."""
    return await streaming_tools.add_symbols_to_stock_stream(symbols, data_types)


@mcp.tool()
async def get_stock_stream_data(
    symbol: str, data_type: str, recent_seconds: int = None, limit: int = None
) -> str:
    """Get streaming data for analysis."""
    return await streaming_tools.get_stock_stream_data(
        symbol, data_type, recent_seconds, limit
    )


@mcp.tool()
async def list_active_stock_streams() -> str:
    """List all active streaming subscriptions."""
    return await streaming_tools.list_active_stock_streams()


@mcp.tool()
async def get_stock_stream_buffer_stats() -> str:
    """Get detailed streaming buffer statistics."""
    return await streaming_tools.get_stock_stream_buffer_stats()


@mcp.tool()
async def clear_stock_stream_buffers() -> str:
    """Clear streaming buffers to free memory."""
    return await streaming_tools.clear_stock_stream_buffers()


# Order Management Tools
@mcp.tool()
async def place_stock_order(
    symbol: str,
    side: str,
    quantity: float,
    order_type: str = "market",
    time_in_force: str = "day",
    limit_price: float = None,
    stop_price: float = None,
    trail_price: float = None,
    trail_percent: float = None,
    extended_hours: bool = False,
    client_order_id: str = None,
) -> str:
    """Place a stock order of any type."""
    return await order_tools.place_stock_order(
        symbol,
        side,
        quantity,
        order_type,
        time_in_force,
        limit_price,
        stop_price,
        trail_price,
        trail_percent,
        extended_hours,
        client_order_id,
    )


@mcp.tool()
async def get_orders(status: str = "all", limit: int = 10) -> str:
    """Get orders with specified status."""
    return await order_tools.get_orders(status, limit)


@mcp.tool()
async def cancel_order_by_id(order_id: str) -> str:
    """Cancel a specific order by ID."""
    return await order_tools.cancel_order_by_id(order_id)


@mcp.tool()
async def cancel_all_orders() -> str:
    """Cancel all open orders."""
    return await order_tools.cancel_all_orders()


@mcp.tool()
async def place_option_market_order(
    legs: list, order_class: str = None, quantity: int = 1
) -> str:
    """Place single or multi-leg options market order."""
    return await order_tools.place_option_market_order(legs, order_class, quantity)


# ============================================================================
# RESOURCES - Dynamic Trading Context
# ============================================================================


@mcp.resource("account://status")
async def get_account_status() -> dict:
    """Real-time account health and trading capacity."""
    return await account_resources.get_account_status()


@mcp.resource("positions://current")
async def get_current_positions() -> dict:
    """Live position data with P&L updates."""
    return await position_resources.get_current_positions()


@mcp.resource("market://conditions")
async def get_market_conditions() -> dict:
    """Current market status and conditions."""
    return await market_resources.get_market_conditions()


@mcp.resource("portfolio://performance")
async def get_portfolio_performance() -> dict:
    """Real-time portfolio performance metrics and P&L analysis."""
    return await portfolio_resources.get_portfolio_performance()


@mcp.resource("portfolio://allocation")
async def get_portfolio_allocation() -> dict:
    """Asset allocation breakdown with winners/losers analysis."""
    return await portfolio_resources.get_portfolio_allocation()


@mcp.resource("portfolio://risk")
async def get_portfolio_risk() -> dict:
    """Portfolio risk metrics and exposure analysis."""
    return await portfolio_resources.get_portfolio_risk()


@mcp.resource("streams://status")
async def get_stream_status() -> dict:
    """Real-time streaming status and buffer statistics."""
    return await streaming_resources.get_stream_status()


@mcp.resource("streams://performance")
async def get_stream_performance() -> dict:
    """Streaming performance metrics and health indicators."""
    return await streaming_resources.get_stream_performance()


@mcp.resource("market://momentum")
async def get_market_momentum_resource() -> dict:
    """Real-time market momentum for SPY with default parameters."""
    return await market_momentum.get_market_momentum()


@mcp.resource("positions://intraday_pnl")
async def get_intraday_pnl_resource() -> dict:
    """Track today's intraday P&L with default parameters."""
    return await intraday_pnl.get_intraday_pnl()


@mcp.resource("data://quality")
async def get_data_quality_resource() -> dict:
    """Monitor data feed quality with default parameters."""
    return await data_quality.get_data_quality()


@mcp.resource("server://health")
async def get_server_health_resource() -> dict:
    """Comprehensive server health monitoring."""
    return await server_health.get_server_health()


@mcp.resource("server://session")
async def get_session_status_resource() -> dict:
    """Trading session and market status."""
    return await session_status.get_session_status()


@mcp.resource("server://apis")
async def get_api_status_resource() -> dict:
    """Monitor API connections and performance."""
    return await api_monitor.get_api_status()


# ============================================================================
# RESOURCE MIRROR TOOLS - For Claude Code Compatibility
# ============================================================================


@mcp.tool()
async def resource_account_status() -> dict:
    """Tool mirror of account://status resource."""
    return await account_resources.get_account_status()


@mcp.tool()
async def resource_current_positions() -> dict:
    """Tool mirror of positions://current resource."""
    return await position_resources.get_current_positions()


@mcp.tool()
async def resource_market_conditions() -> dict:
    """Tool mirror of market://conditions resource."""
    return await market_resources.get_market_conditions()


@mcp.tool()
async def resource_market_momentum(
    symbol: str = "SPY",
    timeframe_minutes: int = 1,
    analysis_hours: int = 2,
    sma_short: int = 5,
    sma_long: int = 20,
) -> dict:
    """Tool mirror of market://momentum resource."""
    return await market_momentum.get_market_momentum(
        symbol=symbol,
        timeframe_minutes=timeframe_minutes,
        analysis_hours=analysis_hours,
        sma_short=sma_short,
        sma_long=sma_long,
    )


@mcp.tool()
async def resource_intraday_pnl(
    days_back: int = 0,
    include_open_positions: bool = True,
    min_trade_value: float = 0.0,
    symbol_filter: str = None,
) -> dict:
    """Tool mirror of positions://intraday_pnl resource."""
    return await intraday_pnl.get_intraday_pnl(
        days_back=days_back,
        include_open_positions=include_open_positions,
        min_trade_value=min_trade_value,
        symbol_filter=symbol_filter,
    )


@mcp.tool()
async def resource_data_quality(
    test_symbols: list = None,
    latency_threshold_ms: float = 500.0,
    quote_age_threshold_seconds: float = 60.0,
    spread_threshold_pct: float = 1.0,
) -> dict:
    """Tool mirror of data://quality resource."""
    return await data_quality.get_data_quality(
        test_symbols=test_symbols,
        latency_threshold_ms=latency_threshold_ms,
        quote_age_threshold_seconds=quote_age_threshold_seconds,
        spread_threshold_pct=spread_threshold_pct,
    )


@mcp.tool()
async def resource_server_health() -> dict:
    """Tool mirror of server://health resource."""
    return await server_health.get_server_health()


@mcp.tool()
async def resource_session_status() -> dict:
    """Tool mirror of server://session resource."""
    return await session_status.get_session_status()


@mcp.tool()
async def resource_api_status() -> dict:
    """Tool mirror of server://apis resource."""
    return await api_monitor.get_api_status()


@mcp.tool()
async def health_check() -> str:
    """Quick server health and status check."""
    try:
        health = await server_health.get_server_health()
        session = await session_status.get_session_status()

        status_emoji = (
            "🟢"
            if health.get("server_status") == "healthy"
            else "🟡" if health.get("server_status") == "degraded" else "🔴"
        )
        market_emoji = "🔔" if session.get("alpaca_market_open") else "🔕"

        return f"""
{status_emoji} Server Status: {health.get("server_status", "unknown").upper()}
{market_emoji} Market: {session.get("session_description", "unknown")}

Quick Stats:
• Memory: {health.get("process_metrics", {}).get("memory_usage_mb", 0):.1f} MB
• CPU: {health.get("process_metrics", {}).get("cpu_usage_percent", 0):.1f}%
• Uptime: {health.get("uptime_formatted", "unknown")}
• APIs: {health.get("connection_health", {}).get("healthy_connections", 0)}/{health.get("connection_health", {}).get("total_connections", 0)}

Market Session:
• Phase: {session.get("session_phase", "unknown")}
• Extended Hours: {session.get("is_extended_hours", False)}
• Next: {session.get("next_event", "unknown")} in {session.get("time_to_next_formatted", "unknown")}

Capabilities: {health.get("capabilities", {}).get("tools", 0)} tools, {health.get("capabilities", {}).get("resources", 0)} resources
        """

    except Exception as e:
        return f"❌ Health check failed: {str(e)}"


@mcp.tool()
async def get_extended_market_clock() -> str:
    """Enhanced market clock with pre/post market sessions."""
    from .tools.enhanced_market_clock import get_extended_market_clock

    return await get_extended_market_clock()


@mcp.tool()
async def validate_extended_hours_order(
    symbol: str, order_type: str, extended_hours: bool = None
) -> dict:
    """Validate if order can be placed in current market session."""
    from .tools.extended_hours_orders import validate_extended_hours_order

    return await validate_extended_hours_order(symbol, order_type, extended_hours)


@mcp.tool()
async def place_extended_hours_order(
    symbol: str,
    side: str,
    quantity: float,
    order_type: str = "limit",
    limit_price: float = None,
    extended_hours: bool = None,
    time_in_force: str = "day",
) -> str:
    """Place order with automatic extended hours detection."""
    from .tools.extended_hours_orders import place_extended_hours_order

    return await place_extended_hours_order(
        symbol, side, quantity, order_type, limit_price, extended_hours, time_in_force
    )


@mcp.tool()
async def get_extended_hours_info() -> str:
    """Get comprehensive information about extended hours trading."""
    from .tools.extended_hours_orders import get_extended_hours_info

    return await get_extended_hours_info()


# ============================================================================
# PROMPT REGISTRATIONS
# ============================================================================


@mcp.prompt()
async def startup() -> str:
    """Execute comprehensive day trading startup checks with parallel execution and high-liquidity scanner."""
    return await startup_prompt.startup()


@mcp.prompt()
async def scan() -> str:
    """Scan for day trading opportunities using high-liquidity scanner and technical analysis.

    Uses default parameters: 500 trades/minute threshold, 20 result limit, combined.lis file.
    For custom parameters, use the scan_day_trading_opportunities tool directly.
    """
    return await scan_prompt.scan(500, 20, "combined.lis")


# ============================================================================
# SERVER INITIALIZATION
# ============================================================================


def get_server():
    """Get the MCP server instance."""
    return mcp


if __name__ == "__main__":
    mcp.run()
