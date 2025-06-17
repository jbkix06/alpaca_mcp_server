# Fix for get_stock_stream_data Timestamp Parsing Issue

## Problem Description

The `get_stock_stream_data` tool was collecting streaming data (showing thousands of items in buffer stats) but when querying recent data with `get_stock_stream_data(symbol="CERO", data_type="trades", recent_seconds=10)`, it returned "No trades data found".

## Root Cause Analysis

The issue was in the `ConfigurableStockDataBuffer.get_recent()` method in `/home/jjoravet/alpaca-mcp-server-enhanced/alpaca_mcp_server/config/settings.py`.

### The Problem
1. **Data Storage**: Streaming handlers store timestamps as ISO format strings using `trade.timestamp.isoformat()` (e.g., "2025-06-17T15:40:55.520908+00:00")
2. **Data Retrieval**: The `get_recent()` method tried to parse these as simple float values
3. **Parsing Failure**: ISO format strings cannot be converted to float directly, causing all data to be filtered out

### Technical Details
- **File**: `alpaca_mcp_server/tools/streaming_tools.py` stores timestamps as: `trade.timestamp.isoformat()`
- **Buffer Method**: `ConfigurableStockDataBuffer.get_recent()` tried: `timestamp = float(timestamp)`
- **Result**: All streaming data was considered invalid and filtered out

## Solution Implemented

### Updated get_recent() Method
Enhanced the timestamp parsing logic in `ConfigurableStockDataBuffer.get_recent()` to handle multiple timestamp formats:

```python
def get_recent(self, seconds: int = 60):
    with self.lock:
        cutoff = time.time() - seconds
        result = []
        for item in self.data:
            timestamp = item.get("timestamp", 0)
            # Handle both string and numeric timestamps
            if isinstance(timestamp, str):
                try:
                    # Try parsing ISO format first (e.g., "2025-06-17T14:30:25.123456")
                    from datetime import datetime
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    timestamp = dt.timestamp()
                except (ValueError, TypeError):
                    try:
                        # Fallback to direct float conversion
                        timestamp = float(timestamp)
                    except (ValueError, TypeError):
                        continue  # Skip invalid timestamps
            if timestamp > cutoff:
                result.append(item)
        return result
```

### Key Improvements
1. **ISO Format Support**: Properly parses ISO format timestamps from Alpaca API
2. **Timezone Handling**: Handles timezone-aware timestamps (converts 'Z' to '+00:00')
3. **Backward Compatibility**: Still supports numeric timestamps for legacy data
4. **Error Resilience**: Gracefully handles invalid timestamps without crashing

## Testing

### Created Comprehensive Test Suite
- **File**: `alpaca_mcp_server/tests/unit/test_buffer_timestamp_parsing.py`
- **Coverage**: 8 test cases covering all timestamp formats and edge cases
- **Result**: All tests pass

### Test Cases Include
1. ISO format timestamp parsing
2. Numeric timestamp parsing  
3. String numeric timestamp parsing
4. Mixed timestamp formats
5. Old data filtering
6. Invalid timestamp handling
7. Timezone-aware ISO timestamps
8. Data retrieval verification

## Files Modified

1. **`alpaca_mcp_server/config/settings.py`**
   - Enhanced `ConfigurableStockDataBuffer.get_recent()` method
   - Added robust timestamp parsing logic

2. **`alpaca_mcp_server/tests/unit/test_buffer_timestamp_parsing.py`** (NEW)
   - Comprehensive test suite for timestamp parsing
   - Ensures fix works and prevents regressions

## Verification

The fix has been verified to work with:
- ✅ Real Alpaca ISO format timestamps
- ✅ Numeric timestamps (backward compatibility)
- ✅ Timezone-aware timestamps
- ✅ Invalid timestamp handling
- ✅ All existing streaming functionality

## Impact

- **✅ Fixed**: `get_stock_stream_data()` now returns recent data properly
- **✅ Maintained**: All existing functionality preserved
- **✅ Enhanced**: Better error handling for malformed timestamps
- **✅ Future-Proof**: Comprehensive test coverage prevents regressions

The streaming data collection and retrieval system now works as expected, allowing traders to access recent market data for analysis and decision-making.