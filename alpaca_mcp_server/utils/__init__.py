"""Utility modules for the Alpaca MCP server."""

# Import utilities with graceful error handling
try:
    from . import stock_analyzer

    STOCK_ANALYZER_AVAILABLE = True
except ImportError:
    STOCK_ANALYZER_AVAILABLE = False

try:
    from . import tickers

    TICKERS_AVAILABLE = True
except ImportError:
    TICKERS_AVAILABLE = False

try:
    from . import snapshot

    SNAPSHOT_AVAILABLE = True
except ImportError:
    SNAPSHOT_AVAILABLE = False

try:
    from . import get_snapshot

    GET_SNAPSHOT_AVAILABLE = True
except ImportError:
    GET_SNAPSHOT_AVAILABLE = False

__all__ = [
    "stock_analyzer",
    "tickers",
    "snapshot",
    "get_snapshot",
    "STOCK_ANALYZER_AVAILABLE",
    "TICKERS_AVAILABLE",
    "SNAPSHOT_AVAILABLE",
    "GET_SNAPSHOT_AVAILABLE",
]
