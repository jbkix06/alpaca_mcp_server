"""Streaming resources implementation."""

from datetime import datetime
from alpaca_mcp_server.config.settings import (
    _stock_stream_active,
    _stock_stream_subscriptions,
    _stock_data_buffers,
    _stock_stream_stats,
    _stock_stream_start_time,
    _stock_stream_config,
)


async def get_stream_status() -> dict:
    """Real-time streaming status and buffer statistics."""
    try:
        # Check if streaming is active
        if not _stock_stream_active:
            return {
                "status": "inactive",
                "streams_active": 0,
                "buffer_stats": {},
                "last_updated": datetime.now().isoformat(),
            }

        # Get all subscribed symbols
        all_symbols = set()
        for symbol_set in _stock_stream_subscriptions.values():
            all_symbols.update(symbol_set)

        # Get buffer statistics
        buffer_stats = {}
        total_messages = 0

        # Group buffers by symbol
        symbol_buffers = {}
        for buffer_key, buffer in _stock_data_buffers.items():
            symbol, data_type = buffer_key.rsplit("_", 1)
            if symbol not in symbol_buffers:
                symbol_buffers[symbol] = {}
            symbol_buffers[symbol][data_type] = buffer

        for symbol, buffers in symbol_buffers.items():
            symbol_stats = {}
            symbol_total = 0

            for data_type, buffer in buffers.items():
                buffer_size = len(buffer.get_all())
                stats = buffer.get_stats()
                symbol_stats[data_type] = {
                    "buffer_size": buffer_size,
                    "last_update": datetime.fromtimestamp(
                        stats["last_update"]
                    ).isoformat()
                    if stats["last_update"]
                    else None,
                }
                symbol_total += buffer_size

            buffer_stats[symbol] = {
                "data_types": symbol_stats,
                "total_messages": symbol_total,
            }
            total_messages += symbol_total

        # Calculate runtime
        runtime_seconds = (
            datetime.now().timestamp() - _stock_stream_start_time
            if _stock_stream_start_time
            else 0
        )

        return {
            "status": "active",
            "streams_active": len(all_symbols),
            "subscribed_symbols": list(all_symbols),
            "total_messages_buffered": total_messages,
            "buffer_stats": buffer_stats,
            "stream_duration_seconds": runtime_seconds,
            "feed_type": _stock_stream_config.get("feed", "unknown"),
            "configured_duration": _stock_stream_config.get("duration_seconds"),
            "last_updated": datetime.now().isoformat(),
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": "error",
            "streams_active": 0,
            "last_updated": datetime.now().isoformat(),
        }


async def get_stream_performance() -> dict:
    """Streaming performance metrics and health indicators."""
    try:
        if not _stock_stream_active:
            return {
                "status": "unavailable",
                "performance": "idle",
                "last_updated": datetime.now().isoformat(),
            }

        # Get all subscribed symbols
        all_symbols = set()
        for symbol_set in _stock_stream_subscriptions.values():
            all_symbols.update(symbol_set)

        # Calculate performance metrics
        total_symbols = len(all_symbols)
        total_buffers = len(_stock_data_buffers)
        total_messages = sum(
            len(buffer.get_all()) for buffer in _stock_data_buffers.values()
        )

        # Estimate memory usage (rough calculation)
        estimated_memory_mb = total_messages * 0.0002  # ~200 bytes per message estimate

        # Calculate event rates
        runtime_seconds = (
            datetime.now().timestamp() - _stock_stream_start_time
            if _stock_stream_start_time
            else 1
        )
        events_per_second = (
            sum(_stock_stream_stats.values()) / runtime_seconds
            if runtime_seconds > 0
            else 0
        )

        # Performance assessment
        if total_symbols == 0:
            performance_level = "idle"
        elif (
            total_symbols <= 10 and estimated_memory_mb < 50 and events_per_second < 100
        ):
            performance_level = "optimal"
        elif (
            total_symbols <= 50
            and estimated_memory_mb < 200
            and events_per_second < 500
        ):
            performance_level = "good"
        else:
            performance_level = "heavy"

        return {
            "status": "active",
            "performance_level": performance_level,
            "total_symbols_streaming": total_symbols,
            "total_buffers": total_buffers,
            "total_messages_buffered": total_messages,
            "events_per_second": round(events_per_second, 2),
            "estimated_memory_usage_mb": round(estimated_memory_mb, 2),
            "runtime_minutes": round(runtime_seconds / 60, 2),
            "recommended_action": {
                "idle": "Ready to start streaming",
                "optimal": "Performance is excellent",
                "good": "Performance is good",
                "heavy": "Consider reducing symbols or clearing buffers",
            }.get(performance_level, "Monitor performance"),
            "last_updated": datetime.now().isoformat(),
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": "error",
            "performance_level": "unknown",
            "last_updated": datetime.now().isoformat(),
        }
