#!/usr/bin/env python3
"""Debug the actual timestamp format in live streaming data."""

import sys
import time
from datetime import datetime, timezone
import re
sys.path.append('/home/jjoravet/alpaca-mcp-server-enhanced')

def test_timestamp_parsing_logic(timestamp_str):
    """Test the exact timestamp parsing logic from get_recent."""
    print(f"Testing timestamp: {repr(timestamp_str)}")
    
    try:
        # Apply the exact logic from get_recent method
        if isinstance(timestamp_str, str):
            # Parse timestamp correctly based on timezone info
            if timestamp_str.endswith('Z'):
                # UTC timestamp with Z suffix
                timestamp_clean = timestamp_str[:-1]
                dt = datetime.fromisoformat(timestamp_clean).replace(tzinfo=timezone.utc)
            elif re.search(r'[+-]\d{2}:\d{2}$', timestamp_str):
                # Timezone-aware timestamp
                dt = datetime.fromisoformat(timestamp_str)
            else:
                # No timezone info, assume local time
                dt = datetime.fromisoformat(timestamp_str)
            
            # Convert to UTC timestamp
            parsed_timestamp = dt.timestamp()
            print(f"  Parsed to: {parsed_timestamp}")
            
            # Check against current time
            current_time = time.time()
            age = current_time - parsed_timestamp
            print(f"  Current time: {current_time}")
            print(f"  Age: {age:.1f} seconds")
            
            # Test against different cutoffs
            for seconds in [30, 60, 300, 3600]:
                cutoff = current_time - seconds
                passes = parsed_timestamp > cutoff
                print(f"  Passes {seconds}s filter: {passes}")
            
        else:
            print(f"  Not a string timestamp")
            
    except Exception as e:
        print(f"  Error: {e}")

def test_common_formats():
    """Test common timestamp formats that might come from Alpaca."""
    
    now_utc = datetime.now(timezone.utc)
    now_local = datetime.now()
    
    # Common formats
    test_formats = [
        now_utc.isoformat().replace('+00:00', 'Z'),  # 2025-06-17T15:53:25.123456Z
        now_utc.isoformat(),                          # 2025-06-17T15:53:25.123456+00:00  
        now_local.isoformat(),                        # 2025-06-17T10:53:25.123456 (local)
        '2025-06-17T15:53:25.123456Z',               # Fixed UTC format
        '2025-06-17T15:53:25+00:00',                 # Fixed UTC format without microseconds
        '2025-06-17T10:53:25.123456',                # Fixed local format
        str(time.time()),                             # Unix timestamp as string
    ]
    
    print("=== TESTING COMMON TIMESTAMP FORMATS ===")
    for fmt in test_formats:
        test_timestamp_parsing_logic(fmt)
        print()

if __name__ == "__main__":
    test_common_formats()