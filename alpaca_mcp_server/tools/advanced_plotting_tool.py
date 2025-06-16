"""
Advanced Multi-Symbol Peak Detection with Professional Plotting
Integration of peak_trough_detection_plot.py as an MCP tool.
"""

import os
import sys
import asyncio
import logging
import tempfile
import subprocess
from typing import List, Dict, Any
from pathlib import Path

# Import the existing plotting functionality
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    # Import from the standalone plotting script that we restored
    from peak_trough_detection_plot import (
        HistoricalDataFetcher,
        process_bars_for_peaks,
        plot_single_symbol,
        plot_combined_subplots,
        plot_overlay,
        print_latest_signals_table,
    )

    PLOTTING_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Plotting functionality not available: {e}")
    PLOTTING_AVAILABLE = False


def create_headless_plot(results, plot_dir, dpi=100):
    """Create a single symbol plot in headless mode using matplotlib with proper display"""
    import matplotlib

    matplotlib.use("Agg")  # Use non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from dateutil import tz
    import numpy as np
    import subprocess
    from datetime import datetime

    if not results:
        return None

    try:
        # Set up the plot with high resolution size
        plt.style.use("seaborn-v0_8-darkgrid")
        fig, ax = plt.subplots(figsize=(20, 12))

        # Extract data
        symbol = results["symbol"]
        timestamps = results["timestamps"]
        original_prices = np.array(results["original_prices"])
        filtered_prices = np.array(results["filtered_prices"])
        peaks = results["peaks"]
        troughs = results["troughs"]

        # Convert timestamps to datetime objects for plotting
        try:
            from peak_trough_detection_plot import convert_to_nyc_timezone

            timestamps_dt = [convert_to_nyc_timezone(ts) for ts in timestamps]
            use_datetime = True
        except:
            timestamps_dt = range(len(original_prices))
            use_datetime = False

        # Plot main price lines
        ax.plot(
            timestamps_dt,
            original_prices,
            color="#2E86AB",
            linewidth=1.5,
            alpha=0.7,
            label="Original Close Prices",
            zorder=1,
        )

        ax.plot(
            timestamps_dt,
            filtered_prices,
            color="#A23B72",
            linewidth=2.5,
            label=f"Filtered (Hanning w={results['filter_params']['window_len']})",
            zorder=2,
        )

        # Plot peaks
        if peaks:
            peak_times = []
            peak_prices = []
            for peak in peaks:
                if use_datetime:
                    peak_times.append(convert_to_nyc_timezone(peak["timestamp"]))
                else:
                    peak_times.append(peak["index"])
                peak_prices.append(peak["original_price"])

            ax.scatter(
                peak_times,
                peak_prices,
                color="#F18F01",
                s=80,
                marker="^",
                label=f"Peaks ({len(peaks)})",
                zorder=4,
                edgecolors="none",
                linewidths=0,
            )

            # Add peak annotations
            for i, (time, price) in enumerate(zip(peak_times, peak_prices)):
                ax.annotate(
                    f"P{i + 1}: ${price:.4f}",
                    (time, price),
                    xytext=(5, 15),
                    textcoords="offset points",
                    fontsize=9,
                    fontweight="bold",
                    color="#F18F01",
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
                )

        # Plot troughs
        if troughs:
            trough_times = []
            trough_prices = []
            for trough in troughs:
                if use_datetime:
                    trough_times.append(convert_to_nyc_timezone(trough["timestamp"]))
                else:
                    trough_times.append(trough["index"])
                trough_prices.append(trough["original_price"])

            ax.scatter(
                trough_times,
                trough_prices,
                color="#C73E1D",
                s=80,
                marker="v",
                label=f"Troughs ({len(troughs)})",
                zorder=4,
                edgecolors="none",
                linewidths=0,
            )

            # Add trough annotations
            for i, (time, price) in enumerate(zip(trough_times, trough_prices)):
                ax.annotate(
                    f"T{i + 1}: ${price:.4f}",
                    (time, price),
                    xytext=(5, -20),
                    textcoords="offset points",
                    fontsize=9,
                    fontweight="bold",
                    color="#C73E1D",
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
                )

        # Set title and labels
        title = (
            f"{symbol} - Peak & Trough Detection\n"
            f"Bars: {results['total_bars']} | Filter: Hanning(w={results['filter_params']['window_len']}) | "
            f"Lookahead: {results['filter_params']['lookahead']} | Peaks: {len(peaks)} | Troughs: {len(troughs)}"
        )
        ax.set_title(title, fontsize=14, fontweight="bold", pad=20)
        ax.set_ylabel("Price ($)", fontsize=12, fontweight="bold")

        # Format x-axis
        if use_datetime:
            nyc_tz = tz.gettz("America/New_York")
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M", tz=nyc_tz))
            ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha="right")
            ax.set_xlabel("Time (NYC/EDT)", fontsize=12, fontweight="bold")
        else:
            ax.set_xlabel("Time", fontsize=12, fontweight="bold")

        # Grid and legend
        ax.grid(True, linestyle="--", alpha=0.7, color="gray")
        ax.legend(
            loc="best",
            frameon=True,
            fancybox=True,
            shadow=True,
            fontsize=11,
            framealpha=0.9,
        )

        # Stats box
        price_min = original_prices.min()
        price_max = original_prices.max()
        noise_reduction = (
            (original_prices.std() - filtered_prices.std())
            / original_prices.std()
            * 100
        )

        stats_text = (
            f"Price Range: ${price_min:.4f} - ${price_max:.4f}\n"
            f"Filter Smoothing: {noise_reduction:.1f}%\n"
            f"Peak/Trough Ratio: {len(peaks)}/{len(troughs)}"
        )

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

        # Save the plot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(plot_dir, f"{symbol}_peak_detection_{timestamp}.png")

        # Save with specified DPI and proper file close (preserving exact figure size)
        fig.savefig(filename, dpi=dpi, bbox_inches='tight', facecolor="white", edgecolor='none')
        
        # Get actual image dimensions for debug
        fig_width_inches, fig_height_inches = fig.get_size_inches()
        pixel_width = int(fig_width_inches * dpi)
        pixel_height = int(fig_height_inches * dpi)
        
        plt.close(fig)  # Important: close the figure to free memory
        
        # Log the actual dimensions
        logging.info(f"Plot saved: {pixel_width}x{pixel_height} pixels ({fig_width_inches}x{fig_height_inches} inches @ {dpi} DPI)")

        # Auto-display disabled - use show_plot.py instead
        logging.info(f"Plot saved (auto-display disabled): {filename}")

        return filename, pixel_width, pixel_height

    except Exception as e:
        logging.error(f"Error creating headless plot for {symbol}: {e}")
        return None, None, None


async def generate_peak_trough_plots(
    symbols: str,
    timeframe: str = "1Min",
    days: int = 1,
    window_len: int = 11,
    lookahead: int = 1,
    plot_mode: str = "single",
    save_plots: bool = True,
    display_plots: bool = False,
    dpi: int = 100,
) -> str:
    """
    Generate professional peak/trough analysis plots for multiple symbols.

    This tool uses advanced zero-phase Hanning filter and peak detection
    algorithms to create publication-quality plots with:
    - Original and filtered price data
    - Peak/trough detection with actual price annotations
    - Multi-symbol overlay and comparison views
    - Professional styling and auto-positioned legends

    Args:
        symbols: Comma-separated symbols (e.g., "AAPL,MSFT,TSLA")
        timeframe: Bar timeframe ("1Min", "5Min", "15Min", etc.)
        days: Number of trading days (1-30)
        window_len: Hanning filter window length (3-101, must be odd)
        lookahead: Peak detection sensitivity (1-50)
        plot_mode: "single", "combined", "overlay", or "all"
        save_plots: Save plots as PNG files
        display_plots: Automatically display plots using system image viewer
        dpi: Image resolution (72-400, recommended: 100 for screen, 400 for ultra-high quality)

    Returns:
        Analysis results with plot file paths and signal summary
    """

    if not PLOTTING_AVAILABLE:
        return """
❌ ADVANCED PLOTTING NOT AVAILABLE

The advanced plotting functionality requires additional dependencies.
Please install matplotlib and scipy:

pip install matplotlib scipy

FALLBACK:
Use get_stock_peak_trough_analysis() for text-based analysis without plots.
        """

    try:
        # Validate parameters
        if window_len % 2 == 0:
            window_len += 1

        if days < 1 or days > 30:
            return "❌ Days must be between 1 and 30"

        if window_len < 3 or window_len > 101:
            return "❌ Window length must be between 3 and 101"

        if lookahead < 1 or lookahead > 50:
            return "❌ Lookahead must be between 1 and 50"

        # Parse symbols
        symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]
        if not symbol_list:
            return "❌ No valid symbols provided"

        if len(symbol_list) > 10:
            return "❌ Maximum 10 symbols allowed for plotting"

        # Check API credentials
        api_key = os.environ.get("APCA_API_KEY_ID")
        api_secret = os.environ.get("APCA_API_SECRET_KEY")

        if not api_key or not api_secret:
            return """
❌ API CREDENTIALS NOT CONFIGURED

Please set environment variables:
- APCA_API_KEY_ID
- APCA_API_SECRET_KEY

Current paper trading status: {os.environ.get('PAPER', 'Not set')}
            """

        # Create temporary directory for plots
        plot_dir = tempfile.mkdtemp(prefix="alpaca_plots_")

        # Initialize data fetcher
        fetcher = HistoricalDataFetcher(api_key, api_secret)

        # Get trading days (run in thread pool to avoid blocking)
        trading_days = await asyncio.to_thread(fetcher.get_trading_days, days)
        if not trading_days:
            return "❌ No trading days found for the specified period"

        start_date = trading_days[-1]
        end_date = trading_days[0]

        # Fetch historical data
        bars_data = await asyncio.to_thread(
            fetcher.fetch_historical_bars, symbol_list, timeframe, start_date, end_date
        )

        if not bars_data:
            return "❌ No historical data received from Alpaca API"

        # Process each symbol
        all_results = []
        for symbol in symbol_list:
            if symbol not in bars_data or not bars_data[symbol]:
                continue

            bars = bars_data[symbol]

            # Process bars for peaks (run in thread pool)
            results = await asyncio.to_thread(
                process_bars_for_peaks, symbol, bars, window_len, lookahead
            )

            if results:
                all_results.append(results)

        if not all_results:
            return f"❌ No symbols processed successfully from {symbol_list}"

        # Generate plots based on mode
        plot_files = []

        if plot_mode in ["single", "all"]:
            for results in all_results:
                try:
                    # Generate plot using matplotlib in headless mode
                    plot_result = await asyncio.to_thread(
                        create_headless_plot, results, plot_dir, dpi
                    )
                    if plot_result:
                        if isinstance(plot_result, tuple):
                            plot_file, width, height = plot_result
                            results['plot_dimensions'] = f"{width}x{height}"
                        else:
                            plot_file = plot_result
                        plot_files.append(plot_file)
                except Exception as e:
                    logging.warning(f"Failed to plot {results['symbol']}: {e}")
                    import traceback

                    logging.warning(f"Traceback: {traceback.format_exc()}")

        if plot_mode in ["combined", "all"] and len(all_results) > 1:
            try:
                fig = await asyncio.to_thread(
                    plot_combined_subplots, all_results, save_plots, plot_dir, dpi
                )
                if save_plots:
                    # Find the generated combined plot file
                    import glob

                    pattern = f"{plot_dir}/multi_symbol_*.png"
                    matches = glob.glob(pattern)
                    if matches:
                        plot_file = max(matches, key=os.path.getctime)
                        plot_files.append(plot_file)
            except Exception as e:
                logging.warning(f"Failed to create combined plot: {e}")

        if plot_mode in ["overlay", "all"] and len(all_results) > 1:
            try:
                fig = await asyncio.to_thread(
                    plot_overlay, all_results, save_plots, plot_dir, dpi
                )
                if save_plots:
                    # Find the generated overlay plot file
                    import glob

                    pattern = f"{plot_dir}/overlay_*.png"
                    matches = glob.glob(pattern)
                    if matches:
                        plot_file = max(matches, key=os.path.getctime)
                        plot_files.append(plot_file)
            except Exception as e:
                logging.warning(f"Failed to create overlay plot: {e}")

        # Generate summary statistics
        total_peaks = sum(len(r["peaks"]) for r in all_results)
        total_troughs = sum(len(r["troughs"]) for r in all_results)

        # Create signal summary
        signal_summary = generate_signal_summary_text(all_results)

        # Generate trading levels summary
        trading_levels = generate_trading_levels_summary(all_results)

        # Get dimensions info if available
        dimensions_info = ""
        if all_results and 'plot_dimensions' in all_results[0]:
            dimensions_info = f"\n• Plot dimensions: {all_results[0]['plot_dimensions']} pixels (16x10 inches @ 100 DPI)"
        
        # Handle display_plots functionality
        if display_plots and plot_files:
            display_success = []
            for plot_file in plot_files:
                try:
                    # Use the same display logic as show_plot.py
                    viewers = [
                        ['eog', '--new-instance', plot_file],
                        ['feh', '--auto-zoom', '--borderless', plot_file],
                        ['gthumb', plot_file],
                        ['display', '-immutable', '-zoom', '100%', '-geometry', '+0+0', plot_file],
                        ['xdg-open', plot_file]
                    ]
                    
                    plot_opened = False
                    for viewer_cmd in viewers:
                        try:
                            process = subprocess.Popen(
                                viewer_cmd,
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL
                            )
                            display_success.append(f"{os.path.basename(plot_file)} opened with {viewer_cmd[0]} (PID: {process.pid})")
                            plot_opened = True
                            break
                        except FileNotFoundError:
                            continue
                        except Exception:
                            continue
                    
                    if not plot_opened:
                        display_success.append(f"{os.path.basename(plot_file)} - No suitable viewer found")
                        
                except Exception as e:
                    display_success.append(f"{os.path.basename(plot_file)} - Display failed: {e}")
            
            display_info = (
                f"\n🖼️  PLOTS DISPLAYED:\n" + 
                "\n".join(f"• {msg}" for msg in display_success) +
                f"\n💡 Plots opened in background - windows should appear automatically"
                f"{dimensions_info}"
            )
        else:
            display_info = (
                f"\n💾 PLOTS SAVED:\n• {len(plot_files)} plot(s) saved to disk"
                f"{dimensions_info}"
                f"\n• Use: python show_plot.py --symbol {symbol_list[0]} to view"
                f"\n• In eog viewer: Press '1' for actual size, or use zoom controls"
            )

        return f"""
🎯 ADVANCED PEAK/TROUGH ANALYSIS WITH PROFESSIONAL PLOTS

📊 ANALYSIS SUMMARY:
• Symbols processed: {len(all_results)}/{len(symbol_list)}
• Total peaks detected: {total_peaks}
• Total troughs detected: {total_troughs}
• Filter: Zero-phase Hanning window (length={window_len})
• Sensitivity: Lookahead={lookahead}
• Timeframe: {timeframe} over {days} trading day(s)
• Date range: {start_date} to {end_date}

📈 PLOTS GENERATED:
• Plot mode: {plot_mode}
• Files saved: {len(plot_files)}
• Output directory: {os.path.basename(plot_dir)}

{signal_summary}

{trading_levels}

📁 PLOT FILES:
{chr(10).join(f"• {os.path.basename(f)}" for f in plot_files)}

📍 PLOT LOCATION: {plot_dir}
📋 DEBUG: display_plots={display_plots}, plot_files={len(plot_files)}
{display_info}

💡 NEXT ACTIONS:
• Review plots for visual confirmation of support/resistance levels
• Use identified levels for precise entry/exit planning
• Integrate with day_trading_workflow() for complete trading setup
• Set price alerts at key peak/trough levels
• Monitor with start_global_stock_stream() for real-time validation

✅ PROFESSIONAL TECHNICAL ANALYSIS WITH PUBLICATION-QUALITY PLOTS COMPLETE!
        """

    except Exception as e:
        return f"""
❌ PLOTTING TOOL ERROR

Error during advanced plot generation: {str(e)}

🔧 TROUBLESHOOTING:
1. Verify API credentials (APCA_API_KEY_ID, APCA_API_SECRET_KEY)
2. Check symbol validity and ensure they are actively traded
3. Confirm market hours or use historical data during off-hours
4. Try reducing number of symbols or shorter timeframe
5. Ensure matplotlib and scipy dependencies are installed

💡 FALLBACK ANALYSIS:
Use get_stock_peak_trough_analysis() for text-based peak/trough detection

SYSTEM INFO:
• Plotting available: {PLOTTING_AVAILABLE}
• Symbols requested: {symbols}
• Timeframe: {timeframe}
• Days: {days}
        """


def generate_signal_summary_text(all_results: List[Dict[str, Any]]) -> str:
    """Generate text-based signal summary for latest peaks and troughs."""
    if not all_results:
        return ""

    lines = ["\n🔍 LATEST TRADING SIGNALS:"]
    lines.append("=" * 50)

    for results in all_results:
        symbol = results["symbol"]
        peaks = results.get("peaks", [])
        troughs = results.get("troughs", [])
        current_price = results.get("current_price", 0)

        lines.append(f"\n{symbol} (Current: ${current_price:.4f}):")

        if peaks:
            latest_peak = peaks[-1]
            peak_price = latest_peak.get("original_price", 0)
            peak_time = latest_peak.get("time", "Unknown")
            lines.append(f"  🔺 Latest Peak: ${peak_price:.4f} at {peak_time}")
            lines.append("     Resistance level for short entries")

        if troughs:
            latest_trough = troughs[-1]
            trough_price = latest_trough.get("original_price", 0)
            trough_time = latest_trough.get("time", "Unknown")
            lines.append(f"  🔻 Latest Trough: ${trough_price:.4f} at {trough_time}")
            lines.append("     Support level for long entries")

        if not peaks and not troughs:
            lines.append("  ⚪ No significant signals detected")
            lines.append("     Consider adjusting sensitivity parameters")

    return "\n".join(lines)


def generate_trading_levels_summary(all_results: List[Dict[str, Any]]) -> str:
    """Generate trading levels summary with risk management."""
    if not all_results:
        return ""

    lines = ["\n📊 PRECISE TRADING LEVELS:"]
    lines.append("=" * 40)

    for results in all_results:
        symbol = results["symbol"]
        peaks = results.get("peaks", [])
        troughs = results.get("troughs", [])
        current_price = results.get("current_price", 0)

        if not peaks and not troughs:
            continue

        lines.append(f"\n{symbol} TRADING SETUP:")

        if peaks and troughs:
            latest_peak = peaks[-1] if peaks else None
            latest_trough = troughs[-1] if troughs else None

            if latest_peak and latest_trough:
                peak_price = latest_peak.get("original_price", 0)
                trough_price = latest_trough.get("original_price", 0)

                # Determine which is more recent
                peak_time = latest_peak.get("sample", 0)
                trough_time = latest_trough.get("sample", 0)

                if peak_time > trough_time:
                    # More recent peak - potential short setup
                    lines.append("  🔻 SHORT SETUP:")
                    lines.append(
                        f"     Entry: Below ${peak_price:.4f} (break of resistance)"
                    )
                    lines.append(f"     Target: ${trough_price:.4f} (support level)")
                    lines.append(f"     Stop: ${peak_price * 1.01:.4f} (1% above peak)")
                else:
                    # More recent trough - potential long setup
                    lines.append("  🔺 LONG SETUP:")
                    lines.append(
                        f"     Entry: Above ${trough_price:.4f} (break of support)"
                    )
                    lines.append(f"     Target: ${peak_price:.4f} (resistance level)")
                    lines.append(
                        f"     Stop: ${trough_price * 0.99:.4f} (1% below trough)"
                    )

                # Risk/Reward calculation
                if peak_price > 0 and trough_price > 0:
                    range_pct = (
                        abs(peak_price - trough_price)
                        / min(peak_price, trough_price)
                        * 100
                    )
                    lines.append(
                        f"     Range: {range_pct:.2f}% between support/resistance"
                    )

        elif peaks:
            latest_peak = peaks[-1]
            peak_price = latest_peak.get("original_price", 0)
            lines.append(f"  🔻 Resistance: ${peak_price:.4f}")
            lines.append("     Short entry below this level")

        elif troughs:
            latest_trough = troughs[-1]
            trough_price = latest_trough.get("original_price", 0)
            lines.append(f"  🔺 Support: ${trough_price:.4f}")
            lines.append("     Long entry above this level")

    lines.append("\n⚠️  RISK MANAGEMENT:")
    lines.append("• Use limit orders for precise entries")
    lines.append("• Position size based on stop distance")
    lines.append("• Monitor volume for breakout confirmation")
    lines.append("• Validate signals with real-time data")

    return "\n".join(lines)


# Export for MCP server registration
__all__ = ["generate_peak_trough_plots"]
