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
    Execute comprehensive day trading opportunity scan using MCP scanner with enhanced analysis.

    Uses the updated MCP scanner that scans all symbols from combined.lis with professional formatting.

    Args:
        trades_threshold: Minimum trades/minute threshold for liquidity (default: 500)
        limit: Maximum number of opportunities to analyze (default: 20)
        filename: Stock symbols list filename (default: "combined.lis")

    Returns:
        Formatted analysis with ranked trading opportunities and market context
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

        # Call the updated scanner with proper parameters
        result = await scan_day_trading_opportunities(
            symbols="ALL",  # Scan all symbols from combined.lis
            min_trades_per_minute=trades_threshold,
            min_percent_change=1.0,  # Lower threshold to find more opportunities
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
