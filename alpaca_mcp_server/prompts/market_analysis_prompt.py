"""Market analysis prompt implementation."""

from typing import Optional, List
from datetime import datetime
from ..tools.enhanced_market_clock import get_extended_market_clock
from ..tools.market_data_tools import get_stock_snapshots
from ..resources.market_resources import get_market_conditions


async def market_analysis(
    symbols: Optional[List[str]] = None,
    timeframe: str = "1Day",
    analysis_type: str = "comprehensive",
) -> str:
    """Real-time market analysis with trading opportunities and risk assessment."""

    try:
        # Get current market session status
        market_clock = await get_extended_market_clock()
        market_conditions = await get_market_conditions()

        # Default symbols if none provided
        if symbols is None:
            symbols = ["SPY", "QQQ", "IWM", "AAPL", "MSFT", "NVDA"]

        # Get market snapshots for analysis
        snapshots = await get_stock_snapshots(
            ",".join(symbols[:4])
        )  # Limit to avoid too much data

        # Generate market analysis based on session
        session_status = "UNKNOWN"
        session_emoji = "❓"
        trading_notes = ""

        # Parse market clock response to determine session
        if "Pre-market trading active" in market_clock:
            session_status = "PRE-MARKET"
            session_emoji = "🌅"
            trading_notes = """
**Pre-Market Trading Active (4:00 AM - 9:30 AM ET):**
• Higher volatility and wider spreads expected
• Lower liquidity - use limit orders only
• Good for earnings/news reactions
• Extended hours trading available (set extended_hours=True)"""
        elif "Regular market session" in market_clock or market_conditions.get(
            "is_open", False
        ):
            session_status = "REGULAR HOURS"
            session_emoji = "🔔"
            trading_notes = """
**Regular Market Hours (9:30 AM - 4:00 PM ET):**
• Full liquidity and normal spreads
• All order types available
• Peak trading volume and activity
• Optimal conditions for day trading"""
        elif "After-hours trading active" in market_clock:
            session_status = "AFTER-HOURS"
            session_emoji = "🌙"
            trading_notes = """
**After-Hours Trading (4:00 PM - 8:00 PM ET):**
• Reduced liquidity and wider spreads
• Limit orders strongly recommended
• Lower volume, higher volatility
• Extended hours trading available (set extended_hours=True)"""
        else:
            session_status = "MARKET CLOSED"
            session_emoji = "🔕"
            trading_notes = """
**Market Closed (8:00 PM - 4:00 AM ET):**
• No trading activity
• Pre-market opens at 4:00 AM ET
• Time for analysis and planning
• Review positions and prepare watchlists"""

        result = f"""# {session_emoji} Market Analysis Report - {session_status}
        
## 📊 Market Overview
**Analysis Time:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S ET")}
**Market Session:** {session_status}
**Timeframe:** {timeframe}
**Analysis Type:** {analysis_type}
**Symbols:** {", ".join(symbols)}

{trading_notes}

## 📈 Market Data Analysis
"""

        # Add market snapshot data
        result += f"""
{snapshots}

## 🎯 Trading Opportunities & Session Strategy

### Session-Specific Considerations:
"""

        if session_status == "PRE-MARKET":
            result += """
**Pre-Market Focus:**
• Watch for gap-up/gap-down opportunities from overnight news
• Monitor earnings reactions and news-driven moves
• Use peak/trough analysis: `get_stock_peak_trough_analysis(symbols, "1Min")`
• Set up streaming for market open: `start_global_stock_stream(symbols, ["trades", "quotes"])`
• Extended hours orders: `place_extended_hours_order(symbol, side, qty, "limit", limit_price)`
"""
        elif session_status == "REGULAR HOURS":
            result += """
**Regular Hours Focus:**
• Full liquidity available for day trading strategies
• Use technical analysis tools for entry/exit timing
• Monitor real-time data: `get_stock_stream_data(symbol, "trades", recent_seconds=60)`
• Peak/trough signals: `get_stock_peak_trough_analysis(symbols, "1Min")`
• All order types available including market orders (though limit preferred)
"""
        elif session_status == "AFTER-HOURS":
            result += """
**After-Hours Focus:**
• Limited liquidity - stick to highly liquid stocks
• News-driven opportunities from earnings/announcements
• Extended hours trading: `place_extended_hours_order(symbol, side, qty, "limit", limit_price)`
• Monitor for next day gap setups
"""
        else:
            result += """
**Market Closed - Planning Phase:**
• Review positions and prepare for next session
• Analyze daily charts and plan entries
• Set up watchlists: `create_watchlist("Daily_Targets", [symbols])`
• Review account performance: `account_analysis()`
"""

        result += f"""

## 📊 Technical Analysis Recommendations

### Immediate Actions:
1. **Market Momentum Check:** `resource_market_momentum()`
2. **Account Status:** `resource_account_status()`
3. **Position Review:** `get_positions()`

### Advanced Analysis:
• **Peak/Trough Signals:** `get_stock_peak_trough_analysis("{",".join(symbols[:3])}", timeframe="1Min")`
• **Intraday Patterns:** `get_stock_bars_intraday("SPY", "5Min", limit=100)`
• **Real-time Monitoring:** `get_stock_stream_data("SPY", "trades", recent_seconds=120)`

## ⚠️ Risk Management

### Session-Specific Risks:
"""

        if session_status in ["PRE-MARKET", "AFTER-HOURS"]:
            result += """
• **Higher Volatility:** Expect larger price swings
• **Wider Spreads:** Factor in increased transaction costs
• **Lower Liquidity:** Use smaller position sizes
• **Gap Risk:** Positions may gap significantly at market open/close
"""
        else:
            result += """
• **Standard Risk Management:** Normal market conditions
• **Monitor Position Sizing:** Keep risk per trade under 2%
• **Use Stop Losses:** Implement via conditional orders
• **Diversification:** Avoid concentration in single sector/stock
"""

        result += f"""

## 🚀 Next Steps

### For Current Session ({session_status}):
1. **Setup:** Account check and position review
2. **Analysis:** Use peak/trough analysis for entry signals  
3. **Execution:** Place limit orders with proper risk management
4. **Monitoring:** Stream real-time data for active positions

### Trading Lesson Integration:
• **"SCAN LONGER before entry"** → Use `get_stock_peak_trough_analysis()` 
• **"Use limit orders exclusively"** → Avoid market orders
• **"React within 2-3 seconds"** → Have streaming data ready
• **"Monitor every 1-3 seconds"** → Use `get_stock_stream_data()`

### Quick Commands:
```
# Market check
get_extended_market_clock()

# Multi-stock analysis  
get_stock_snapshots("CGTL,HCTI,KLTO")

# Peak/trough signals
get_stock_peak_trough_analysis("CGTL", timeframe="1Min")

# Start streaming
start_global_stock_stream(["CGTL"], ["trades", "quotes"])
```
"""

        return result

    except Exception as e:
        return f"""Error in market analysis: {str(e)}

Troubleshooting:
• Check market connectivity
• Verify symbols are valid
• Try get_stock_snapshots(['SPY', 'QQQ']) for basic data
"""
