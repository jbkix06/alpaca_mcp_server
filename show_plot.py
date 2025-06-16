#!/usr/bin/env python3
"""
Persistent plot viewer - keeps plots open until explicitly closed
"""

import os
import sys
import subprocess
import glob
import argparse
from pathlib import Path

def find_latest_plot(symbol=None):
    """Find the most recent plot file"""
    # Search in temp directories
    plot_dirs = glob.glob("/tmp/alpaca_plots_*")
    
    all_plots = []
    for plot_dir in plot_dirs:
        if symbol:
            pattern = f"{plot_dir}/{symbol.upper()}_*.png"
        else:
            pattern = f"{plot_dir}/*.png"
        plots = glob.glob(pattern)
        all_plots.extend(plots)
    
    if not all_plots:
        return None
    
    # Return the most recent plot
    return max(all_plots, key=os.path.getctime)

def show_plot_persistent(filepath):
    """Show plot with persistent viewer"""
    if not os.path.exists(filepath):
        print(f"❌ Plot file not found: {filepath}")
        return False
    
    print(f"📈 Opening plot: {os.path.basename(filepath)}")
    
    # Try different viewers with persistent options
    viewers = [
        ['eog', '--new-instance', filepath],  # GNOME Image Viewer (stays open)
        ['feh', '--auto-zoom', '--borderless', filepath],  # Lightweight, persistent
        ['gthumb', filepath],  # GNOME thumbnail viewer
        ['display', '-immutable', '-zoom', '100%', '-geometry', '+0+0', filepath],  # ImageMagick at actual size
        ['xdg-open', filepath]  # System default
    ]
    
    for viewer_cmd in viewers:
        try:
            # Use Popen to start in background but don't wait
            process = subprocess.Popen(
                viewer_cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print(f"✅ Plot opened with {viewer_cmd[0]} (PID: {process.pid})")
            print(f"💡 To keep it open: Don't click outside the window or press ESC")
            return True
        except FileNotFoundError:
            continue
        except Exception as e:
            print(f"⚠️  {viewer_cmd[0]} failed: {e}")
            continue
    
    print("❌ No suitable image viewer found")
    return False

def main():
    parser = argparse.ArgumentParser(description="Show persistent plot viewer")
    parser.add_argument("--symbol", "-s", help="Symbol to show plot for")
    parser.add_argument("--file", "-f", help="Specific plot file to show")
    parser.add_argument("--latest", "-l", action="store_true", help="Show latest plot")
    
    args = parser.parse_args()
    
    if args.file:
        filepath = args.file
    elif args.latest or args.symbol:
        filepath = find_latest_plot(args.symbol)
        if not filepath:
            if args.symbol:
                print(f"❌ No plots found for symbol: {args.symbol}")
            else:
                print("❌ No plots found")
            return
    else:
        # Interactive selection
        filepath = find_latest_plot()
        if not filepath:
            print("❌ No plots found")
            return
    
    success = show_plot_persistent(filepath)
    if success:
        print(f"📍 Plot location: {filepath}")
    
if __name__ == "__main__":
    main()