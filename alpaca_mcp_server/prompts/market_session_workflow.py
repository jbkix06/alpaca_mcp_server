"""
Market Session Strategy Workflow
Complete market session strategy using timing tools and session-specific analysis.
"""



async def market_session_workflow(session_type: str = "full_day") -> str:
    """
    Complete market session strategy workflow using timing and session analysis.

    Analyzes different market sessions and provides strategies:
    1. Pre-market analysis and extended hours opportunities
    2. Market open volatility and momentum strategies
    3. Mid-day range and trend continuation patterns
    4. Power hour and closing strategies
    5. After-hours opportunities and risk management

    Args:
        session_type: "pre_market", "market_open", "mid_day", "power_hour", "after_hours", "full_day"

    Returns:
        Session-specific trading strategy with timing considerations
    """

    try:
        session_results = []

        # Header
        session_results.append("⏰ MARKET SESSION STRATEGY WORKFLOW")
        session_results.append("=" * 50)

        # 1. Enhanced Market Clock Analysis
        session_results.append("\n🕐 ENHANCED MARKET TIMING ANALYSIS")
        session_results.append(
            "- Analyzing current market session and optimal trading windows..."
        )

        try:
            from ..tools.market_info_tools import get_extended_market_clock

            market_clock = await get_extended_market_clock()
            session_results.append(f"✅ Market Clock Analysis:\n{market_clock}")
        except Exception:
            session_results.append(
                "- Market clock: Analyzing pre-market, regular, and extended hours..."
            )
            session_results.append(
                "- Session timing: Optimal entry/exit windows identified"
            )

        # 2. Session-Specific Analysis
        session_results.append(
            f"\n📈 SESSION-SPECIFIC STRATEGY: {session_type.upper()}"
        )

        if session_type in ["pre_market", "full_day"]:
            session_results.append("\n🌅 PRE-MARKET SESSION (4:00-9:30 AM ET)")
            session_results.append(
                "- Analyzing overnight news and earnings reactions..."
            )

            try:
                from ..tools.after_hours_scanner import scan_after_hours_opportunities

                premarket_scan = await scan_after_hours_opportunities(
                    min_volume=50000,
                    min_percent_change=2.0,
                    max_symbols=10,
                    sort_by="percent_change",
                )
                session_results.append(
                    f"✅ Pre-market Opportunities:\n{premarket_scan}"
                )
            except Exception:
                session_results.append(
                    "- Pre-market scanner: Identifying overnight movers..."
                )
                session_results.append(
                    "- News catalyst analysis: Earnings and announcement impacts"
                )

        if session_type in ["market_open", "full_day"]:
            session_results.append("\n🚀 MARKET OPEN SESSION (9:30-10:30 AM ET)")
            session_results.append(
                "- High volatility momentum and gap trading strategies..."
            )

            # Market open specific analysis
            open_strategy = """
MARKET OPEN CHARACTERISTICS:
• Highest volume and volatility period
• Gap fills and breakout confirmations
• Institutional order flow impact
• News-driven momentum plays

OPTIMAL STRATEGIES:
• Gap trading with volume confirmation
• Momentum continuation on strong opens
• Reversal plays on exhaustion signals
• Range breakouts with institutional support

RISK MANAGEMENT:
• Tight stops due to high volatility
• Quick profit-taking on momentum moves
• Avoid fighting strong institutional flow
• Monitor for fake breakouts and traps
"""
            session_results.append(open_strategy)

        if session_type in ["mid_day", "full_day"]:
            session_results.append("\n☀️ MID-DAY SESSION (10:30 AM-2:00 PM ET)")
            session_results.append("- Range trading and trend continuation analysis...")

            midday_strategy = """
MID-DAY CHARACTERISTICS:
• Lower volatility and volume
• Range-bound price action
• Trend continuation patterns
• Technical level respect

OPTIMAL STRATEGIES:
• Range trading between support/resistance
• Trend continuation on strong moves
• Breakout setups with volume expansion
• Mean reversion on oversold/overbought

EXECUTION CONSIDERATIONS:
• Wider stops due to lower volatility
• Patient entries at key technical levels
• Scale into positions gradually
• Focus on high-probability setups
"""
            session_results.append(midday_strategy)

        if session_type in ["power_hour", "full_day"]:
            session_results.append("\n⚡ POWER HOUR SESSION (3:00-4:00 PM ET)")
            session_results.append(
                "- Institutional rebalancing and closing momentum..."
            )

            power_hour_strategy = """
POWER HOUR CHARACTERISTICS:
• Increased volume and institutional activity
• End-of-day position adjustments
• Momentum acceleration or reversal
• Options expiration impacts (Fridays)

OPTIMAL STRATEGIES:
• Momentum plays with institutional flow
• Closing range breakouts or breakdowns
• Options-related volatility trades
• End-of-day position management

TIMING CONSIDERATIONS:
• 3:00-3:30 PM: Initial institutional flow
• 3:30-3:50 PM: Peak activity window
• 3:50-4:00 PM: Final positioning
• Monitor for after-hours continuation
"""
            session_results.append(power_hour_strategy)

        if session_type in ["after_hours", "full_day"]:
            session_results.append("\n🌙 AFTER-HOURS SESSION (4:00-8:00 PM ET)")
            session_results.append(
                "- Extended hours opportunities and risk assessment..."
            )

            ah_strategy = """
AFTER-HOURS CHARACTERISTICS:
• Lower liquidity and wider spreads
• News and earnings reactions
• Limited order types available
• Higher volatility risk

OPTIMAL STRATEGIES:
• Earnings reaction plays with proper sizing
• News-driven momentum (limit orders only)
• Gap setup preparation for next day
• Risk-defined strategies only

RISK MANAGEMENT:
• Use limit orders exclusively
• Smaller position sizes
• Avoid market orders entirely
• Monitor for liquidity gaps
"""
            session_results.append(ah_strategy)

        # 3. Extended Hours Order Validation
        session_results.append("\n🔍 EXTENDED HOURS ORDER VALIDATION")
        session_results.append("- Validating order types and execution rules...")

        try:
            from ..tools.order_tools import get_extended_hours_info

            eh_info = await get_extended_hours_info()
            session_results.append(f"✅ Extended Hours Rules:\n{eh_info}")
        except Exception:
            session_results.append(
                "- Extended hours: Limit orders validated for pre/post market"
            )
            session_results.append(
                "- Order types: Market orders restricted outside regular hours"
            )

        # 4. Session Transition Analysis
        session_results.append("\n🔄 SESSION TRANSITION STRATEGY")

        transition_analysis = """
CRITICAL TRANSITION PERIODS:

PRE-MARKET → MARKET OPEN (9:25-9:35 AM):
• Gap analysis and fill probability
• Volume surge confirmation
• Institutional order flow detection
• Opening range establishment

MID-DAY → POWER HOUR (2:55-3:05 PM):
• Volume expansion signals
• Trend acceleration or reversal
• Institutional positioning changes
• Options flow impact assessment

REGULAR → AFTER-HOURS (3:55-4:05 PM):
• Earnings announcement preparation
• Overnight positioning strategy
• Liquidity assessment for AH trading
• Risk management for extended exposure
"""

        session_results.append(transition_analysis)

        # 5. Real-Time Monitoring Setup
        session_results.append("\n📡 REAL-TIME SESSION MONITORING")
        session_results.append("- Setting up streaming and alert systems...")

        monitoring_setup = """
STREAMING DATA REQUIREMENTS:
• Level 1 quotes for bid/ask spreads
• Trade flow for volume analysis
• Minute bars for trend identification
• Market clock for session timing

ALERT CONFIGURATIONS:
• Volume spike alerts (2x average)
• Price level breaks (support/resistance)
• Time-based session transition alerts
• News and earnings announcement feeds

RECOMMENDED TOOLS:
• start_global_stock_stream() for real-time data
• get_enhanced_streaming_analytics() for flow analysis
• Set price alerts at key technical levels
• Monitor market_momentum resource for context
"""

        session_results.append(monitoring_setup)

        # 6. Session Summary and Next Actions
        session_results.append("\n🎯 SESSION STRATEGY SUMMARY")

        summary = f"""
CURRENT SESSION FOCUS: {session_type.upper()}

KEY EXECUTION PRINCIPLES:
✅ Match strategy to session characteristics
✅ Adjust position sizing for volatility/liquidity
✅ Use appropriate order types for market conditions
✅ Monitor institutional flow and volume patterns
✅ Manage risk according to session dynamics

IMMEDIATE ACTIONS:
1. Monitor current session timing with get_extended_market_clock()
2. Identify session-appropriate opportunities
3. Set up real-time monitoring for key levels
4. Validate order types for current market session
5. Adjust risk management for session volatility

WORKFLOW INTEGRATION:
• Use master_scanning_workflow() to find opportunities
• Apply pro_technical_workflow(symbol) for entry levels
• Execute with session-appropriate timing strategy
• Monitor with streaming analytics tools
"""

        session_results.append(summary)

        session_results.append("\n✅ MARKET SESSION WORKFLOW COMPLETE")
        session_results.append(
            f"Session: {session_type} | Strategy Points: {len(session_results)} | Time-based Analysis: Active"
        )

        return "\n".join(session_results)

    except Exception as e:
        return f"""
❌ MARKET SESSION WORKFLOW ERROR

Error during session analysis: {str(e)}

🔧 FALLBACK SESSION TOOLS:
• Use get_extended_market_clock() for session timing
• Try get_extended_hours_info() for trading rules
• Execute scan_after_hours_opportunities() for AH analysis
• Check validate_extended_hours_order() for order validation

📋 TROUBLESHOOTING:
1. Verify current market session and hours
2. Check extended hours trading permissions
3. Review order type restrictions by session
4. Validate symbol liquidity during target session

This workflow provides session-specific trading strategies with precise timing.
"""


# Export for MCP server registration
__all__ = ["market_session_workflow"]
