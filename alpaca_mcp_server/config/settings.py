"""Configuration settings for Alpaca MCP Server."""

import os
from dotenv import load_dotenv
from typing import Optional
import time
import threading
from collections import deque, defaultdict

# Alpaca imports
from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.historical.option import OptionHistoricalDataClient
from alpaca.data.live.stock import StockDataStream

# Load environment variables
load_dotenv()


class Settings:
    """Configuration settings for Alpaca MCP Server."""

    def __init__(self):
        # API credentials - support both naming conventions
        self.api_key = os.getenv("APCA_API_KEY_ID") or os.getenv("ALPACA_API_KEY")
        self.api_secret = os.getenv("APCA_API_SECRET_KEY") or os.getenv(
            "ALPACA_SECRET_KEY"
        )

        # Paper trading flag
        self.paper = os.getenv("PAPER", "true").lower() in ["true", "1", "yes"]

        # Optional URL overrides
        self.trade_api_url = os.getenv("trade_api_url")
        self.trade_api_wss = os.getenv("trade_api_wss")
        self.data_api_url = os.getenv("data_api_url")
        self.stream_data_wss = os.getenv("stream_data_wss")

        # Server configuration
        self.server_name = "alpaca-trading"
        self.version = "2.0.0"

        # Validate required credentials
        if not self.api_key or not self.api_secret:
            raise ValueError(
                "Alpaca API credentials not found in environment variables."
            )


# Global settings instance
settings = Settings()

# ============================================================================
# Client Factory Functions (Singleton Pattern)
# ============================================================================

_trading_client = None
_stock_historical_client = None
_stock_data_stream_client = None
_option_historical_client = None


def get_trading_client() -> TradingClient:
    """Get or create trading client instance."""
    global _trading_client
    if _trading_client is None:
        _trading_client = TradingClient(
            settings.api_key,
            settings.api_secret,
            paper=settings.paper,
            url_override=settings.trade_api_url,
        )
    return _trading_client


def get_stock_historical_client() -> StockHistoricalDataClient:
    """Get or create stock historical data client instance."""
    global _stock_historical_client
    if _stock_historical_client is None:
        _stock_historical_client = StockHistoricalDataClient(
            settings.api_key, settings.api_secret, url_override=settings.data_api_url
        )
    return _stock_historical_client


def get_stock_stream_client() -> StockDataStream:
    """Get or create stock data stream client instance."""
    global _stock_data_stream_client
    if _stock_data_stream_client is None:
        _stock_data_stream_client = StockDataStream(
            settings.api_key, settings.api_secret, url_override=settings.stream_data_wss
        )
    return _stock_data_stream_client


def get_option_historical_client() -> OptionHistoricalDataClient:
    """Get or create option historical data client instance."""
    global _option_historical_client
    if _option_historical_client is None:
        _option_historical_client = OptionHistoricalDataClient(
            api_key=settings.api_key, secret_key=settings.api_secret
        )
    return _option_historical_client


# ============================================================================
# Global Stock Streaming State (Alpaca allows only ONE stream connection)
# ============================================================================

_global_stock_stream = None
_stock_stream_thread = None
_stock_stream_active = False
_stock_stream_subscriptions = {
    "trades": set(),
    "quotes": set(),
    "bars": set(),
    "updated_bars": set(),
    "daily_bars": set(),
    "statuses": set(),
}

# Configurable stock data buffers - no artificial limits for active stocks
_stock_data_buffers = {}
_stock_stream_stats = defaultdict(int)
_stock_stream_start_time = None
_stock_stream_end_time = None
_stock_stream_config = {
    "feed": "sip",
    "buffer_size": None,  # Unlimited by default
    "duration_seconds": None,  # No time limit by default
}

# ============================================================================
# Stock Streaming Helper Classes and Functions
# ============================================================================


class ConfigurableStockDataBuffer:
    """Thread-safe buffer with configurable size limits for stock market data"""

    def __init__(self, max_size: Optional[int] = None):
        """
        Initialize buffer with optional size limit.

        Args:
            max_size: Maximum number of items to store. None = unlimited.
                     For active stocks, consider 10000+ or unlimited.
        """
        if max_size is None:
            self.data = deque()  # Unlimited
        else:
            self.data = deque(maxlen=max_size)  # Limited

        self.lock = threading.Lock()
        self.last_update = time.time()
        self.max_size = max_size
        self.total_items_added = 0  # Track total even if some are dropped

    def add(self, item):
        with self.lock:
            self.data.append(item)
            self.last_update = time.time()
            self.total_items_added += 1

    def get_recent(self, seconds: int = 60):
        with self.lock:
            cutoff = time.time() - seconds
            return [item for item in self.data if item.get("timestamp", 0) > cutoff]

    def get_all(self):
        with self.lock:
            return list(self.data)

    def get_stats(self):
        with self.lock:
            return {
                "current_size": len(self.data),
                "max_size": self.max_size,
                "total_added": self.total_items_added,
                "last_update": self.last_update,
                "is_unlimited": self.max_size is None,
            }

    def clear(self):
        with self.lock:
            self.data.clear()
            self.total_items_added = 0


def get_or_create_stock_buffer(
    symbol: str, data_type: str, buffer_size: Optional[int] = None
) -> ConfigurableStockDataBuffer:
    """Get or create a buffer for a stock symbol/data_type combination"""
    buffer_key = f"{symbol}_{data_type}"
    if buffer_key not in _stock_data_buffers:
        effective_size = (
            buffer_size
            if buffer_size is not None
            else _stock_stream_config.get("buffer_size")
        )
        _stock_data_buffers[buffer_key] = ConfigurableStockDataBuffer(effective_size)
    return _stock_data_buffers[buffer_key]


def check_stock_stream_duration_limit():
    """Check if stock stream should stop due to duration limit"""
    if _stock_stream_config["duration_seconds"] and _stock_stream_start_time:
        elapsed = time.time() - _stock_stream_start_time
        if elapsed >= _stock_stream_config["duration_seconds"]:
            return True
    return False


# Global handler functions for stock streaming
async def handle_stock_trade(trade):
    """Global handler for stock trade data"""
    try:
        if check_stock_stream_duration_limit():
            return

        trade_data = {
            "type": "trade",
            "symbol": trade.symbol,
            "price": float(trade.price),
            "size": trade.size,
            "exchange": trade.exchange,
            "timestamp": time.time(),
            "datetime": trade.timestamp.isoformat(),
            "conditions": getattr(trade, "conditions", []),
            "tape": getattr(trade, "tape", None),
        }

        buffer = get_or_create_stock_buffer(
            trade.symbol, "trades", _stock_stream_config.get("buffer_size")
        )
        buffer.add(trade_data)
        _stock_stream_stats["trades"] += 1

    except Exception as e:
        print(f"Error handling trade: {e}")


async def handle_stock_quote(quote):
    """Global handler for stock quote data"""
    try:
        if check_stock_stream_duration_limit():
            return

        quote_data = {
            "type": "quote",
            "symbol": quote.symbol,
            "bid_price": float(quote.bid_price),
            "ask_price": float(quote.ask_price),
            "bid_size": quote.bid_size,
            "ask_size": quote.ask_size,
            "spread": float(quote.ask_price - quote.bid_price),
            "timestamp": time.time(),
            "datetime": quote.timestamp.isoformat(),
            "bid_exchange": getattr(quote, "bid_exchange", None),
            "ask_exchange": getattr(quote, "ask_exchange", None),
        }

        buffer = get_or_create_stock_buffer(
            quote.symbol, "quotes", _stock_stream_config.get("buffer_size")
        )
        buffer.add(quote_data)
        _stock_stream_stats["quotes"] += 1

    except Exception as e:
        print(f"Error handling quote: {e}")


async def handle_stock_bar(bar):
    """Global handler for stock bar data"""
    try:
        if check_stock_stream_duration_limit():
            return

        bar_data = {
            "type": "bar",
            "symbol": bar.symbol,
            "open": float(bar.open),
            "high": float(bar.high),
            "low": float(bar.low),
            "close": float(bar.close),
            "volume": bar.volume,
            "trade_count": getattr(bar, "trade_count", None),
            "vwap": float(getattr(bar, "vwap", 0)),
            "timestamp": time.time(),
            "datetime": bar.timestamp.isoformat(),
        }

        buffer = get_or_create_stock_buffer(
            bar.symbol, "bars", _stock_stream_config.get("buffer_size")
        )
        buffer.add(bar_data)
        _stock_stream_stats["bars"] += 1

    except Exception as e:
        print(f"Error handling bar: {e}")
