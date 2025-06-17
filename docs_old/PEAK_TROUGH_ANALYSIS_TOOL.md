# Peak and Trough Analysis Tool

## Overview

The Peak and Trough Analysis Tool is a professional technical analysis instrument designed for day trading applications. It implements zero-phase Hanning filtering followed by peak detection algorithms to identify precise entry and exit points for trading strategies.

## Purpose

This tool directly addresses the trading lesson: **"SCAN LONGER before entry - Watch streaming data 60-120 seconds to find better entry price"** by providing sophisticated technical analysis to identify optimal support and resistance levels.

## Technical Implementation

### Algorithm Flow

1. **Data Acquisition**: Fetches historical intraday bar data from Alpaca Markets
2. **Zero-Phase Filtering**: Applies low-pass Hanning window filtering to remove noise while preserving timing
3. **Peak Detection**: Uses advanced algorithms to identify local maxima (peaks) and minima (troughs)
4. **Signal Analysis**: Generates trading recommendations based on current price position relative to recent peaks/troughs

### Key Features

- **X/Y Accuracy**: Peak timing from filtered data, price levels from original unfiltered data
- **Configurable Parameters**: Full control over analysis parameters
- **Multi-Symbol Support**: Analyze multiple stocks simultaneously
- **Multiple Timeframes**: Support for 1Min, 5Min, 15Min, 30Min, 1Hour bars
- **Trading Signals**: Clear BUY/LONG, SELL/SHORT, and WATCH recommendations

## MCP Tool Registration

```python
@mcp.tool()
async def get_stock_peak_trough_analysis(
    symbols: str,
    timeframe: str = "1Min",
    days: int = 1,
    limit: int = 1000,
    window_len: int = 11,
    lookahead: int = 1,
    delta: float = 0.0,
    min_peak_distance: int = 5
) -> str:
```

## Parameters

### Required Parameters

- **symbols** (str): Comma-separated list of stock symbols
  - Examples: `"CGTL"`, `"AAPL,MSFT,NVDA"`

### Optional Parameters

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

## Usage Examples

### Basic Analysis
```python
# Quick analysis of CGTL with default settings
result = await get_stock_peak_trough_analysis("CGTL")
```

### Multi-Symbol Analysis
```python
# Analyze multiple stocks with 5-minute bars
result = await get_stock_peak_trough_analysis(
    symbols="AAPL,MSFT,NVDA",
    timeframe="5Min",
    days=2
)
```

### High-Sensitivity Analysis
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

### Reduced Noise Analysis
```python
# Less sensitive analysis for swing trading
result = await get_stock_peak_trough_analysis(
    symbols="AAPL",
    timeframe="15Min",
    days=5,
    window_len=21,     # More smoothing
    lookahead=5,       # Less sensitive
    min_peak_distance=10  # Wider peak spacing
)
```

## Output Format

The tool returns a comprehensive formatted analysis including:

### Header Information
- Analysis parameters used
- Timestamp of analysis
- Symbol list processed

### Per-Symbol Analysis
- Total bars analyzed
- Price range (min/max)
- Current price
- Number of peaks and troughs found

### Recent Peaks (Resistance/Sell Signals)
- Timestamp of each peak
- Original price at peak (executable level)
- Filtered price (detection level)
- Latest peak analysis with distance

### Recent Troughs (Support/Buy Signals)
- Timestamp of each trough
- Original price at trough (executable level)
- Filtered price (detection level)
- Latest trough analysis with distance

### Trading Signal Summary
- **BUY/LONG**: Price rising from recent trough
- **SELL/SHORT**: Price declining from recent peak
- **WATCH**: Price near turning point
- Signal strength percentage
- Distance from latest signal

## Trading Applications

### Entry Point Identification
- **Buy Signals**: When price bounces from trough support
- **Sell Signals**: When price rejects from peak resistance
- **Confirmation**: Use with streaming data for timing

### Risk Management
- **Stop Levels**: Place stops below troughs (long) or above peaks (short)
- **Target Levels**: Take profits at opposite signal level
- **Position Sizing**: Use signal strength for position allocation

### Integration with Trading Lessons

This tool directly supports the key trading lessons:

1. **"SCAN LONGER before entry"**: Provides precise technical levels to watch
2. **"Use limit orders exclusively"**: Gives exact price levels for limit orders
3. **"React within 2-3 seconds when profit appears"**: Pre-identifies key levels
4. **"Capture profits aggressively"**: Shows resistance levels for exits

### Parameter Tuning Guidelines

#### For Penny Stocks (< $1.00)
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

#### For Regular Stocks (> $1.00)
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

#### For Volatile Stocks
```python
get_stock_peak_trough_analysis(
    symbols="volatile_stock",
    timeframe="1Min",
    window_len=15,      # More smoothing
    lookahead=2,        # Less sensitive
    min_peak_distance=7  # Wider spacing
)
```

## Performance Considerations

- **Real-time Use**: Designed for live trading analysis
- **Data Volume**: Manages large datasets efficiently
- **Parameter Sensitivity**: Test parameters with historical data first
- **Multiple Symbols**: Can analyze many symbols in single call

## Integration with MCP Server

The tool is fully integrated into the Alpaca MCP server and available through:
- Claude Desktop
- Cursor IDE
- VSCode with MCP extension
- Direct MCP client connections

## Error Handling

The tool includes comprehensive error handling for:
- Invalid symbols
- Parameter validation and correction
- Data availability issues
- Network connectivity problems
- Empty datasets

## Limitations

- Requires historical data availability
- Past performance does not guarantee future results
- Should be combined with other technical indicators
- Market conditions affect algorithm effectiveness

## Best Practices

1. **Parameter Testing**: Test different parameters with paper trading first
2. **Multiple Timeframes**: Use multiple timeframes for confirmation
3. **Volume Confirmation**: Combine with volume analysis
4. **Risk Management**: Always use proper position sizing and stops
5. **Market Conditions**: Adjust parameters for different market volatility

## Support and Maintenance

The tool is part of the Alpaca MCP Server project and follows the same maintenance and update schedule. Feature requests and bug reports should be submitted through the project's issue tracking system.