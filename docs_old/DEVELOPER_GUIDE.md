# DEVELOPER GUIDE

## Table of Contents
1. [Project Overview](#project-overview)
2. [Development Environment](#development-environment)
3. [Architecture Implementation](#architecture-implementation)
4. [MCP Development Guidelines](#mcp-development-guidelines)
5. [Data Handling & Safety](#data-handling--safety)
6. [Production Deployment](#production-deployment)

---

## Project Overview

### Core Mission

This is an Alpaca MCP (Model Context Protocol) Server that provides LLMs with access to Alpaca's trading API. The server implements the FastMCP framework to expose trading functionality as tools that can be called by Claude Desktop, Cursor, or VSCode.

### Core Development Principles

- **Do not simplify the tools or pretend to solve the problems - actually solve the problems. Never mock - engineer.**
- **I don't want hype, propaganda, or mock functionality - only real engineering solutions**
- **Use the MCP tools, not direct Alpaca API methods. If the tools do not exist in the MCP server, we will create them.**
- **You can use the get_stock_bars_intraday MCP tool to fetch historical intraday bar data for MULTIPLE STOCK SYMBOLS at one time - this is more efficient than individual stock symbol tool use.**

### Architecture Hierarchy (Highest to Lowest Leverage)

🥇 **PROMPTS** (Highest Leverage - "Recipes for Repeat Solutions")
├── Intelligent workflows that guide users through complete strategies
├── Compose multiple tools and resources automatically
└── Examples: account_analysis(), position_management(), market_analysis()

🥈 **RESOURCES** (Dynamic Context)
├── Real-time data and state information
├── account://status - Live account metrics
├── positions://current - Real-time P&L data
└── market://conditions - Market status and momentum

🥉 **TOOLS** (Individual Actions - Lowest Leverage)
├── Single-purpose functions that do one thing well
├── Account, Position, Order, Market Data tools
└── Building blocks composed by prompts

---

## Development Environment

### Core Components

- **Main Server**: `alpaca_mcp_server.py` - The primary MCP server implementation using FastMCP
- **Client Initialization**: Multiple Alpaca clients are initialized:
  - `TradingClient` - For account management, positions, orders
  - `StockHistoricalDataClient` - For historical market data
  - `StockDataStream` - For streaming market data  
  - `OptionHistoricalDataClient` - For options data and Greeks
- **Tool Categories**: The server exposes ~40 tools organized by functionality:
  - Account & Position Management
  - Market Data (stocks, options, quotes, bars, trades)
  - Order Management (all order types including options)
  - Asset Information & Search
  - Watchlist Management
  - Market Status & Corporate Actions

### Environment Configuration

The server uses environment variables for API credentials and configuration:
- `APCA_API_KEY_ID` / `ALPACA_API_KEY` - API key
- `APCA_API_SECRET_KEY` / `ALPACA_SECRET_KEY` - Secret key  
- `PAPER` - Boolean flag for paper trading (defaults to true)

### Development Setup

The project uses UV for dependency management with a virtual environment at `.venv/`.

### Common Development Commands

#### Running the Server
```bash
# Primary method - run the MCP server directly
python alpaca_mcp_server.py

# Alternative module invocation
python -m alpaca_mcp_server
```

#### Environment Management
```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies with UV
uv sync

# Add new dependencies
uv add package-name
```

#### Testing Credentials
```bash
# Test API credentials and client connectivity
python test_credentials.py
```

### Development Notes

- The server defaults to paper trading for safety
- For live trading, set `PAPER=False` in environment
- The server requires Python 3.12+ and uses alpaca-py SDK
- All tools return formatted strings for LLM consumption
- Error handling includes specific guidance for options trading permissions
- The server implements both single-leg and multi-leg options strategies

### Project Dependencies

Core dependencies managed in `pyproject.toml`:
- `alpaca-py` - Primary Alpaca SDK for trading
- `mcp` - Model Context Protocol framework
- `python-dotenv` - Environment variable management

### Important File Notes

- `main.py` - Simple Hello World script, not the actual server
- `alpaca_mcp_server.py` - The actual MCP server implementation
- `test_credentials.py` - Utility for testing API connectivity
- `bub.sh` - Development script for testing alpaca-trade-api integration

---

## Architecture Implementation

### FastMCP Server Structure

```
alpaca_mcp_server/
├── prompts/           # Intelligent analysis prompts
├── tools/            # 40+ specialized trading tools
├── resources/        # Real-time market analysis engines
├── config/           # Flexible client management
└── models/           # Type-safe data structures
```

### Prompt Development Pattern

#### 1. Create Prompt Function
**File**: `alpaca_mcp_server/prompts/{command}_prompt.py`

```python
"""Brief description of what this prompt does."""

import asyncio
from datetime import datetime

async def command_name() -> str:
    """
    Detailed description for LLM understanding.
    
    This docstring becomes the prompt description that helps
    the LLM understand when and how to use this prompt.
    
    Returns:
        Formatted string with comprehensive analysis
    """
    
    # Implementation details
    result = await comprehensive_analysis()
    return formatted_result

__all__ = ["command_name"]
```

#### 2. Register in Module
**File**: `alpaca_mcp_server/prompts/__init__.py`

```python
from .command_name_prompt import command_name

__all__ = [
    # ... existing prompts ...
    "command_name",  # ADD NEW PROMPT
]
```

#### 3. Import in Server
**File**: `alpaca_mcp_server/server.py`

```python
from .prompts import (
    # ... existing imports ...
    command_name_prompt,  # ADD IMPORT
)
```

#### 4. Register with FastMCP
**File**: `alpaca_mcp_server/server.py`

```python
@mcp.prompt()
async def command_name() -> str:
    """Brief description for MCP registration."""
    return await command_name_prompt.command_name()
```

### Tool Development Pattern

#### Tool Creation Guidelines
```python
@tool(name="tool_name")
async def tool_function(param1: str, param2: int = 100) -> str:
    """
    Tool description that explains what it does.
    
    Args:
        param1: Description of required parameter
        param2: Description of optional parameter (default: 100)
    
    Returns:
        Formatted string with results for LLM consumption
    """
    
    try:
        # Tool implementation
        result = await execute_tool_logic(param1, param2)
        return format_tool_result(result)
        
    except Exception as e:
        return f"❌ Error: {str(e)}\n\nSuggested actions:\n• Check parameter values\n• Verify API connectivity"
```

### Resource Development Pattern

#### Resource Implementation
```python
class ResourceName:
    def __init__(self):
        self.config = load_resource_config()
        self.cache = {}
    
    async def get_resource_data(self) -> dict:
        """Get real-time resource data."""
        
        # Check cache first
        if self.is_cached_valid():
            return self.cache["data"]
        
        # Fetch fresh data
        data = await self.fetch_fresh_data()
        
        # Update cache
        self.cache = {
            "data": data,
            "timestamp": time.time()
        }
        
        return data
    
    async def fetch_fresh_data(self) -> dict:
        """Fetch fresh data from APIs."""
        # Implementation details
        pass
```

---

## MCP Development Guidelines

### Critical Safety Memories

- **If the MCP tools are not functioning properly, STOP and fix the tools, do not proceed unless the tools are fixed. Day-trading involves significant risk and the tools must function properly.**
- **Do not use market orders, unless I specifically instruct you.**
- **Use 4 decimal places for penny stock computations, so as to maintain accuracy.**
- **You can get order and account status from the real-time streaming data.**
- **You need more significant figures - 4 for penny stocks**
- **Do not buy stocks, which have less than 1,000 trades per minute. Need liquidity to get in and out quickly.**
- **You should check the latest trade price, when performing analysis or computing percentage up or down.**

### Trading Tool Requirements

#### Day Trading Stock Scanner Integration

**CRITICAL:** Always use the `trades_per_minute.sh` script for finding day trading opportunities instead of MCP scanner functions.

**Command:** `./trades_per_minute.sh -f combined.lis -t 500`

**Implementation in Prompts:**
```python
async def startup() -> str:
    """Execute startup checks with high-liquidity scanner."""
    
    # Run high-liquidity scanner
    scanner_result = subprocess.run(
        ["./trades_per_minute.sh", "-f", "combined.lis", "-t", "500"],
        capture_output=True, text=True, timeout=30,
        cwd="/home/jjoravet/alpaca-mcp-server"
    )
    
    # Process and sort by percent change
    if scanner_result.returncode == 0:
        lines = scanner_result.stdout.strip().split('\n')
        # Parse and sort by percentage change
        stocks_data = parse_scanner_output(lines)
        top_stocks = sort_by_percent_change(stocks_data, limit=20)
        return format_scanner_results(top_stocks)
    else:
        return f"❌ Scanner failed: {scanner_result.stderr}"
```

#### Trading Execution Patterns

**Entry Tracking Pattern:**
```python
async def track_entry_execution(symbol: str, order_id: str) -> dict:
    """Track and verify order execution with complete documentation."""
    
    # 1. Verify fill immediately
    order_status = await get_order_status(order_id)
    
    # 2. Confirm position
    position = await get_position(symbol)
    
    # 3. Document entry details
    entry_tracking = {
        "symbol": symbol,
        "entry_time": datetime.now().strftime("%H:%M:%S EDT"),
        "entry_price": float(order_status.filled_avg_price),
        "quantity": int(position.qty),
        "total_cost": float(order_status.filled_avg_price) * int(position.qty),
        "verified": True
    }
    
    return entry_tracking
```

**Position Size Verification:**
```python
def calculate_position_size(capital_amount: float, stock_price: float) -> int:
    """Calculate correct position size with verification."""
    
    # Calculate shares (round down for safety)
    shares = int(capital_amount / stock_price)
    
    # Verify calculation
    total_cost = shares * stock_price
    
    verification = {
        "requested_capital": capital_amount,
        "stock_price": stock_price,
        "calculated_shares": shares,
        "actual_cost": total_cost,
        "difference": capital_amount - total_cost,
        "calculation_correct": abs(capital_amount - total_cost) < (stock_price * 0.1)
    }
    
    return shares, verification
```

### Error Handling Standards

#### Intelligent Error Messages
```python
async def handle_trading_error(operation: str, error: Exception) -> str:
    """Provide contextual error handling for trading operations."""
    
    error_type = type(error).__name__
    
    if "insufficient buying power" in str(error).lower():
        return f"""
        ❌ Insufficient Buying Power
        
        Operation: {operation}
        
        Suggested actions:
        • Check account balance: get_account_info()
        • Review open positions: get_positions()
        • Consider reducing position size
        • Check for pending orders: get_orders(status="open")
        """
    
    elif "position not found" in str(error).lower():
        return f"""
        ❌ Position Not Found
        
        Operation: {operation}
        
        Suggested actions:
        • List all positions: get_positions()
        • Check symbol spelling
        • Verify position wasn't already closed
        """
    
    else:
        return f"""
        ❌ Trading Error: {error_type}
        
        Operation: {operation}
        Error: {str(error)}
        
        General troubleshooting:
        • Check API connectivity: health_check()
        • Verify account status: get_account_info()
        • Review market hours: get_market_clock()
        """
```

---

## Data Handling & Safety

### Alpaca Pre-Market Data Corrections

**CRITICAL:** Alpaca's snapshot data contains stale/incorrect reference data during pre-market hours that leads to inaccurate percentage calculations.

#### Problem Analysis
- The "Previous Close" field in snapshots shows outdated data (often from days prior)
- This causes incorrect percentage change calculations during pre-market trading
- Other financial data providers (Yahoo Finance, etc.) often have the same issue

#### Solution Implementation
```python
def correct_premarket_percentage(snapshot_data: dict) -> dict:
    """Correct pre-market percentage calculations using proper reference data."""
    
    # Extract OHLC data
    daily_bar = snapshot_data.get("daily_bar", {})
    
    # Yesterday's actual close = "Close" field in today's OHLC
    yesterday_close = daily_bar.get("c")
    
    # Current price from latest trade
    latest_trade = snapshot_data.get("latest_trade", {})
    current_price = latest_trade.get("p")
    
    if yesterday_close and current_price:
        # Calculate correct percentage
        correct_pct_change = ((current_price - yesterday_close) / yesterday_close) * 100
        
        return {
            "yesterday_actual_close": yesterday_close,
            "current_price": current_price,
            "correct_pct_change": correct_pct_change,
            "data_corrected": True,
            "explanation": "Used Today's OHLC 'Close' as yesterday's actual close"
        }
    
    return {
        "data_corrected": False,
        "error": "Insufficient data for correction"
    }

# Example usage in tools
async def get_corrected_snapshot(symbol: str) -> str:
    """Get snapshot with pre-market corrections applied."""
    
    raw_snapshot = await get_stock_snapshots(symbol)
    correction = correct_premarket_percentage(raw_snapshot)
    
    if correction["data_corrected"]:
        return f"""
        📊 {symbol} Snapshot (Pre-market Corrected)
        
        Yesterday Close: ${correction['yesterday_actual_close']:.4f}
        Current Price: ${correction['current_price']:.4f}
        Correct Change: {correction['correct_pct_change']:+.2f}%
        
        ⚠️ Note: {correction['explanation']}
        """
    else:
        return f"❌ Unable to correct pre-market data: {correction['error']}"
```

### Precision Requirements

#### Penny Stock Calculations
```python
def format_penny_stock_price(price: float) -> str:
    """Format prices with 4 decimal places for penny stocks."""
    return f"${price:.4f}"

def calculate_penny_stock_metrics(entry_price: float, current_price: float, shares: int) -> dict:
    """Calculate metrics with appropriate precision for penny stocks."""
    
    return {
        "entry_price": round(entry_price, 4),
        "current_price": round(current_price, 4),
        "price_change": round(current_price - entry_price, 4),
        "pct_change": round(((current_price - entry_price) / entry_price) * 100, 2),
        "unrealized_pnl": round((current_price - entry_price) * shares, 2),
        "total_value": round(current_price * shares, 2)
    }
```

### Memory Management Guidelines

#### Time Zone Consistency
- **All times in analysis should be referenced to NYC/EDT.**
- **Always convert timestamps to EDT for consistency**
- **Document time zone in all time-based outputs**

```python
from datetime import datetime
import pytz

def get_edt_timestamp() -> str:
    """Get current timestamp in EDT."""
    edt = pytz.timezone('America/New_York')
    return datetime.now(edt).strftime("%Y-%m-%d %H:%M:%S EDT")

def format_time_for_trading(timestamp: datetime) -> str:
    """Format timestamp for trading analysis."""
    edt = pytz.timezone('America/New_York')
    edt_time = timestamp.astimezone(edt)
    return edt_time.strftime("%H:%M:%S EDT")
```

#### Analysis Tool Integration
```python
async def comprehensive_analysis_pattern(symbol: str) -> str:
    """Standard pattern for comprehensive stock analysis."""
    
    # Use the tools for analysis - don't process screenshots
    snapshot = await get_stock_snapshots(symbol)
    bars = await get_stock_bars_intraday(symbol, limit=1000)
    peak_trough = await get_stock_peak_trough_analysis(symbol)
    
    # Apply corrections if pre-market
    market_clock = await get_market_clock()
    if not market_clock["is_open"]:
        snapshot = apply_premarket_corrections(snapshot)
    
    # Format with proper time zone
    analysis_time = get_edt_timestamp()
    
    return f"""
    📊 Comprehensive Analysis: {symbol}
    Analysis Time: {analysis_time}
    
    Current Status: {format_snapshot_data(snapshot)}
    Technical Signals: {format_peak_trough_data(peak_trough)}
    Intraday Action: {format_bars_summary(bars)}
    """
```

---

## Production Deployment

### Environment Safety

#### Paper Trading Default
```python
# Always default to paper trading for safety
PAPER_TRADING = os.getenv("PAPER", "true").lower() == "true"

if not PAPER_TRADING:
    logger.warning("🚨 LIVE TRADING MODE ENABLED - USE WITH EXTREME CAUTION")
    # Additional safety checks for live trading
    confirmation = input("Confirm live trading mode (yes/no): ")
    if confirmation.lower() != "yes":
        logger.info("Switching to paper trading for safety")
        PAPER_TRADING = True
```

#### API Key Validation
```python
def validate_api_credentials() -> bool:
    """Validate API credentials before starting server."""
    
    required_vars = ["APCA_API_KEY_ID", "APCA_API_SECRET_KEY"]
    
    for var in required_vars:
        if not os.getenv(var):
            logger.error(f"Missing required environment variable: {var}")
            return False
    
    # Test API connectivity
    try:
        test_client = TradingClient(
            api_key=os.getenv("APCA_API_KEY_ID"),
            secret_key=os.getenv("APCA_API_SECRET_KEY"),
            paper=True  # Always test with paper first
        )
        account = test_client.get_account()
        logger.info("✅ API credentials validated successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ API credential validation failed: {e}")
        return False
```

### Monitoring and Logging

#### Trading Activity Logging
```python
import logging
from datetime import datetime

# Configure trading-specific logger
trading_logger = logging.getLogger("trading_activity")
trading_logger.setLevel(logging.INFO)

handler = logging.FileHandler("trading_activity.log")
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
trading_logger.addHandler(handler)

def log_trading_action(action: str, symbol: str, details: dict):
    """Log all trading actions for audit trail."""
    
    log_entry = {
        "timestamp": get_edt_timestamp(),
        "action": action,
        "symbol": symbol,
        "details": details,
        "paper_trading": PAPER_TRADING
    }
    
    trading_logger.info(f"TRADING_ACTION: {log_entry}")
```

#### Performance Monitoring
```python
async def monitor_system_performance() -> dict:
    """Monitor system performance for production use."""
    
    import psutil
    
    return {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent,
        "api_latency": await measure_api_latency(),
        "active_connections": len(psutil.net_connections()),
        "timestamp": get_edt_timestamp()
    }
```

### Deployment Checklist

#### Pre-Deployment Verification
- [ ] ✅ All environment variables configured
- [ ] ✅ API credentials validated
- [ ] ✅ Paper trading mode confirmed
- [ ] ✅ Dependencies installed and up-to-date
- [ ] ✅ Tool registration verified
- [ ] ✅ Prompt registration confirmed
- [ ] ✅ Error handling tested
- [ ] ✅ Logging configured
- [ ] ✅ Performance monitoring active

#### Production Startup Sequence
```python
async def production_startup():
    """Safe production startup sequence."""
    
    logger.info("🚀 Starting Alpaca MCP Server")
    
    # 1. Validate environment
    if not validate_api_credentials():
        raise Exception("API credential validation failed")
    
    # 2. Initialize clients
    clients = initialize_alpaca_clients()
    logger.info("✅ Alpaca clients initialized")
    
    # 3. Register tools and prompts
    await register_all_tools()
    await register_all_prompts()
    logger.info("✅ Tools and prompts registered")
    
    # 4. Start monitoring
    monitoring_task = asyncio.create_task(start_performance_monitoring())
    
    # 5. Start MCP server
    logger.info("✅ MCP server ready for connections")
    return server
```

---

*This developer guide provides comprehensive instructions for building, maintaining, and deploying the Alpaca MCP Server with professional-grade safety, monitoring, and error handling capabilities.*