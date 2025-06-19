"""Day Trading Opportunity Scanner - Uses updated MCP scanner with professional formatting."""

from datetime import datetime
from typing import Optional
import pytz


async def scan(
    trades_threshold: Optional[int] = 500,
    limit: Optional[int] = 20,
    filename: Optional[str] = "combined.lis",
) -> str:
    """
    Execute EXPLOSIVE UP-ONLY day trading opportunity scan with extreme volatility focus.

    Uses the updated MCP scanner that filters for ONLY UP STOCKS with minimum +10% gains.
    NO BORING STOCKS - Only extreme volatility explosive movers.

    Args:
        trades_threshold: Minimum trades/minute threshold for extreme liquidity (default: 500)
        limit: Maximum number of explosive opportunities to analyze (default: 20)
        filename: Not used - scans ALL tradeable assets for explosive moves

    Returns:
        Formatted analysis with EXPLOSIVE UP-ONLY trading opportunities
    """

    # Robust input validation and conversion
    try:
        if trades_threshold is None:
            trades_threshold = 500
        elif isinstance(trades_threshold, str):
            trades_threshold = (
                int(trades_threshold) if trades_threshold.isdigit() else 500
            )
        trades_threshold = int(trades_threshold)
    except (ValueError, TypeError):
        trades_threshold = 500

    try:
        if limit is None:
            limit = 20
        elif isinstance(limit, str):
            limit = int(limit) if limit.isdigit() else 20
        limit = int(limit)
    except (ValueError, TypeError):
        limit = 20

    try:
        # Use the updated MCP scanner that scans all symbols from combined.lis
        from ..tools.day_trading_scanner import scan_day_trading_opportunities

        # Call the updated scanner with EXPLOSIVE UP-ONLY parameters
        result = await scan_day_trading_opportunities(
            symbols="ALL",  # Scan all tradeable assets for explosive moves
            min_trades_per_minute=trades_threshold,
            min_percent_change=10.0,  # EXPLOSIVE moves only - minimum +10%
            max_symbols=limit,
            sort_by="trades",
        )

        return result

    except Exception as e:
        # Fallback to error message
        edt = pytz.timezone("America/New_York")
        scan_time = datetime.now(edt).strftime("%Y-%m-%d %H:%M:%S EDT")

        return f"""
❌ **SCAN ERROR**
Time: {scan_time}
Error: {str(e)}

• Check MCP scanner is functioning
• Verify API connectivity
• Ensure all required files are present
"""


# Export the function
__all__ = ["scan"]
