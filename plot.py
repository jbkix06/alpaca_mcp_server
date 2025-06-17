#!/usr/bin/env python3
"""
Multi-Symbol Peak Detection Test Script with MCP Server Display
Modified to work with MCP server that uses ImageMagick display
"""

import os
import sys
import logging
import numpy as np
import requests
import subprocess
import tempfile
import threading
from datetime import datetime, timedelta
from scipy.signal import filtfilt
from scipy.signal.windows import hann as hanning

# Set matplotlib backend BEFORE any other matplotlib imports
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server environments
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from dateutil import parser as date_parser
from dateutil import tz
import pytz

# Add current directory to path to import peakdetect
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from peakdetect import peakdetect

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global plot manager for MCP server
class MCPPlotManager:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp(prefix='alpaca_plots_')
        self.generated_plots = []
        self.display_processes = []
        logger.info(f"Plot temp directory: {self.temp_dir}")
    
    def generate_filename(self, symbol, plot_type="peak_detection"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{symbol}_{plot_type}_{timestamp}.png"
        return os.path.join(self.temp_dir, filename)
    
    def save_and_display(self, fig, filepath):
        try:
            fig.savefig(filepath, dpi=100, bbox_inches='tight', facecolor='white')
            plt.close(fig)
            self.generated_plots.append(filepath)
            logger.info(f"Plot saved: {filepath}")
            
            # Display with ImageMagick (non-blocking) and track process
            process = subprocess.Popen(['display', filepath], 
                                     stdout=subprocess.DEVNULL, 
                                     stderr=subprocess.DEVNULL)
            self.display_processes.append(process)
            logger.info(f"Plot displayed with ImageMagick (PID: {process.pid})")
            
            # Start cleanup monitoring in background
            self._schedule_cleanup_on_close(process)
            return True
        except Exception as e:
            logger.error(f"Failed to save/display plot: {e}")
            return False
    
    def _schedule_cleanup_on_close(self, process):
        """Monitor display process and cleanup when it closes"""
        def monitor_and_cleanup():
            try:
                # Wait for the display process to terminate
                process.wait()
                logger.info(f"Display process {process.pid} closed, cleaning up temp directory")
                self.cleanup()
            except Exception as e:
                logger.error(f"Error monitoring display process: {e}")
        
        # Start monitoring in background thread
        cleanup_thread = threading.Thread(target=monitor_and_cleanup, daemon=True)
        cleanup_thread.start()
    
    def cleanup(self):
        """Clean up temporary directory and all plot files"""
        try:
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                logger.info(f"Cleaned up temporary directory: {self.temp_dir}")
            self.generated_plots.clear()
        except Exception as e:
            logger.error(f"Failed to cleanup temp directory: {e}")
    
    def force_cleanup(self):
        """Force cleanup of all display processes and temp files"""
        # Terminate any remaining display processes
        for process in self.display_processes:
            try:
                if process.poll() is None:  # Process still running
                    process.terminate()
                    logger.info(f"Terminated display process {process.pid}")
            except Exception as e:
                logger.error(f"Error terminating process: {e}")
        
        self.display_processes.clear()
        self.cleanup()

# Global instance
mcp_plot_manager = MCPPlotManager()


def convert_to_nyc_timezone(timestamp_str):
    """Convert timestamp string to NYC/EDT timezone for plotting"""
    try:
        # Parse the timestamp (handles UTC timestamps from Alpaca API)
        dt = date_parser.parse(timestamp_str)

        # If timezone-naive, assume UTC
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=pytz.UTC)

        # Convert to NYC timezone (handles EDT/EST automatically)
        nyc_tz = pytz.timezone("America/New_York")
        dt_nyc = dt.astimezone(nyc_tz)

        return dt_nyc
    except Exception as e:
        logger.warning(f"Failed to convert timestamp {timestamp_str}: {e}")
        # Return the original timestamp as fallback to avoid None values
        try:
            return (
                date_parser.parse(timestamp_str)
                if isinstance(timestamp_str, str)
                else timestamp_str
            )
        except:
            # Last resort: return current time in NYC timezone
            return datetime.now(pytz.timezone("America/New_York"))


def zero_phase_filter(data, window_len=11):
    """Apply zero-phase low-pass filter using Hanning window"""
    data = np.array(data)

    min_required_length = window_len * 3
    if len(data) < min_required_length:
        if len(data) < 5:
            return data
        else:
            window_len = max(3, len(data) // 3)
            if window_len % 2 == 0:
                window_len -= 1

    if window_len % 2 == 0:
        window_len += 1

    window = hanning(window_len)
    window = window / window.sum()

    pad_len = window_len // 2
    padded = np.pad(data, pad_len, mode="edge")
    filtered_padded = filtfilt(window, 1.0, padded)
    filtered = filtered_padded[pad_len:-pad_len]

    return filtered


class HistoricalDataFetcher:
    """Fetch historical bar data from Alpaca API"""

    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()
        self.session.headers.update(
            {"APCA-API-KEY-ID": self.api_key, "APCA-API-SECRET-KEY": self.api_secret}
        )

    def get_trading_days(self, days):
        """Get the last N trading days"""
        now = datetime.now()
        start_date = now - timedelta(days=days * 3)

        url = "https://paper-api.alpaca.markets/v2/calendar"
        params = {
            "start": start_date.strftime("%Y-%m-%d"),
            "end": now.strftime("%Y-%m-%d"),
        }

        try:
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()

            calendar_data = response.json()
            if not calendar_data:
                logger.warning("No trading calendar data received")
                return []

            trading_days = [day["date"] for day in calendar_data if day.get("date")]
            if len(trading_days) < days:
                logger.warning(
                    "Only %s trading days available, requested %s",
                    len(trading_days),
                    days,
                )

            trading_days = trading_days[-days:] if trading_days else []
            trading_days.sort(reverse=True)

            logger.info("Retrieved %s trading days", len(trading_days))
            return trading_days

        except requests.exceptions.RequestException as e:
            logger.error("Request error retrieving trading calendar: %s", e)
            return []
        except Exception as e:
            logger.error("Error retrieving trading calendar: %s", e)
            return []

    def fetch_historical_bars(
        self, symbols, timeframe, start_date, end_date, feed="sip"
    ):
        """Fetch historical bar data for multiple symbols in one API call"""
        if not symbols:
            logger.warning("No symbols provided for historical data fetch")
            return None

        url = "https://data.alpaca.markets/v2/stocks/bars"
        params = {
            "symbols": ",".join(symbols),
            "timeframe": timeframe,
            "start": start_date,
            "end": end_date,
            "limit": 10000,
            "adjustment": "split",
            "feed": feed,
            "sort": "asc",
        }

        try:
            logger.info(
                "Fetching historical bars: %s symbols, %s, %s to %s",
                len(symbols),
                timeframe,
                start_date,
                end_date,
            )

            response = self.session.get(url, params=params, timeout=60)
            response.raise_for_status()

            data = response.json()

            if not isinstance(data, dict):
                logger.error("Invalid response format from bars API")
                return None

            if "bars" not in data:
                logger.warning("No 'bars' key in API response")
                return None

            bars_data = data["bars"]
            total_bars = 0

            for symbol, bars in bars_data.items():
                if bars:
                    total_bars += len(bars)
                else:
                    logger.warning("No bars received for symbol %s", symbol)

            logger.info(
                "Successfully fetched %s bars for %s symbols",
                total_bars,
                len(bars_data),
            )
            return bars_data

        except requests.exceptions.Timeout:
            logger.error("Timeout fetching historical bars")
            return None
        except requests.exceptions.RequestException as e:
            logger.error("Request error fetching historical bars: %s", e)
            return None
        except Exception as e:
            logger.error("Error fetching historical bars: %s", e)
            return None


def process_bars_for_peaks(symbol, bars, window_len=11, lookahead=1):
    """Process bars to compute filtered close prices and detect peaks/troughs"""
    try:
        if not bars or len(bars) < lookahead * 2:
            logger.warning(
                "Not enough bars for %s to detect peaks (need at least %d)",
                symbol,
                lookahead * 2,
            )
            return None

        close_prices = np.array([float(bar["c"]) for bar in bars])
        timestamps = [bar["t"] for bar in bars]

        logger.info("Processing %d bars for %s", len(close_prices), symbol)
        logger.info(
            "Close price range: %.4f - %.4f", close_prices.min(), close_prices.max()
        )

        filtered_prices = zero_phase_filter(close_prices, window_len)
        time_axis = np.arange(len(close_prices))

        max_peaks, min_peaks = peakdetect(
            filtered_prices, x_axis=time_axis, lookahead=lookahead, delta=0
        )

        logger.info("Found %d peaks and %d troughs", len(max_peaks), len(min_peaks))

        peaks_data = []
        for peak_idx, peak_value in max_peaks:
            idx = int(peak_idx)
            if 0 <= idx < len(bars):
                peaks_data.append(
                    {
                        "index": idx,
                        "timestamp": timestamps[idx],
                        "filtered_price": float(peak_value),
                        "original_price": float(close_prices[idx]),
                        "volume": int(bars[idx]["v"]),
                    }
                )

        troughs_data = []
        for trough_idx, trough_value in min_peaks:
            idx = int(trough_idx)
            if 0 <= idx < len(bars):
                troughs_data.append(
                    {
                        "index": idx,
                        "timestamp": timestamps[idx],
                        "filtered_price": float(trough_value),
                        "original_price": float(close_prices[idx]),
                        "volume": int(bars[idx]["v"]),
                    }
                )

        results = {
            "symbol": symbol,
            "total_bars": len(bars),
            "timestamps": timestamps,
            "original_prices": close_prices.tolist(),
            "filtered_prices": filtered_prices.tolist(),
            "peaks": peaks_data,
            "troughs": troughs_data,
            "filter_params": {"window_len": window_len, "lookahead": lookahead},
        }

        logger.info(
            "Processed %d bars for %s: %d peaks, %d troughs",
            len(bars),
            symbol,
            len(peaks_data),
            len(troughs_data),
        )

        return results

    except Exception as e:
        logger.error("Error processing bars for peaks in %s: %s", symbol, e)
        return None


def get_latest_signal(results):
    """Get the most recent peak or trough signal for a symbol"""
    if not results:
        return None

    peaks = results["peaks"]
    troughs = results["troughs"]

    if not peaks and not troughs:
        return None

    latest_signal = None
    latest_index = -1

    for peak in peaks:
        if peak["index"] > latest_index:
            latest_index = peak["index"]
            latest_signal = {
                "type": "Peak",
                "index": peak["index"],
                "timestamp": peak["timestamp"],
                "signal_price": peak["original_price"],
                "filtered_price": peak["filtered_price"],
                "volume": peak["volume"],
            }

    for trough in troughs:
        if trough["index"] > latest_index:
            latest_index = trough["index"]
            latest_signal = {
                "type": "Trough",
                "index": trough["index"],
                "timestamp": trough["timestamp"],
                "signal_price": trough["original_price"],
                "filtered_price": trough["filtered_price"],
                "volume": trough["volume"],
            }

    if latest_signal:
        total_bars = results["total_bars"]
        samples_ago = total_bars - 1 - latest_signal["index"]
        current_price = results["original_prices"][-1]

        latest_signal["samples_ago"] = samples_ago
        latest_signal["current_price"] = current_price
        latest_signal["price_change"] = current_price - latest_signal["signal_price"]
        latest_signal["price_change_pct"] = (
            latest_signal["price_change"] / latest_signal["signal_price"]
        ) * 100

    return latest_signal


def print_latest_signals_table(all_results):
    """Print a table showing the latest signal for each symbol"""
    if not all_results:
        return

    print("")
    print("=" * 115)
    print("LATEST PEAK/TROUGH SIGNALS")
    print("=" * 115)

    # Create header line safely
    col_widths = [8, 8, 6, 14, 14, 12, 10, 22]
    header_items = [
        "Symbol",
        "Signal",
        "Ago",
        "Signal $",
        "Current $",
        "Change",
        "Change%",
        "Time (NYC/EDT)",
    ]

    header_line = ""
    for i, (header, width) in enumerate(zip(header_items, col_widths)):
        if i == 0:
            header_line += header.rjust(width)
        else:
            header_line += " " + header.rjust(width)

    print(header_line)
    print("-" * 115)

    signals_found = 0

    for results in all_results:
        symbol = results["symbol"]
        latest_signal = get_latest_signal(results)

        if latest_signal:
            signals_found += 1
            signal_type = latest_signal["type"]
            samples_ago = latest_signal["samples_ago"]
            signal_price = latest_signal["signal_price"]
            current_price = latest_signal["current_price"]
            price_change = latest_signal["price_change"]
            price_change_pct = latest_signal["price_change_pct"]
            # Convert timestamp to NYC timezone for display
            raw_timestamp = latest_signal["timestamp"]
            try:
                nyc_timestamp = convert_to_nyc_timezone(raw_timestamp)
                if hasattr(nyc_timestamp, "strftime"):
                    formatted_timestamp = nyc_timestamp.strftime("%H:%M:%S %Z")
                else:
                    formatted_timestamp = raw_timestamp
            except:
                formatted_timestamp = raw_timestamp

            change_indicator = "+" if price_change >= 0 else "-"
            signal_indicator = "^P" if signal_type == "Peak" else "vT"

            # Format each column safely
            cols = [
                symbol.rjust(col_widths[0]),
                signal_indicator.rjust(col_widths[1]),
                str(samples_ago).rjust(col_widths[2]),
                "{:.4f}".format(signal_price).rjust(col_widths[3]),
                "{:.4f}".format(current_price).rjust(col_widths[4]),
                "{}{}".format(
                    change_indicator, "{:.4f}".format(abs(price_change))
                ).rjust(col_widths[5]),
                "{:.2f}%".format(price_change_pct).rjust(col_widths[6]),
                formatted_timestamp.rjust(col_widths[7]),
            ]

            print(" ".join(cols))
        else:
            # No signal row
            cols = [
                symbol.rjust(col_widths[0]),
                "None".rjust(col_widths[1]),
                "-".rjust(col_widths[2]),
                "-".rjust(col_widths[3]),
                "-".rjust(col_widths[4]),
                "-".rjust(col_widths[5]),
                "-".rjust(col_widths[6]),
                "-".rjust(col_widths[7]),
            ]

            print(" ".join(cols))

    print("-" * 115)
    print("Signals found: {}/{} symbols".format(signals_found, len(all_results)))
    print("=" * 115)


def plot_single_symbol(results):
    """Create plot for single symbol - modified for MCP server"""
    if not results:
        logger.error("No results to plot")
        return None

    # Set matplotlib timezone to NYC
    matplotlib.rcParams["timezone"] = "America/New_York"

    plt.style.use("seaborn-v0_8-darkgrid")
    fig, ax = plt.subplots(figsize=(12, 8))  # Smaller size for server

    # Set timezone for x-axis BEFORE plotting
    nyc_tz = tz.gettz("America/New_York")
    ax.xaxis_date(tz=nyc_tz)

    # Parse timestamps and convert to NYC/EDT timezone
    try:
        timestamps = [convert_to_nyc_timezone(ts) for ts in results["timestamps"]]
        if len(timestamps) != len(results["original_prices"]):
            logger.warning("Timestamp count mismatch, using indices for x-axis")
            timestamps = range(len(results["original_prices"]))
    except Exception as e:
        logger.warning(f"Could not parse timestamps: {e}, using indices for x-axis")
        timestamps = range(len(results["original_prices"]))

    # Extract data
    original_prices = np.array(results["original_prices"])
    filtered_prices = np.array(results["filtered_prices"])
    peaks = results["peaks"]
    troughs = results["troughs"]

    # Main price lines
    ax.plot(
        timestamps,
        original_prices,
        color="#2E86AB",
        linewidth=1.5,
        alpha=0.7,
        label="Original Close Prices",
        zorder=1,
    )

    ax.plot(
        timestamps,
        filtered_prices,
        color="#A23B72",
        linewidth=2.5,
        label="Filtered (Hanning w={})".format(results["filter_params"]["window_len"]),
        zorder=2,
    )

    # Plot peaks at original prices with actual price annotations
    if peaks:
        peak_times = [
            (
                convert_to_nyc_timezone(peak["timestamp"])
                if isinstance(timestamps[0], datetime)
                else peak["index"]
            )
            for peak in peaks
        ]
        peak_original_prices = [peak["original_price"] for peak in peaks]

        ax.scatter(
            peak_times,
            peak_original_prices,
            color="#F18F01",
            s=80,
            marker="^",
            label="Peaks ({})".format(len(peaks)),
            zorder=4,
            edgecolors="black",
            linewidth=1,
        )

        # Add peak annotations with actual prices
        for i, (time, price) in enumerate(zip(peak_times, peak_original_prices)):
            ax.annotate(
                "P{}: ${:.4f}".format(i + 1, price),
                (time, price),
                xytext=(5, 15),
                textcoords="offset points",
                fontsize=9,
                fontweight="bold",
                color="#F18F01",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
            )

    # Plot troughs at original prices with actual price annotations
    if troughs:
        trough_times = [
            (
                convert_to_nyc_timezone(trough["timestamp"])
                if isinstance(timestamps[0], datetime)
                else trough["index"]
            )
            for trough in troughs
        ]
        trough_original_prices = [trough["original_price"] for trough in troughs]

        ax.scatter(
            trough_times,
            trough_original_prices,
            color="#C73E1D",
            s=80,
            marker="v",
            label="Troughs ({})".format(len(troughs)),
            zorder=4,
            edgecolors="black",
            linewidth=1,
        )

        # Add trough annotations with actual prices
        for i, (time, price) in enumerate(zip(trough_times, trough_original_prices)):
            ax.annotate(
                "T{}: ${:.4f}".format(i + 1, price),
                (time, price),
                xytext=(5, -20),
                textcoords="offset points",
                fontsize=9,
                fontweight="bold",
                color="#C73E1D",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
            )

    # Styling
    ax.set_ylabel("Price ($)", fontsize=12, fontweight="bold")

    # Create title
    symbol = results["symbol"]
    total_bars = results["total_bars"]
    window_len = results["filter_params"]["window_len"]
    lookahead = results["filter_params"]["lookahead"]

    title = (
        "{} - Peak & Trough Detection\n"
        "Bars: {} | Filter: Hanning(w={}) | "
        "Lookahead: {} | Peaks: {} | Troughs: {}"
    ).format(symbol, total_bars, window_len, lookahead, len(peaks), len(troughs))

    ax.set_title(title, fontsize=14, fontweight="bold", pad=20)

    # Format x-axis for datetime with NYC/EDT timezone
    if isinstance(timestamps[0], datetime):
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M", tz=nyc_tz))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha="right")
        ax.set_xlabel("Time (NYC/EDT)", fontsize=12, fontweight="bold")
    else:
        ax.set_xlabel("Time", fontsize=12, fontweight="bold")

    # Grid
    ax.grid(True, linestyle="--", alpha=0.7, color="gray")

    # Legend - simple positioning
    ax.legend(loc='best', frameon=True, fancybox=True, shadow=True, fontsize=11, framealpha=0.9)

    # Calculate stats for text box
    price_min = original_prices.min()
    price_max = original_prices.max()
    noise_reduction = (
        (original_prices.std() - filtered_prices.std()) / original_prices.std() * 100
    )

    stats_text = (
        "Price Range: ${:.4f} - ${:.4f}\n"
        "Filter Smoothing: {:.1f}%\n"
        "Peak/Trough Ratio: {}/{}"
    ).format(price_min, price_max, noise_reduction, len(peaks), len(troughs))

    # Simple stats box positioning
    ax.text(
        0.02,
        0.98,
        stats_text,
        transform=ax.transAxes,
        fontsize=10,
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8),
    )

    plt.tight_layout()

    # Save and display using MCP plot manager
    filepath = mcp_plot_manager.generate_filename(symbol)
    success = mcp_plot_manager.save_and_display(fig, filepath)
    
    if success:
        return filepath
    else:
        return None


def print_summary(results):
    """Print summary for a single symbol"""
    if not results:
        return

    symbol = results["symbol"]
    print("\n📊 RESULTS SUMMARY for {}:".format(symbol))
    print("   • Total bars processed: {}".format(results["total_bars"]))
    print(
        "   • Filter parameters: window_len={}, lookahead={}".format(
            results["filter_params"]["window_len"],
            results["filter_params"]["lookahead"],
        )
    )
    print(
        "   • Price range: ${:.4f} - ${:.4f}".format(
            min(results["original_prices"]), max(results["original_prices"])
        )
    )
    print(
        "   • Peaks detected: {} (at original close prices)".format(
            len(results["peaks"])
        )
    )
    print(
        "   • Troughs detected: {} (at original close prices)".format(
            len(results["troughs"])
        )
    )

    if results["peaks"] or results["troughs"]:
        if results["peaks"]:
            print("   PEAKS (at original close prices):")
            for i, peak in enumerate(results["peaks"]):
                print(
                    "     P{}: Index {}, ${:.4f} (filtered: ${:.4f})".format(
                        i + 1,
                        peak["index"],
                        peak["original_price"],
                        peak["filtered_price"],
                    )
                )

        if results["troughs"]:
            print("   TROUGHS (at original close prices):")
            for i, trough in enumerate(results["troughs"]):
                print(
                    "     T{}: Index {}, ${:.4f} (filtered: ${:.4f})".format(
                        i + 1,
                        trough["index"],
                        trough["original_price"],
                        trough["filtered_price"],
                    )
                )


def main():
    """Main test function - modified for MCP server"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Test zero-phase filtering and peak detection on multiple stock symbols",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--symbols",
        "-s",
        type=str,
        required=True,
        help="Comma-delimited stock symbols to analyze (e.g., 'AAPL,TSLA,MSFT')",
    )

    parser.add_argument(
        "--timeframe",
        "-t",
        type=str,
        default="1Min",
        choices=[
            "1Min",
            "2Min",
            "5Min",
            "15Min",
            "30Min",
            "1Hour",
            "2Hour",
            "4Hour",
            "1Day",
        ],
        help="Bar timeframe",
    )

    parser.add_argument(
        "--days",
        "-d",
        type=int,
        default=1,
        help="Number of trading days to fetch (1-30)",
    )

    parser.add_argument(
        "--window",
        "-w",
        type=int,
        default=11,
        help="Hanning filter window length (must be odd, 3-101)",
    )

    parser.add_argument(
        "--lookahead",
        "-l",
        type=int,
        default=1,
        help="Peak detection lookahead parameter (1-50)",
    )

    parser.add_argument(
        "--feed",
        "-f",
        type=str,
        default="sip",
        choices=["iex", "sip", "otc"],
        help="Data feed to use",
    )

    parser.add_argument(
        "--no-plot",
        action="store_true",
        help="Skip plotting (useful for batch processing)",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validate arguments
    if args.days < 1 or args.days > 30:
        logger.error("Days must be between 1 and 30")
        sys.exit(1)

    if args.window < 3 or args.window > 101:
        logger.error("Window length must be between 3 and 101")
        sys.exit(1)

    # Ensure window length is odd
    if args.window % 2 == 0:
        args.window += 1
        logger.info("Window length adjusted to %d (must be odd)", args.window)

    if args.lookahead < 1 or args.lookahead > 50:
        logger.error("Lookahead must be between 1 and 50")
        sys.exit(1)

    # Check for required environment variables
    api_key = os.environ.get("APCA_API_KEY_ID")
    api_secret = os.environ.get("APCA_API_SECRET_KEY")

    if not api_key or not api_secret:
        logger.error(
            "APCA_API_KEY_ID and APCA_API_SECRET_KEY environment variables must be set"
        )
        sys.exit(1)

    # Extract and validate symbols
    if not args.symbols:
        logger.error("No symbols provided")
        sys.exit(1)

    # Parse comma-delimited symbols and convert to uppercase
    test_symbols = [
        symbol.strip().upper() for symbol in args.symbols.split(",") if symbol.strip()
    ]

    if not test_symbols:
        logger.error("No valid symbols found")
        sys.exit(1)

    if len(test_symbols) > 20:
        logger.error("Too many symbols (max 20)")
        sys.exit(1)

    days = args.days
    timeframe = args.timeframe
    feed = args.feed
    window_len = args.window
    lookahead = args.lookahead

    logger.info("Starting multi-symbol peak detection test...")
    logger.info("Symbols: %s", test_symbols)
    logger.info("Days: %d, Timeframe: %s, Feed: %s", days, timeframe, feed)
    logger.info("Filter params: window_len=%d, lookahead=%d", window_len, lookahead)

    try:
        # Initialize data fetcher
        fetcher = HistoricalDataFetcher(api_key, api_secret)

        # Get trading days
        trading_days = fetcher.get_trading_days(days)
        if not trading_days:
            logger.error("No trading days found")
            return

        start_date = trading_days[-1]
        end_date = trading_days[0]

        logger.info("Fetching data from %s to %s", start_date, end_date)

        # Fetch historical data for all symbols in one API call
        bars_data = fetcher.fetch_historical_bars(
            test_symbols, timeframe, start_date, end_date, feed
        )

        if not bars_data:
            logger.error("No historical data received")
            return

        # Process each symbol
        all_results = []
        for symbol in test_symbols:
            if symbol not in bars_data:
                logger.warning("No data for symbol %s", symbol)
                continue

            bars = bars_data[symbol]
            if not bars:
                logger.warning("No bars for symbol %s", symbol)
                continue

            # Process bars for peaks
            results = process_bars_for_peaks(symbol, bars, window_len, lookahead)

            if results:
                all_results.append(results)
                print_summary(results)
            else:
                logger.error("Failed to process %s", symbol)

        if not all_results:
            logger.error("No symbols processed successfully")
            return

        # Print latest signals table
        print_latest_signals_table(all_results)

        # Generate plots if not disabled
        if not args.no_plot:
            logger.info("Creating plots with MCP display...")
            plot_files = []
            for results in all_results:
                filepath = plot_single_symbol(results)
                if filepath:
                    plot_files.append(filepath)
                    print(f"✅ Plot generated and displayed: {filepath}")
                else:
                    print(f"❌ Failed to generate plot for {results['symbol']}")
            
            print(f"\n📈 Generated {len(plot_files)} plots in: {mcp_plot_manager.temp_dir}")
        else:
            logger.info("Plotting skipped")

        # Print overall summary
        print("\n🎯 OVERALL SUMMARY:")
        print(
            "   • Symbols processed: {}/{}".format(len(all_results), len(test_symbols))
        )
        print(
            "   • Total peaks found: {}".format(
                sum(len(r["peaks"]) for r in all_results)
            )
        )
        print(
            "   • Total troughs found: {}".format(
                sum(len(r["troughs"]) for r in all_results)
            )
        )

        if all_results:
            avg_bars = np.mean([r["total_bars"] for r in all_results])
            print("   • Average bars per symbol: {:.0f}".format(avg_bars))

        logger.info("Multi-symbol peak detection test completed")

    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
        mcp_plot_manager.force_cleanup()
    except Exception as e:
        logger.error("Test failed: %s", e)
        mcp_plot_manager.force_cleanup()
        raise


if __name__ == "__main__":
    main()
