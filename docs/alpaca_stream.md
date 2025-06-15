# Alpaca Stream Script

The Alpaca Stream script is a comprehensive tool for connecting to Alpaca's WebSocket streaming data service. It provides access to real-time market data, allowing you to stream various data types for multiple stock symbols with minimal latency.

## Features

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

## Reconnection System

The script includes an intelligent automatic reconnection system that:

- Monitors the time since the last received message
- Detects stalled connections when no data is received
- Implements exponential backoff for reconnection attempts
- Re-applies all subscriptions after reconnection
- Provides configurable parameters for fine-tuning

## Symbol Management

The script offers flexible symbol management:

- Command-line symbol specification
- Loading symbols from a text file (one per line)
- Combining symbols from both sources
- Automatic deduplication
- Case-insensitive symbol handling

## Usage Examples

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

## Output Format

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

## Statistics

At the end of the run, the script displays statistics on the number of events received for each data type:

```
Event counters:
  trades: 1250
  quotes: 0
  bars: 0
```

## Integration

This script is designed to work alongside the TradeManager component, providing the real-time market data needed for optimal trade execution. The two components can be used together for a complete high-frequency trading system:

- **Alpaca Stream Script**: Provides real-time market data
- **TradeManager**: Executes trades with optimal timing

Together, these components form the foundation of a robust, high-performance trading system for volatile markets.
