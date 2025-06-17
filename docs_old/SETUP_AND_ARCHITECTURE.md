# SETUP AND ARCHITECTURE GUIDE

## Table of Contents
1. [Project Overview](#project-overview)
2. [Quick Start Setup](#quick-start-setup)
3. [Security Configuration](#security-configuration)
4. [Architecture Deep Dive](#architecture-deep-dive)
5. [Integration Examples](#integration-examples)
6. [Advanced Configuration](#advanced-configuration)

---

## Project Overview

### 🚀 Professional Alpaca MCP Server

A sophisticated **Model Context Protocol (MCP) server** that transforms Alpaca's Trading API into an intelligent trading assistant for LLMs. Built with advanced prompt engineering, modular architecture, and institutional-grade market analysis capabilities.

### 🌟 Why This MCP Server is Superior

#### 🧠 **Advanced Prompt Engineering**
- **Intelligent Trading Prompts**: Pre-built analysis functions that combine multiple data sources
- **Contextual Insights**: Prompts automatically interpret market conditions and provide actionable recommendations
- **Professional Analysis**: Institutional-quality portfolio reviews, risk assessments, and position management

#### 🏗️ **Enterprise Architecture**
```
alpaca_mcp_server/
├── prompts/           # Intelligent analysis prompts
├── tools/            # 40+ specialized trading tools
├── resources/        # Real-time market analysis engines
├── config/           # Flexible client management
└── models/           # Type-safe data structures
```

#### 📊 **Institutional-Grade Analysis**
- **Market Momentum Detection**: Real-time SPY analysis with configurable indicators
- **Data Quality Monitoring**: Latency, spread, and feed quality metrics
- **Intraday P&L Tracking**: Professional performance analytics
- **Streaming Infrastructure**: High-frequency data processing for active trading

---

## Quick Start Setup

### 1. **Installation**

```bash
# Clone the repository
git clone <your-repo-url>
cd alpaca-mcp-server

# Install dependencies with UV (recommended)
uv sync

# Or use pip
pip install -r requirements.txt
```

### 2. **Basic Testing**

```bash
# Test the server
python run_alpaca_mcp.py

# Test credentials
python test_credentials.py
```

---

## Security Configuration

### ⚠️ CRITICAL: API Keys and Sensitive Data

**NEVER commit API keys, secrets, or personal data to git repositories.**

#### Environment Setup

1. **Copy environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Edit .env with your actual credentials:**
   ```bash
   # Your actual Alpaca API credentials
   APCA_API_KEY_ID="your_actual_api_key"
   APCA_API_SECRET_KEY="your_actual_secret_key"
   PAPER="true"  # Set to "false" for live trading
   ```

3. **Copy MCP configuration template:**
   ```bash
   cp .mcp.json.example .mcp.json
   ```

#### Files That Must Never Be Committed

- `.env` - Contains API keys and secrets
- `.mcp.json` - May contain user-specific configuration
- Any file containing actual API keys or personal data
- Log files that might contain sensitive information

#### Security Best Practices

1. **Use environment variables** instead of hardcoding credentials
2. **Use paper trading** (`PAPER="true"`) for development and testing
3. **Regularly rotate API keys** for security
4. **Never share credentials** in chat, email, or other communications
5. **Use separate API keys** for development vs production

#### If You Accidentally Commit Secrets

1. **Immediately rotate the exposed credentials** on your Alpaca account
2. **Remove from git history** using tools like `git filter-branch` or BFG Repo-Cleaner
3. **Verify the secrets are removed** from all branches and tags
4. **Force push** to overwrite remote history (if applicable)

---

## Architecture Deep Dive

### 🧠 Design Philosophy

#### **Intelligence Over Integration**
Instead of simple API passthrough, we built an **intelligent trading assistant** that:
- **Interprets market conditions** using advanced prompts
- **Combines multiple data sources** for comprehensive analysis
- **Provides actionable insights** rather than raw data
- **Scales to institutional requirements** with professional-grade tools

#### **Modular Excellence**
```
Enterprise Architecture = Prompts + Tools + Resources + Configuration
```

### 📊 Layer Architecture

#### 1. **Prompt Engineering Layer** (`prompts/`)
**Purpose**: Transform raw API data into intelligent trading insights

```python
prompts/
├── account_analysis_prompt.py     # Portfolio health & risk assessment
├── position_management_prompt.py  # Intelligent position analysis
├── market_analysis_prompt.py      # Market condition interpretation
├── risk_management_prompt.py      # Multi-factor risk scoring
├── options_strategy_prompt.py     # Options trading strategies
└── portfolio_review_prompt.py     # Performance attribution
```

**Key Features:**
- **Multi-source data fusion**: Combines account, position, and market data
- **Contextual analysis**: Interprets performance relative to market conditions
- **Actionable recommendations**: Specific next steps, not just status
- **Professional formatting**: Institutional-quality reporting

**Example Prompt Intelligence:**
```python
async def position_management(symbol: str) -> str:
    # Gather multiple data sources
    position = get_open_position(symbol)
    snapshot = get_stock_snapshots(symbol)
    account = get_account_info()
    
    # Intelligent analysis
    unrealized_pnl_pct = float(position.unrealized_plpc) * 100
    
    if unrealized_pnl_pct > 20:
        return "🟢 Strong Winner - Consider scaling out 25-50% to lock profits"
    elif unrealized_pnl_pct < -15:
        return "🔴 Significant Loss - Urgent review of thesis required"
    
    # Contextual market analysis
    market_momentum = await get_market_momentum("SPY")
    if market_momentum["direction"] == "bearish" and unrealized_pnl_pct < 0:
        return "⚠️  Market headwinds detected - Consider defensive positioning"
```

#### 2. **Tools Layer** (`tools/`)
**Purpose**: Specialized trading functions organized by domain

```python
tools/
├── account/           # Account & portfolio management
│   ├── account_info.py      # Account details & balances
│   ├── positions.py         # Position management
│   └── portfolio_history.py # Performance tracking
├── market_data/       # Advanced market data
│   ├── stocks.py           # Enhanced stock data (10K bars)
│   ├── options.py          # Options chains & Greeks
│   ├── snapshots.py        # Comprehensive market snapshots
│   └── streaming.py        # Real-time data feeds
├── orders/            # Professional order management
│   ├── stock_orders.py     # All stock order types
│   ├── option_orders.py    # Multi-leg options strategies
│   └── order_management.py # Order lifecycle management
├── assets/            # Asset discovery & analysis
└── watchlist/         # Portfolio tracking
```

**Advanced Tool Features:**
- **Enhanced data limits**: 10,000 intraday bars (vs typical 100)
- **Professional timeframes**: 1-minute default for institutional analysis
- **Multi-asset support**: Stocks, options, ETFs unified interface
- **Error handling**: Graceful degradation with actionable error messages

#### 3. **Resources Layer** (`resources/`)
**Purpose**: Real-time analysis engines for institutional-grade insights

```python
resources/
├── market_momentum.py       # Technical analysis engine
├── data_quality.py         # Feed quality monitoring
├── intraday_pnl.py         # Performance analytics
├── streaming_resources.py  # Real-time data management
├── api_monitor.py          # Connection health monitoring
└── server_health.py        # System status tracking
```

**Resource Capabilities:**
- **Configurable parameters**: Customize analysis to trading style
- **Real-time computation**: Live market analysis during trading hours
- **Quality monitoring**: Latency, spread, and data freshness tracking
- **Professional metrics**: Institutional-grade performance analytics

**Example Resource - Market Momentum:**
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

#### 4. **Configuration Layer** (`config/`)
**Purpose**: Flexible client management and environment handling

```python
config/
├── settings.py         # Environment configuration
└── clients.py          # API client factory functions
```

**Configuration Features:**
- **Multiple environment support**: Paper vs live trading
- **Client factory pattern**: Reusable API client creation
- **Environment validation**: Ensure required credentials are present
- **Fallback handling**: Graceful degradation when services unavailable

### 🚀 Advanced Features

#### **1. Enhanced Data Processing**

**Standard MCP servers**: Basic API passthrough
```python
# Typical approach
def get_bars(symbol):
    return api.get_bars(symbol, limit=100)  # Limited data
```

**Our approach**: Enhanced data with analysis
```python
# Our enhanced approach
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

#### **2. Real-time Streaming Infrastructure**

**Professional-grade streaming** for active trading:

```python
# Configurable streaming with institutional features
streaming_features = {
    "unlimited_buffers": True,           # Handle high-velocity stocks
    "multi_symbol_support": True,        # Concurrent streaming
    "configurable_feeds": ["sip", "iex"], # All exchanges vs single
    "buffer_management": "automatic",     # Memory optimization
    "data_quality_monitoring": True,     # Real-time quality checks
}
```

#### **3. Intelligent Error Handling**

**Context-aware error responses** instead of technical errors:

```python
# Instead of raw API errors
try:
    position = client.get_open_position(symbol)
except Exception as e:
    return f"API Error: {e}"  # Unhelpful

# Our intelligent error handling
try:
    position = client.get_open_position(symbol)
except PositionNotFound:
    return f"""
    No open position found for {symbol}.
    
    Suggested actions:
    • Check if you have this position: get_positions()
    • Search for the asset: get_asset_info('{symbol}')
    • View your watchlists: get_watchlists()
    """
```

---

## Integration Examples

### 📱 **Claude Desktop Integration**

Add to your Claude Desktop MCP configuration:

```json
{
  "mcpServers": {
    "alpaca": {
      "type": "stdio",
      "command": "bash",
      "args": ["-c", "source .venv/bin/activate && python run_alpaca_mcp.py"],
      "cwd": "/path/to/alpaca-mcp-server"
    }
  }
}
```

### 💬 **Natural Language Trading**

With Claude Desktop, you can now:

```
"Analyze my portfolio and give me a comprehensive health check"
→ Triggers account_analysis() prompt with professional insights

"Check the market momentum for SPY over the last 2 hours"
→ Executes market_momentum analysis with technical indicators

"Start streaming NVDA and TSLA for real-time analysis"
→ Initiates professional streaming with optimal configuration

"What's the intraday action on AAPL with volume analysis?"
→ Gets 10,000 1-minute bars with institutional-grade analysis
```

### 💡 Usage Examples

#### 🔍 **Intelligent Market Analysis**

The MCP server provides sophisticated analysis prompts that combine multiple data sources:

```python
# Get comprehensive portfolio health check
result = await account_analysis()
```

**What you get:**
- Portfolio value and cash allocation analysis
- Risk level assessment with specific factors
- Concentration risk warnings
- Strategic recommendations for rebalancing
- Next steps for optimization

#### 📊 **Advanced Position Management**

```python
# Analyze specific position with intelligent insights
result = await position_management("AAPL")
```

**Professional analysis includes:**
- Performance categorization (Strong Winner, Underperforming, etc.)
- Specific action recommendations
- Risk-adjusted position sizing guidance
- Exit strategy suggestions based on market conditions

#### 🎯 **Market Momentum Detection**

```python
# Real-time market momentum analysis
result = await get_market_momentum(
    symbol="SPY",
    timeframe_minutes=1,
    analysis_hours=2,
    sma_short=5,
    sma_long=20
)
```

**Advanced metrics:**
- Dynamic SMA calculations with trend direction
- Momentum strength scoring (0-10 scale)
- Volume confirmation analysis
- Price volatility assessment
- Short-term momentum indicators

#### 🚀 **Enhanced Intraday Analysis**

```python
# Get detailed intraday analysis with 10,000 bars
result = await get_stock_bars_intraday(
    symbol="NVDA",
    timeframe="1Min",
    limit=10000  # Industry-leading data depth
)
```

**Professional insights:**
- Volume surge detection (36x normal patterns)
- Block trade identification (>10K shares)
- Institutional vs retail activity analysis
- Liquidity assessment via bid-ask spreads
- Price action momentum classification

#### 📡 **Real-time Streaming Analysis**

```python
# Start professional streaming for active trading
result = await start_global_stock_stream(
    symbols=["AAPL", "NVDA", "TSLA"],
    data_types=["trades", "quotes", "bars"],
    feed="sip",  # All exchanges
    buffer_size_per_symbol=None  # Unlimited for active stocks
)
```

**Advanced streaming features:**
- Configurable buffer management
- Multi-symbol concurrent streaming
- Real-time trade and quote analysis
- Professional-grade data quality monitoring

---

## Advanced Configuration

### 📈 **Market Data Configuration**

```python
# Configurable analysis parameters
market_momentum_config = {
    "timeframe_minutes": 1,     # 1, 5, 15, 30, 60
    "analysis_hours": 2,        # Historical depth
    "sma_short": 5,            # Short-term MA
    "sma_long": 20,            # Long-term MA
}

# Data quality thresholds
data_quality_config = {
    "latency_threshold_ms": 500.0,
    "quote_age_threshold_seconds": 60.0,
    "spread_threshold_pct": 1.0,
}
```

### 🚀 **Streaming Configuration**

```python
# Professional streaming setup
streaming_config = {
    "feed": "sip",              # All exchanges vs "iex"
    "buffer_size": None,        # Unlimited for active stocks
    "data_types": ["trades", "quotes", "bars"],
    "duration_seconds": None,   # Run indefinitely
}
```

### 🔧 **Performance Optimizations**

#### **1. Intelligent Caching**
- **Market data caching**: Avoid redundant API calls during analysis
- **Configuration caching**: Reuse client connections
- **Prompt result caching**: Cache expensive analysis computations

#### **2. Async Architecture**
- **Concurrent data fetching**: Gather multiple data sources simultaneously
- **Non-blocking operations**: Maintain responsiveness during analysis
- **Stream processing**: Handle real-time data efficiently

#### **3. Memory Management**
- **Configurable buffers**: Handle high-velocity stocks without memory issues
- **Automatic cleanup**: Garbage collection for long-running streams
- **Buffer monitoring**: Real-time memory usage tracking

### 📚 **Advanced Features (Coming Soon)**

#### **Institutional Analysis Tools**
- **Volcanic Accumulation Detector**: Identify institutional buying patterns
- **Pre-Breakout Scanner**: Detect acceleration in trade frequency
- **Microstructure Analysis**: Raw data access for velocity calculations
- **Block Trade Detection**: Identify large institutional orders

#### **Professional Reporting**
The server provides institutional-quality analysis:
- Multi-factor risk assessment
- Performance attribution analysis
- Concentration risk monitoring
- Cash allocation optimization
- Strategic rebalancing recommendations

---

## 🚀 Get Started Now

1. **Clone the repository**
2. **Follow the security setup** above
3. **Configure your environment** with .env
4. **Start with paper trading**
5. **Experience professional-grade trading AI**

Transform your trading workflow with intelligent analysis, institutional-grade tools, and advanced prompt engineering. This isn't just an API wrapper - it's a comprehensive trading intelligence platform.

---

*This architecture represents a new standard for trading AI integration - moving beyond simple API access to intelligent trading assistance with institutional-grade capabilities.*