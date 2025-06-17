#!/usr/bin/env python3
"""Debug script to examine timestamp formats in streaming buffers."""

import sys
import os
sys.path.append('/home/jjoravet/alpaca-mcp-server-enhanced')

from alpaca_mcp_server.config.settings import _stock_data_buffers
import time
from datetime import datetime

def debug_timestamps():
    """Debug the timestamp formats in the buffers."""
    print("=== DEBUG TIMESTAMP FORMATS ===")
    print(f"Current time: {time.time()}")
    print(f"Current datetime: {datetime.now().isoformat()}")
    print()
    
    # Check available buffers
    print(f"Available buffers: {list(_stock_data_buffers.keys())}")
    print()
    
    for buffer_key, buffer in _stock_data_buffers.items():
        print(f"=== Buffer: {buffer_key} ===")
        data = buffer.get_all()
        print(f"Total items: {len(data)}")
        
        if data:
            print("Last 3 items with raw timestamps:")
            for i, item in enumerate(data[-3:]):
                print(f"  Item {i+1}:")
                timestamp = item.get('timestamp')
                print(f"    timestamp: {repr(timestamp)} (type: {type(timestamp)})")
                print(f"    price: {item.get('price')}")
                
                # Try to parse the timestamp
                if isinstance(timestamp, str):
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        unix_timestamp = dt.timestamp()
                        print(f"    parsed as: {unix_timestamp}")
                        print(f"    age: {time.time() - unix_timestamp:.1f} seconds")
                    except Exception as e:
                        print(f"    parse error: {e}")
                elif isinstance(timestamp, (int, float)):
                    print(f"    unix timestamp, age: {time.time() - timestamp:.1f} seconds")
                print()
        print()

if __name__ == "__main__":
    debug_timestamps()