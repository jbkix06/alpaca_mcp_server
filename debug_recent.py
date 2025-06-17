#!/usr/bin/env python3
"""Debug the recent_seconds functionality directly."""

import sys
import time
sys.path.append('/home/jjoravet/alpaca-mcp-server-enhanced')

# Import the actual module to access the global variables
import sys
settings_module = sys.modules.get('alpaca_mcp_server.config.settings')
if settings_module is None:
    import alpaca_mcp_server.config.settings
    settings_module = sys.modules['alpaca_mcp_server.config.settings']

def debug_recent_functionality():
    """Test the get_recent functionality."""
    print("=== DEBUGGING get_recent FUNCTIONALITY ===")
    
    # Check what buffers exist
    print(f"Available buffers: {list(settings_module._stock_data_buffers.keys())}")
    
    for buffer_key, buffer in settings_module._stock_data_buffers.items():
        print(f"\n=== Buffer: {buffer_key} ===")
        
        # Get all data
        all_data = buffer.get_all()
        print(f"Total items: {len(all_data)}")
        
        if all_data:
            # Show last few items with timestamps
            print("Last 3 items with raw timestamps:")
            for i, item in enumerate(all_data[-3:]):
                timestamp = item.get('timestamp')
                print(f"  Item {i+1}: timestamp={repr(timestamp)} (type: {type(timestamp)})")
                print(f"            price={item.get('price')}, size={item.get('size')}")
        
        # Test get_recent with different time windows
        for seconds in [10, 30, 60, 300]:
            recent_data = buffer.get_recent(seconds)
            print(f"Recent {seconds}s: {len(recent_data)} items")
            
            if recent_data:
                # Show first item from recent data
                first_item = recent_data[0]
                timestamp = first_item.get('timestamp')
                print(f"  First recent item: timestamp={repr(timestamp)}")
                
                # Manual time check
                current_time = time.time()
                cutoff = current_time - seconds
                print(f"  Current time: {current_time}")
                print(f"  Cutoff time: {cutoff}")
                
                # Try to parse the timestamp manually
                if isinstance(timestamp, str):
                    try:
                        from datetime import datetime, timezone
                        import re
                        
                        if timestamp.endswith('Z'):
                            timestamp_clean = timestamp[:-1]
                            dt = datetime.fromisoformat(timestamp_clean).replace(tzinfo=timezone.utc)
                        elif re.search(r'[+-]\d{2}:\d{2}$', timestamp):
                            dt = datetime.fromisoformat(timestamp)
                        else:
                            dt = datetime.fromisoformat(timestamp)
                        
                        parsed_ts = dt.timestamp()
                        print(f"  Parsed timestamp: {parsed_ts}")
                        print(f"  Age: {current_time - parsed_ts:.1f} seconds")
                        print(f"  Should pass filter: {parsed_ts > cutoff}")
                    except Exception as e:
                        print(f"  Parse error: {e}")
                elif isinstance(timestamp, (int, float)):
                    print(f"  Numeric timestamp: {timestamp}")
                    print(f"  Age: {current_time - timestamp:.1f} seconds")
                    print(f"  Should pass filter: {timestamp > cutoff}")
            
            print()

if __name__ == "__main__":
    debug_recent_functionality()