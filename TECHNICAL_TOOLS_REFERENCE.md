# TECHNICAL TOOLS REFERENCE

## Table of Contents
1. [FastMCP Prompt Registration](#fastmcp-prompt-registration)
2. [Day Trading Scanner Tools](#day-trading-scanner-tools)
3. [Market Data Analysis](#market-data-analysis)
4. [Pre-Market Data Corrections](#pre-market-data-corrections)
5. [Streaming Data Management](#streaming-data-management)
6. [Performance Optimization](#performance-optimization)

---

## FastMCP Prompt Registration

### Overview

FastMCP prompts are **reusable message templates** that provide guided workflows for LLM interactions. They're different from tools (which execute actions) and resources (which provide data) - prompts create structured interaction patterns.

### Key Characteristics
- **Reusable templates** for LLM guidance
- **Parameterized** with type-safe inputs
- **Flexible return types** (strings or message objects)
- **Auto-discovered** through decorator registration
- **Accessible via command interface** (e.g., `/startup`, `/analyze`)

### Step-by-Step Registration Process

#### 1. Create the Prompt Function File

Create a new Python file in the prompts directory:

**File:** `alpaca_mcp_server/prompts/your_prompt_name_prompt.py`

```python
"""Your Prompt Description - Brief explanation of what it does."""

import asyncio
from datetime import datetime
# Import any other dependencies you need


async def your_prompt_name() -> str:
    """
    Detailed description of what this prompt does.
    
    This docstring becomes the prompt description that helps
    the LLM understand when and how to use this prompt.
    
    Returns:
        Formatted string with the prompt result
    """
    
    # Your prompt implementation here
    result = "Your prompt output"
    return result


# Export the function
__all__ = ["your_prompt_name"]
```

**Key Requirements:**
- ✅ Function must be `async`
- ✅ Docstring is **critical** - becomes prompt description
- ✅ Return type should be `str` (or `list[PromptMessage]` for advanced cases)
- ✅ File naming: `{prompt_name}_prompt.py`

#### 2. Add to Prompts Module

Update `alpaca_mcp_server/prompts/__init__.py`:

```python
"""Prompts module for Alpaca MCP Server - Guided trading workflows."""

# Import all prompt modules
from .list_trading_capabilities import list_trading_capabilities
from .account_analysis_prompt import account_analysis
from .position_management_prompt import position_management
from .market_analysis_prompt import market_analysis
from .your_prompt_name_prompt import your_prompt_name  # ADD THIS LINE

__all__ = [
    "list_trading_capabilities",
    "account_analysis", 
    "position_management",
    "market_analysis",
    "your_prompt_name",  # ADD THIS LINE
]
```

#### 3. Import in Server Configuration

Update `alpaca_mcp_server/server.py` imports section:

```python
# Import all prompt modules
from .prompts import (
    list_trading_capabilities as ltc_module,
    account_analysis_prompt,
    position_management_prompt,
    market_analysis_prompt,
    tools_reference_prompt,
    your_prompt_name_prompt,  # ADD THIS LINE
)
```

#### 4. Register with FastMCP Server

Add the registration in `alpaca_mcp_server/server.py`:

```python
# ============================================================================
# PROMPT REGISTRATIONS
# ============================================================================

@mcp.prompt()
async def your_prompt_name() -> str:
    """Brief description for the MCP registration."""
    return await your_prompt_name_prompt.your_prompt_name()

# Add more prompt registrations here...
```

**Critical Pattern:**
- ✅ Use `@mcp.prompt()` decorator
- ✅ Function name becomes the command name (e.g., `startup` → `/startup`)
- ✅ Call the imported prompt function with `await`
- ✅ Add in the "PROMPT REGISTRATIONS" section

### Real Example: `/startup` Command

Here's the actual implementation from the `/startup` command:

#### File Structure:
```
alpaca_mcp_server/
├── prompts/
│   ├── startup_prompt.py          # ✅ Created
│   └── __init__.py                # ✅ Updated
└── server.py                      # ✅ Updated
```

#### Created `startup_prompt.py`:
```python
async def startup() -> str:
    """Execute comprehensive day trading startup checks with parallel execution."""
    
    # Run high-liquidity scanner
    scanner_result = subprocess.run(
        ["./trades_per_minute.sh", "-f", "combined.lis", "-t", "500"],
        capture_output=True, text=True, timeout=30,
        cwd="/home/jjoravet/alpaca-mcp-server"
    )
    
    # Process results and format professional report
    # ... implementation details ...
    
    return formatted_report
```

#### Updated `server.py`:
```python
# Import section
from .prompts import (
    # ... existing imports ...
    startup_prompt,  # Added
)

# Registration section
@mcp.prompt()
async def startup() -> str:
    """Execute comprehensive day trading startup checks with parallel execution and high-liquidity scanner."""
    return await startup_prompt.startup()
```

### Verification and Testing

#### 1. Check Registration
```python
from alpaca_mcp_server.server import mcp
import asyncio

# List all registered prompts
prompts = asyncio.run(mcp.list_prompts())
for p in prompts:
    print(f"- {p.name}")
```

#### 2. Test Execution
```python
from alpaca_mcp_server.prompts.your_prompt_name_prompt import your_prompt_name
import asyncio

# Test the function directly
result = asyncio.run(your_prompt_name())
print(result)
```

### Advanced Features

#### Parameterized Prompts
```python
@mcp.prompt()
async def analyze_stock(symbol: str, timeframe: str = "1D") -> str:
    """Analyze a specific stock with given timeframe."""
    return await analyze_stock_prompt.analyze_stock(symbol, timeframe)
```

#### Error Handling
```python
async def robust_prompt() -> str:
    """Prompt with comprehensive error handling."""
    try:
        result = await some_operation()
        return f"✅ Success: {result}"
    except Exception as e:
        return f"❌ Error: {str(e)}\n\nPlease try again or contact support."
```

### Troubleshooting

#### Common Issues:

1. **Prompt Not Registered**
   - ✅ Check all 4 steps completed
   - ✅ Verify imports and function names match
   - ✅ Restart server after changes

2. **Circular Import Errors**
   - ❌ Don't import `mcp` in prompt files
   - ✅ Keep prompts as plain async functions
   - ✅ Register with decorator in `server.py`

3. **Function Not Found**
   - ✅ Check `__init__.py` exports
   - ✅ Verify function name consistency
   - ✅ Ensure proper async/await usage

---

## Day Trading Scanner Tools

### High-Liquidity Stock Scanner (CRITICAL)

**ALWAYS use trades_per_minute.sh script instead of MCP scanner functions:**

```bash
./trades_per_minute.sh -f combined.lis -t 500
```

#### Purpose
- Scans all 10,112 stocks in combined.lis
- Filters by minimum 500 trades/minute (adjustable threshold)
- Returns real-time liquidity and momentum data
- Sorts by highest trades/minute activity

#### Output Format
```
Symbol  Trades/Min  Change%
------   ---------  -------
TSLA          6436    3.13%
RBNE          2284   380.9%
HOVR          1105   36.48%
ORCL           994    7.46%
```

#### Usage in Startup
1. Run script to identify high-liquidity opportunities
2. Focus on stocks with 1000+ trades/minute for primary targets
3. Use 500+ trades/minute as secondary tier
4. Analyze top results with peak/trough analysis
5. Prioritize explosive momentum (>20% change) with adequate liquidity

#### Analysis Procedure
- [ ] Run script to scan all 10,112 stocks in combined.lis
- [ ] Identify stocks with 1000+ trades/minute (Tier 1 targets)
- [ ] Identify stocks with 500-999 trades/minute (Tier 2 targets)
- [ ] **REJECT any stocks below 500 trades/minute** (insufficient liquidity)
- [ ] Prioritize explosive momentum stocks (>20% change) with adequate liquidity
- [ ] Note timestamp and compare with previous scans for trend analysis

#### Example Analysis
```
Symbol  Trades/Min  Change%  Analysis
------   ---------  -------  --------
TSLA          6436    3.13%  ← TIER 1: Ultra-high liquidity
RBNE          2284   380.9%  ← TIER 1: Explosive momentum  
HOVR          1105   36.48%  ← TIER 1: High momentum
ORCL           994    7.46%  ← TIER 2: Just below 1000
```

### Peak/Trough Analysis Integration

**Analyze only stocks that pass liquidity requirements:**
- [ ] `get_stock_peak_trough_analysis("TOP_LIQUID_SYMBOLS")` 
- [ ] Focus on stocks with recent TROUGH signals (buy opportunities)
- [ ] Avoid stocks with recent PEAK signals (potential exits)
- [ ] Combine momentum + liquidity + technical signals

### 8 AM EDT Algorithmic Trading Frenzy Detection

**CRITICAL MARKET PHENOMENON:** Every trading day at exactly 8:00 AM EDT, massive algorithmic/institutional trading activity creates extreme volatility.

#### What Happens
- **Tens of thousands of trades** execute within minutes (40K+ trades common)
- **Extreme price swings** - stocks can move 50-200% in minutes
- **Massive volume spikes** - 10x-50x normal pre-market volume
- **Algorithmic order execution** - institutions break large orders into thousands of small trades
- **High-frequency trading systems** activate simultaneously

#### Evidence from Real Data (Example: 8:01:32 EDT)
- RBNE: 201.2% gain, 45,956 trades, 3.7M volume
- ICON: 60.9% gain, 36,140 trades, 6M volume  
- TMDE: 84.6% gain, 28,993 trades, 9.8M volume
- USEG: 68.3% gain, 17,707 trades, 34M volume

#### Trading Strategy During 8 AM Frenzy
- **DO NOT TRADE** during 8:00-8:10 AM EDT period
- **Algorithms control the market** - human traders get crushed
- **Wait for 8:15 AM** when algorithmic activity subsides
- **Monitor for opportunities AFTER** the dust settles
- **Use 8 AM data** to identify which stocks institutions are targeting

---

## Market Data Analysis

### Enhanced Intraday Bar Data

#### Tool: `get_stock_bars_intraday`

**Enhanced data with institutional-grade analysis:**

```python
async def get_stock_bars_intraday(
    symbol: str,
    timeframe: str = "1Min",      # Professional 1-minute default
    limit: int = 10000,           # 100x more data than typical
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> str:
    # Get comprehensive data
    bars = await get_enhanced_bars(symbol, timeframe, limit)
    
    # Add professional analysis
    volume_analysis = analyze_volume_patterns(bars)
    momentum_analysis = calculate_momentum_indicators(bars)
    liquidity_analysis = assess_market_liquidity(bars)
    
    # Return actionable insights, not just raw data
    return format_professional_analysis(bars, analyses)
```

#### Professional Insights
- Volume surge detection (36x normal patterns)
- Block trade identification (>10K shares)
- Institutional vs retail activity analysis
- Liquidity assessment via bid-ask spreads
- Price action momentum classification

### Market Momentum Analysis

#### Tool: `get_market_momentum`

**Real-time technical analysis engine:**

```python
async def get_market_momentum(
    symbol: str = "SPY",
    timeframe_minutes: int = 1,
    analysis_hours: int = 2,
    sma_short: int = 5,
    sma_long: int = 20,
) -> dict:
    # Dynamic technical analysis
    # - Configurable moving averages
    # - Volume confirmation
    # - Volatility assessment
    # - Momentum strength scoring (0-10)
    # - Real-time trend direction
```

#### Advanced Metrics
- Dynamic SMA calculations with trend direction
- Momentum strength scoring (0-10 scale)
- Volume confirmation analysis
- Price volatility assessment
- Short-term momentum indicators

### Data Quality Monitoring

#### Resource: `data_quality.py`

**Feed quality monitoring for optimal execution:**

```python
class DataQualityMonitor:
    async def monitor_quality(self) -> dict:
        return {
            "latency_ms": self.measure_api_latency(),
            "spread_quality": self.analyze_bid_ask_spreads(),
            "data_freshness": self.check_quote_ages(),
            "feed_reliability": self.assess_connection_stability(),
        }
```

#### Configuration Thresholds
```python
data_quality_config = {
    "latency_threshold_ms": 500.0,
    "quote_age_threshold_seconds": 60.0,
    "spread_threshold_pct": 1.0,
}
```

---

## Pre-Market Data Corrections

### Alpaca Pre-Market Snapshot Data Issues

**CRITICAL:** Alpaca's snapshot data contains stale/incorrect reference data during pre-market hours that leads to inaccurate percentage calculations.

#### Problem
- The "Previous Close" field in snapshots shows outdated data (often from days prior)
- This causes incorrect percentage change calculations during pre-market trading
- Other financial data providers (Yahoo Finance, etc.) often have the same issue

#### Solution for Pre-Market Analysis

When analyzing stocks during pre-market hours, use this interpretation of snapshot data:

```
Today's OHLC: Open/High/Low/Close
                ↑              ↑
         Today's open    Yesterday's ACTUAL close
```

#### Correct Pre-Market Calculation
- Yesterday's actual close = Last value in "Today's OHLC" (the "Close" field)
- Current price = Latest trade price from snapshot
- Accurate % change = ((Current Price - Yesterday's Close) / Yesterday's Close) × 100

#### Example Correction
```
Snapshot shows: "Today's OHLC: $6.73 / $9.20 / $5.89 / $7.14"
- Yesterday's actual close: $7.14 (NOT the "Previous Close" field)
- Current price: $15.00
- Correct % change: ($15.00 - $7.14) / $7.14 = +110.08%
```

**This correction is essential until normal market hours begin and Alpaca updates their reference data.**

### Data Validation Tools

#### Pre-Market Data Validator
```python
def validate_premarket_data(snapshot_data):
    """Validate and correct pre-market snapshot data."""
    
    # Extract correct reference data
    todays_ohlc = snapshot_data.get("daily_bar", {})
    yesterday_close = todays_ohlc.get("c")  # Close is yesterday's actual close
    current_price = snapshot_data.get("latest_trade", {}).get("p")
    
    # Calculate corrected percentage
    if yesterday_close and current_price:
        correct_pct_change = ((current_price - yesterday_close) / yesterday_close) * 100
        
        return {
            "yesterday_close": yesterday_close,
            "current_price": current_price,
            "correct_pct_change": correct_pct_change,
            "data_quality": "corrected_premarket"
        }
    
    return {"data_quality": "insufficient_data"}
```

---

## Streaming Data Management

### Professional-Grade Streaming Infrastructure

#### Tool: `start_global_stock_stream`

**Advanced streaming features:**

```python
# Professional streaming setup
streaming_config = {
    "feed": "sip",              # All exchanges vs "iex"
    "buffer_size": None,        # Unlimited for active stocks
    "data_types": ["trades", "quotes", "bars"],
    "duration_seconds": None,   # Run indefinitely
}

# Configurable streaming with institutional features
streaming_features = {
    "unlimited_buffers": True,           # Handle high-velocity stocks
    "multi_symbol_support": True,        # Concurrent streaming
    "configurable_feeds": ["sip", "iex"], # All exchanges vs single
    "buffer_management": "automatic",     # Memory optimization
    "data_quality_monitoring": True,     # Real-time quality checks
}
```

#### Real-time Data Processing
```python
# Start professional streaming for active trading
result = await start_global_stock_stream(
    symbols=["AAPL", "NVDA", "TSLA"],
    data_types=["trades", "quotes", "bars"],
    feed="sip",  # All exchanges
    buffer_size_per_symbol=None  # Unlimited for active stocks
)
```

#### Streaming Resource Management

**Resource: `streaming_resources.py`**

```python
class StreamingManager:
    def __init__(self):
        self.active_streams = {}
        self.buffer_stats = {}
        self.quality_metrics = {}
    
    async def monitor_stream_health(self) -> dict:
        return {
            "active_streams": len(self.active_streams),
            "buffer_utilization": self.calculate_buffer_usage(),
            "data_latency": self.measure_stream_latency(),
            "connection_stability": self.assess_connection_health(),
        }
```

#### Buffer Management
```python
# Memory-efficient buffer management
def manage_stream_buffers():
    # Configurable buffers for high-velocity stocks
    # Automatic cleanup for long-running streams
    # Real-time memory usage tracking
    pass
```

### Stream Data Analysis Tools

#### Real-Time Trade Analysis
```python
async def analyze_streaming_trades(symbol: str, seconds: int = 30):
    """Analyze recent streaming trade data for execution insights."""
    
    stream_data = await get_stock_stream_data(symbol, "trades", recent_seconds=seconds)
    
    return {
        "trade_velocity": calculate_trades_per_minute(stream_data),
        "volume_intensity": analyze_volume_patterns(stream_data),
        "price_momentum": detect_momentum_shifts(stream_data),
        "execution_quality": assess_fill_opportunities(stream_data),
    }
```

#### Quote Quality Assessment
```python
async def assess_quote_quality(symbol: str):
    """Evaluate bid-ask spread quality and market depth."""
    
    quotes = await get_stock_stream_data(symbol, "quotes", recent_seconds=10)
    
    return {
        "average_spread": calculate_average_spread(quotes),
        "spread_stability": analyze_spread_volatility(quotes),
        "quote_frequency": measure_quote_updates(quotes),
        "market_depth": estimate_liquidity_depth(quotes),
    }
```

---

## Performance Optimization

### Intelligent Caching System

#### Data Caching Strategy
```python
class MarketDataCache:
    def __init__(self):
        self.cache = {}
        self.cache_ttl = {}
        
    async def get_cached_or_fetch(self, key: str, fetch_func, ttl_seconds: int = 60):
        """Get cached data or fetch fresh if expired."""
        
        if key in self.cache and not self.is_expired(key):
            return self.cache[key]
        
        # Fetch fresh data
        data = await fetch_func()
        self.cache[key] = data
        self.cache_ttl[key] = time.time() + ttl_seconds
        
        return data
```

#### Configuration Caching
```python
# Reuse client connections
class ClientFactory:
    _clients = {}
    
    @classmethod
    def get_trading_client(cls):
        if 'trading' not in cls._clients:
            cls._clients['trading'] = TradingClient(
                api_key=settings.ALPACA_API_KEY,
                secret_key=settings.ALPACA_SECRET_KEY,
                paper=settings.PAPER_TRADING
            )
        return cls._clients['trading']
```

### Async Architecture Optimization

#### Concurrent Data Fetching
```python
async def fetch_comprehensive_data(symbol: str):
    """Gather multiple data sources simultaneously."""
    
    # Execute all data fetches concurrently
    tasks = [
        get_stock_snapshots(symbol),
        get_stock_bars_intraday(symbol, limit=1000),
        get_market_momentum("SPY"),
        get_data_quality_metrics(),
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results with error handling
    return process_concurrent_results(results)
```

#### Non-Blocking Operations
```python
async def stream_with_analysis(symbols: list):
    """Maintain responsiveness during streaming analysis."""
    
    # Start streaming (non-blocking)
    stream_task = asyncio.create_task(start_streaming(symbols))
    
    # Perform analysis while streaming
    analysis_tasks = [
        analyze_symbol_momentum(symbol) for symbol in symbols
    ]
    
    # Wait for both streaming and analysis
    stream_result, analysis_results = await asyncio.gather(
        stream_task,
        asyncio.gather(*analysis_tasks)
    )
    
    return combine_streaming_and_analysis(stream_result, analysis_results)
```

### Memory Management

#### Buffer Optimization
```python
class OptimizedBuffer:
    def __init__(self, max_size: int = 10000):
        self.buffer = collections.deque(maxlen=max_size)
        self.size_limit = max_size
        
    def add_data(self, data):
        """Add data with automatic size management."""
        self.buffer.append(data)
        
        # Automatic cleanup if buffer grows too large
        if len(self.buffer) > self.size_limit * 0.9:
            self.cleanup_old_data()
    
    def cleanup_old_data(self):
        """Remove oldest 25% of data to prevent memory issues."""
        cleanup_count = len(self.buffer) // 4
        for _ in range(cleanup_count):
            self.buffer.popleft()
```

#### Memory Monitoring
```python
async def monitor_memory_usage():
    """Track memory usage for long-running operations."""
    
    import psutil
    process = psutil.Process()
    
    return {
        "memory_percent": process.memory_percent(),
        "memory_mb": process.memory_info().rss / 1024 / 1024,
        "open_files": len(process.open_files()),
        "connections": len(process.connections()),
    }
```

### Performance Benchmarking

#### Latency Measurement
```python
async def benchmark_api_latency():
    """Measure API response times for performance tuning."""
    
    start_time = time.time()
    
    # Test basic API call
    await get_stock_quote("SPY")
    
    latency_ms = (time.time() - start_time) * 1000
    
    return {
        "api_latency_ms": latency_ms,
        "performance_grade": grade_latency(latency_ms),
        "optimization_needed": latency_ms > 500,
    }
```

#### Throughput Analysis
```python
async def measure_data_throughput(symbols: list, duration_seconds: int = 60):
    """Measure data processing throughput for capacity planning."""
    
    start_time = time.time()
    processed_count = 0
    
    async for data_point in stream_multiple_symbols(symbols):
        processed_count += 1
        
        if time.time() - start_time >= duration_seconds:
            break
    
    throughput = processed_count / duration_seconds
    
    return {
        "data_points_per_second": throughput,
        "total_processed": processed_count,
        "capacity_utilization": calculate_capacity_usage(throughput),
    }
```

---

*This technical reference provides comprehensive documentation for implementing and optimizing the advanced trading tools and infrastructure required for professional day trading operations.*