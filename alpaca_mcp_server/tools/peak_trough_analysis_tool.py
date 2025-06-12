"""Peak and trough analysis tool for day trading signals"""

import logging
import numpy as np
from datetime import datetime, timedelta
import sys
import os

from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

# Add parent directory to path to import peakdetect
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, project_root)

try:
    from peakdetect import peakdetect
except ImportError:
    # Fallback if peakdetect not found
    def peakdetect(y_axis, x_axis=None, lookahead=1, delta=0):
        """Fallback peak detection if peakdetect module not available"""
        peaks = []
        troughs = []
        if x_axis is None:
            x_axis = list(range(len(y_axis)))

        for i in range(1, len(y_axis) - 1):
            if y_axis[i] > y_axis[i - 1] and y_axis[i] > y_axis[i + 1]:
                peaks.append((x_axis[i], y_axis[i]))
            elif y_axis[i] < y_axis[i - 1] and y_axis[i] < y_axis[i + 1]:
                troughs.append((x_axis[i], y_axis[i]))

        return peaks, troughs


try:
    from ..config import get_stock_historical_client
except ImportError:
    # Try absolute import
    from alpaca_mcp_server.config import get_stock_historical_client

logger = logging.getLogger(__name__)


def zero_phase_filter(data: np.ndarray, window_len: int = 11) -> np.ndarray:
    """
    Apply zero-phase low-pass filter using Hanning window

    This function is copied from server.py to ensure consistency
    """
    from scipy.signal import filtfilt
    from scipy.signal.windows import hann as hanning

    # Convert to numpy array
    data = np.array(data)

    # If data is too short, return it as-is or use a smaller window
    min_required_length = window_len * 3  # filtfilt needs at least 3x the filter length
    if len(data) < min_required_length:
        # Use a smaller window or just return the data
        if len(data) < 5:
            return data  # Too short to filter
        else:
            # Use a smaller window that's appropriate for the data length
            window_len = max(3, len(data) // 3)
            if window_len % 2 == 0:
                window_len -= 1

    # Ensure window length is odd
    if window_len % 2 == 0:
        window_len += 1

    # Create Hanning window
    window = hanning(window_len)
    window = window / window.sum()  # Normalize

    # Apply zero-phase filtering using filtfilt
    # Pad the signal to handle edge effects
    pad_len = window_len // 2
    padded = np.pad(data, pad_len, mode="edge")

    # For zero-phase response, we use filtfilt
    filtered_padded = filtfilt(window, 1.0, padded)

    # Remove padding
    filtered = filtered_padded[pad_len:-pad_len]

    return filtered


async def analyze_peaks_and_troughs(
    symbols: str,
    timeframe: str = "1Min",
    days: int = 1,
    limit: int = 1000,
    window_len: int = 11,
    lookahead: int = 1,
    delta: float = 0.0,
    min_peak_distance: int = 5,
) -> str:
    """
    Fetch intraday bar data and identify peaks and troughs for day trading signals using
    zero-phase Hanning filtering followed by peak detection algorithm.

    This tool applies professional technical analysis to identify precise entry/exit points:
    1. Fetches historical intraday bar data for specified symbols
    2. Applies zero-phase low-pass Hanning filtering to remove noise while preserving timing
    3. Runs peak detection algorithm on filtered data to find optimal turning points
    4. Returns original prices at detected peaks/troughs for executable trading signals

    Args:
        symbols: Comma-separated list of stock symbols (e.g., "AAPL,MSFT,NVDA")
        timeframe: Bar timeframe - "1Min", "5Min", "15Min", "30Min", "1Hour" (default: "1Min")
        days: Number of trading days of historical data (default: 1, max: 30)
        limit: Maximum number of bars to fetch (default: 1000, max: 10000)
        window_len: Hanning filter window length - controls smoothing (default: 11, must be odd, range: 3-101)
        lookahead: Peak detection lookahead parameter (default: 1, range: 1-50)
        delta: Minimum peak/trough amplitude threshold (default: 0.0, use 0 for penny stocks)
        min_peak_distance: Minimum bars between peaks for filtering noise (default: 5)

    Returns:
        Formatted string with comprehensive peak/trough analysis including:
        - Technical summary with price ranges and bar counts
        - Recent peaks (resistance/sell signals) with timestamps and prices
        - Recent troughs (support/buy signals) with timestamps and prices
        - Trading signal recommendations (BUY/LONG, SELL/SHORT, WATCH)
        - Distance and percentage analysis from latest signals

    Examples:
        analyze_peaks_and_troughs("CGTL")  # Quick analysis of CGTL
        analyze_peaks_and_troughs("AAPL,MSFT", timeframe="5Min", days=2)  # 5min bars, 2 days
        analyze_peaks_and_troughs("NVDA", window_len=21, lookahead=3)  # More smoothing, wider lookahead
    """
    try:
        # Parse symbols
        symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]
        if not symbol_list:
            return "Error: No valid symbols provided"

        # Validate parameters
        if limit < 1 or limit > 10000:
            limit = min(max(limit, 1), 10000)

        if days < 1 or days > 30:
            days = min(max(days, 1), 30)

        if window_len < 3 or window_len > 101:
            window_len = 11
        if window_len % 2 == 0:
            window_len += 1

        if lookahead < 1 or lookahead > 50:
            lookahead = min(max(lookahead, 1), 50)

        if delta < 0:
            delta = 0.0

        if min_peak_distance < 1:
            min_peak_distance = 5

        # Get the data client
        try:
            data_client = get_stock_historical_client()
        except Exception as e:
            logger.error(f"Failed to get data client: {e}")
            return f"Error: Failed to initialize data client - {str(e)}"

        # Map timeframe string to TimeFrame enum
        timeframe_map = {
            "1Min": TimeFrame.Minute,
            "5Min": TimeFrame(5, "Min"),
            "15Min": TimeFrame(15, "Min"),
            "30Min": TimeFrame(30, "Min"),
            "1Hour": TimeFrame.Hour,
            "1Day": TimeFrame.Day,
        }

        tf = timeframe_map.get(timeframe, TimeFrame.Minute)

        # Calculate start time based on days parameter
        now = datetime.utcnow()
        start = now - timedelta(days=days + 2)  # Extra buffer for weekends/holidays

        # Create request
        request = StockBarsRequest(
            symbol_or_symbols=symbol_list,
            timeframe=tf,
            start=start,
            end=now,
            limit=limit * len(symbol_list),  # Total limit across all symbols
            feed="sip",
        )

        # Fetch bars
        bars_response = data_client.get_stock_bars(request)

        # Access the actual data from the response
        bars_data = (
            bars_response.data if hasattr(bars_response, "data") else bars_response
        )

        # Process each symbol
        results = []
        results.append("# Peak and Trough Analysis for Day Trading\n")
        results.append(
            f"Parameters: {timeframe} bars, {days} days, Window: {window_len}, Lookahead: {lookahead}\n"
        )
        results.append(f"Delta: {delta}, Min Peak Distance: {min_peak_distance}\n")
        results.append(
            f"Analysis Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n"
        )
        results.append("=" * 80 + "\n")

        for symbol in symbol_list:
            results.append(f"\n## {symbol}\n")

            # Get bars for this symbol
            if symbol not in bars_data:
                results.append(f"No data available for {symbol}\n")
                continue

            symbol_bars = bars_data[symbol]
            if not symbol_bars:
                results.append(f"No bars found for {symbol}\n")
                continue

            # Extract close prices and timestamps
            close_prices = []
            timestamps = []
            for bar in symbol_bars:
                close_prices.append(float(bar.close))
                timestamps.append(bar.timestamp)

            close_prices = np.array(close_prices)

            if len(close_prices) < lookahead * 2:
                results.append(
                    f"Insufficient data for {symbol} (need at least {lookahead * 2} bars)\n"
                )
                continue

            # Apply zero-phase Hanning filter
            filtered_prices = zero_phase_filter(close_prices, window_len)

            # Create time axis (indices)
            time_axis = np.arange(len(close_prices))

            # Detect peaks and troughs
            max_peaks, min_peaks = peakdetect(
                filtered_prices, x_axis=time_axis, lookahead=lookahead, delta=delta
            )

            # Filter peaks/troughs by minimum distance if specified
            if min_peak_distance > 1:
                # Filter peaks that are too close together
                filtered_max_peaks = []
                filtered_min_peaks = []

                for i, (idx, value) in enumerate(max_peaks):
                    if i == 0 or (idx - max_peaks[i - 1][0]) >= min_peak_distance:
                        filtered_max_peaks.append((idx, value))

                for i, (idx, value) in enumerate(min_peaks):
                    if i == 0 or (idx - min_peaks[i - 1][0]) >= min_peak_distance:
                        filtered_min_peaks.append((idx, value))

                max_peaks = filtered_max_peaks
                min_peaks = filtered_min_peaks

            # Format results
            results.append(f"Total bars analyzed: {len(close_prices)}\n")
            results.append(
                f"Price range: ${min(close_prices):.4f} - ${max(close_prices):.4f}\n"
            )
            results.append(f"Current price: ${close_prices[-1]:.4f}\n\n")

            # Peaks (potential sell signals)
            results.append(f"### Peaks (Resistance/Sell Signals): {len(max_peaks)}\n")
            if max_peaks:
                # Get last 5 peaks
                recent_peaks = max_peaks[-5:] if len(max_peaks) > 5 else max_peaks
                for idx, peak_value in recent_peaks:
                    idx = int(idx)
                    if 0 <= idx < len(timestamps):
                        peak_time = timestamps[idx]
                        original_price = close_prices[idx]
                        filtered_price = peak_value
                        results.append(
                            f"  - {peak_time.strftime('%H:%M:%S')}: ${original_price:.4f} (filtered: ${filtered_price:.4f})\n"
                        )

                # Latest peak analysis
                if max_peaks:
                    latest_peak_idx = int(max_peaks[-1][0])
                    latest_peak_price = close_prices[latest_peak_idx]
                    current_price = close_prices[-1]
                    peak_distance = len(close_prices) - 1 - latest_peak_idx

                    results.append(
                        f"\nLatest peak: ${latest_peak_price:.4f} ({peak_distance} bars ago)\n"
                    )
                    if (
                        current_price < latest_peak_price * 0.995
                    ):  # More than 0.5% below peak
                        results.append(
                            "⬇️ Price below recent peak - potential SHORT opportunity\n"
                        )

            # Troughs (potential buy signals)
            results.append(f"\n### Troughs (Support/Buy Signals): {len(min_peaks)}\n")
            if min_peaks:
                # Get last 5 troughs
                recent_troughs = min_peaks[-5:] if len(min_peaks) > 5 else min_peaks
                for idx, trough_value in recent_troughs:
                    idx = int(idx)
                    if 0 <= idx < len(timestamps):
                        trough_time = timestamps[idx]
                        original_price = close_prices[idx]
                        filtered_price = trough_value
                        results.append(
                            f"  - {trough_time.strftime('%H:%M:%S')}: ${original_price:.4f} (filtered: ${filtered_price:.4f})\n"
                        )

                # Latest trough analysis
                if min_peaks:
                    latest_trough_idx = int(min_peaks[-1][0])
                    latest_trough_price = close_prices[latest_trough_idx]
                    current_price = close_prices[-1]
                    trough_distance = len(close_prices) - 1 - latest_trough_idx

                    results.append(
                        f"\nLatest trough: ${latest_trough_price:.4f} ({trough_distance} bars ago)\n"
                    )
                    if (
                        current_price > latest_trough_price * 1.005
                    ):  # More than 0.5% above trough
                        results.append(
                            "⬆️ Price above recent trough - potential LONG opportunity\n"
                        )

            # Trading signals summary
            results.append("\n### Trading Signal Summary:\n")

            # Determine current position relative to peaks/troughs
            if max_peaks and min_peaks:
                latest_peak_idx = int(max_peaks[-1][0])
                latest_trough_idx = int(min_peaks[-1][0])

                if latest_peak_idx > latest_trough_idx:
                    # Last signal was a peak
                    peak_price = close_prices[latest_peak_idx]
                    price_from_peak = ((current_price - peak_price) / peak_price) * 100
                    results.append(f"📊 Last signal: PEAK at ${peak_price:.4f}\n")
                    results.append(
                        f"📍 Current position: {price_from_peak:+.2f}% from peak\n"
                    )

                    if price_from_peak < -1.0:
                        results.append(
                            "🔴 SELL/SHORT Signal - Price declining from peak\n"
                        )
                    elif price_from_peak < -0.5:
                        results.append("⚠️ Watch for further decline or reversal\n")
                else:
                    # Last signal was a trough
                    trough_price = close_prices[latest_trough_idx]
                    price_from_trough = (
                        (current_price - trough_price) / trough_price
                    ) * 100
                    results.append(f"📊 Last signal: TROUGH at ${trough_price:.4f}\n")
                    results.append(
                        f"📍 Current position: {price_from_trough:+.2f}% from trough\n"
                    )

                    if price_from_trough > 1.0:
                        results.append(
                            "🟢 BUY/LONG Signal - Price rising from trough\n"
                        )
                    elif price_from_trough > 0.5:
                        results.append("⚠️ Watch for continued rise or reversal\n")

            results.append("-" * 40 + "\n")

        return "".join(results)

    except Exception as e:
        logger.error(f"Error in analyze_peaks_and_troughs: {e}")
        return f"Error analyzing peaks and troughs: {str(e)}"
