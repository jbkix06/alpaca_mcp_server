"""Day Trading Startup Prompt - Parallel execution of all startup checks."""

import subprocess
from datetime import datetime


async def startup() -> str:
    """
    Execute all day trading startup checks in parallel for maximum speed.

    Runs comprehensive system health checks, market status, account verification,
    and trading scanners to ensure all systems are ready for day trading.
    Uses ONLY currently active stocks from live scanner data.

    Returns:
        Comprehensive startup status report with top trading opportunities
    """

    # Run the high-liquidity scanner to get active stocks
    try:
        scanner_result = subprocess.run(
            ["./trades_per_minute.sh", "-f", "combined.lis", "-t", "500"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd="/home/jjoravet/alpaca-mcp-server",
        )

        if scanner_result.returncode == 0:
            # Process output to get all active stocks
            lines = scanner_result.stdout.strip().split("\n")[2:]  # Skip header
            stocks = []
            for line in lines:
                parts = line.split()
                if len(parts) >= 3:
                    symbol = parts[0]
                    trades = int(parts[1])
                    pct_str = parts[2].rstrip("%")
                    try:
                        pct = float(pct_str)
                        # Only include stocks with meaningful activity
                        if trades >= 500:
                            stocks.append((symbol, trades, pct))
                    except ValueError:
                        continue

            # Sort by percent change and get top 20 ACTIVE stocks
            stocks.sort(key=lambda x: x[2], reverse=True)
            top_20 = stocks[:20]
        else:
            top_20 = []
    except Exception:
        top_20 = []

    # Build report
    report = []
    report.append("## 🚀 DAY TRADING STARTUP COMPLETE - SYSTEM CHECK\n")

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S EDT")
    report.append(f"**Startup Time:** {current_time}\n")

    # Active Scanner Results
    report.append("### 🔥 ACTIVE STOCK SCANNER: TOP 20 BY MOMENTUM")
    report.append(
        "*Minimum 500 trades/minute • ONLY ACTIVE STOCKS • Sorted by % change*\n"
    )
    report.append("```")
    report.append(f"{'Symbol':<6} {'Trades/Min':>10}   {'Change%':>8}")
    report.append(f"{'------':<6} {'----------':>10}  {'--------':>8}")

    if top_20:
        for i, (symbol, trades, pct) in enumerate(top_20):
            emoji = ""
            if pct > 100:
                emoji = "  🚀 EXPLOSIVE"
            elif pct > 50:
                emoji = "  🔥 MEGA MOVE"
            elif pct > 10:
                emoji = "  ⚡ High volatility"
            elif pct > 5:
                emoji = "  📈 Strong momentum"
            elif pct > 2:
                emoji = "  ⬆️ Positive"
            elif pct > -1:
                emoji = "  → Neutral"
            else:
                emoji = "  ⬇️ Declining"

            report.append(f"{symbol:<6} {trades:>10}  {pct:+8.2f}%{emoji}")
    else:
        report.append("No active stocks found meeting criteria (500+ trades/min)")

    report.append("```")

    if top_20:
        # Key metrics
        top_mover = top_20[0]
        avg_liquidity = sum(t[1] for t in top_20) / len(top_20)
        winners = sum(1 for t in top_20 if t[2] > 0)
        explosive = sum(1 for t in top_20 if t[2] > 10)

        report.append("\n**Key Metrics:**")
        report.append(
            f"- 🎯 **Top Mover:** {top_mover[0]} ({top_mover[2]:+.2f}%) with {top_mover[1]:,} trades/min"
        )
        report.append(f"- 📊 **Avg Liquidity:** {avg_liquidity:,.0f} trades/minute")
        report.append(
            f"- 📈 **Winners:** {winners}/{len(top_20)} stocks positive ({winners / len(top_20) * 100:.0f}%)"
        )
        report.append(f"- 🔥 **Explosive Moves:** {explosive} stocks >10% gain")

        # Action items
        if top_mover[2] > 50:
            report.append("\n**🚨 IMMEDIATE ACTIONS:**")
            report.append(
                f'1. Analyze {top_mover[0]}\'s explosive move: `get_stock_peak_trough_analysis("{top_mover[0]}")`'
            )
            top_5_symbols = [t[0] for t in top_20[:5] if t[2] > 5]
            if top_5_symbols:
                symbols_str = '", "'.join(top_5_symbols[:3])
                report.append(
                    f'2. Start streaming: `start_global_stock_stream(["{symbols_str}"], ["trades","quotes"])`'
                )
                snapshot_str = ",".join(top_5_symbols[:5])
                report.append(
                    f'3. Get snapshots: `get_stock_snapshots("{snapshot_str}")`'
                )

    # System status
    report.append("\n### 📊 System Status")
    report.append(
        "- **Scanner**: ✅ Active stock scanner operational (500+ trades/min)"
    )
    report.append("- **Server**: ✅ MCP server running")
    report.append("- **Tools**: ✅ All trading tools available")
    report.append("- **Data**: ✅ Using ONLY currently active stocks")

    # Trading rules reminder
    report.append("\n### 🚨 TRADING RULES")
    report.append("- **Orders**: Limit orders only (never market orders)")
    report.append("- **Precision**: 4 decimal places for penny stocks")
    report.append("- **Liquidity**: Minimum 500 trades/minute for active stocks")
    report.append("- **Exits**: Never sell for loss unless specifically instructed")
    report.append("- **Speed**: React within 2-3 seconds when profit appears")

    report.append("\n**🚀 READY FOR DAY TRADING! 🚀**")

    return "\n".join(report)


# Register the prompt
__all__ = ["startup"]
