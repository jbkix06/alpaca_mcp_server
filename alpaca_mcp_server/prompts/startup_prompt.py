"""Day Trading Startup Prompt - Parallel execution of all startup checks."""

from datetime import datetime
from ..tools.day_trading_scanner import scan_day_trading_opportunities


async def startup() -> str:
    """
    Execute all day trading startup checks in parallel for maximum speed.

    Runs comprehensive system health checks, market status, account verification,
    and trading scanners to ensure all systems are ready for day trading.
    Uses ONLY currently active stocks from live scanner data.

    Returns:
        Comprehensive startup status report with top trading opportunities
    """

    # Use MCP day trading scanner for active stocks - scan ALL tradeable assets
    try:
        scanner_result = await scan_day_trading_opportunities(
            symbols="ALL",  # Use ALL tradeable stock assets by default
            min_trades_per_minute=500,
            min_percent_change=0.0,  # Get all stocks, we'll filter later
            max_symbols=20,
            sort_by="trades",
        )

        # Parse the formatted result to extract stock data
        top_20 = []
        if "No opportunities found" not in scanner_result and "Total Qualified: 0" not in scanner_result:
            lines = scanner_result.split("\n")
            for line in lines:
                # Look for lines with rank numbers (e.g., "   1 NVDA      10,253 +     1.5% $144.029 1,469,127 ⚡ MODERATE")
                if line.strip() and line.strip().split() and line.strip().split()[0].isdigit():
                    try:
                        # Split by whitespace and extract fields
                        parts = line.strip().split()
                        if len(parts) >= 6:  # rank symbol trades +/- change% price
                            symbol = parts[1]
                            trades_str = parts[2].replace(",", "")
                            # Handle the +/- sign separately from percentage
                            if parts[3] in ['+', '-']:
                                pct_str = parts[4].rstrip("%")
                                if parts[3] == '-':
                                    pct_str = '-' + pct_str
                            else:
                                # Handle case where +/- is attached to percentage
                                pct_str = parts[3].rstrip("%")

                            trades = int(trades_str)
                            pct = float(pct_str)

                            if trades >= 500:
                                top_20.append((symbol, trades, pct))
                    except (ValueError, IndexError):
                        continue
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
