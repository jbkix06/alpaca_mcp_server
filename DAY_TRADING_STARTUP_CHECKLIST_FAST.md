# Day Trading Startup: Parallel Execution Command

**COMMAND:** `/startup` - Executes all day trading startup checks in parallel for maximum speed

## 🎯 ALPACA MCP SERVER PURPOSE

This Model Context Protocol (MCP) server provides LLMs with direct access to Alpaca's trading APIs for:

### Supported Trading Types:
- **DAY TRADING** - Intraday positions closed before market close
- **SWING TRADING** - Multi-day positions (with PDT considerations)
- **OPTIONS TRADING** - Single and multi-leg strategies
- **EXTENDED HOURS** - Pre-market (4-9:30 AM) and after-hours (4-8 PM)
- **PAPER TRADING** - Risk-free practice environment (default mode)

### Primary Focus: High-Volatility Day Trading
- **TARGET:** Explosive penny stocks and momentum plays (+20% to +500% moves)
- **RANGE:** $0.01 to $10.00 stocks with extreme volatility
- **LIQUIDITY:** Minimum 500-1000 trades/minute requirement
- **EXECUTION:** Limit orders for precision, streaming data for speed

## ⚖️ REGULATORY COMPLIANCE & RULES

### Pattern Day Trader (PDT) Rule:
- **$25,000 minimum** equity required for unlimited day trades
- **Day trade:** Buy and sell same security on same day
- **Restriction:** 3 day trades per 5 business days if under $25k
- **This account:** PDT enabled with unlimited day trades

### Trading Regulations:
- **Reg T:** 2-day settlement for cash accounts
- **Good Faith Violations:** Don't sell before settlement
- **Wash Sale Rule:** No loss deduction if repurchased within 30 days
- **Market Manipulation:** No artificial price movements

### Risk Disclosures:
⚠️ **Day trading involves substantial risk of loss**
⚠️ **Most day traders lose money**
⚠️ **Only trade with capital you can afford to lose**
⚠️ **Paper trading recommended for practice**

## 🚨 CORE DAY TRADING RULES (NON-NEGOTIABLE)

### Order Management Rules:
- ❌ **NEVER use market orders** (unless specifically instructed)
- ❌ **NEVER sell for a loss** (unless specifically instructed)  
- ✅ **ALWAYS use limit orders** for precise execution
- ✅ **Use 4 decimal places** for penny stocks ($0.0118 format)
- ✅ **Minimum 1,000 trades/minute** for liquidity requirements

### Speed Requirements:
- ⚡ **React within 2-3 seconds** when profit appears
- ⚡ **Monitor streaming data** every 1-3 seconds during active trades
- ⚡ **Check order fills immediately** after placement
- ⚡ **Document entry price** immediately after fill verification

### Post-Order Fill Procedure (MANDATORY):
After ANY order fills:
1. `get_orders(status="all", limit=5)` - **Verify actual fill price**
2. `get_positions()` - **Confirm position and entry price**  
3. **Write down and verify fill price** - never rely on memory
4. Start appropriate monitoring (streaming for profits, quotes for losses)

---

## 🏁 STARTUP EXECUTION: ALL CHECKS IN PARALLEL

When `/startup` is executed, Claude will automatically run all these tools concurrently for maximum speed:

**PARALLEL BATCH 1: Core System Health (4 tools)**
- `health_check()` - Overall system health
- `resource_server_health()` - Server performance metrics  
- `resource_api_status()` - API connectivity status
- `resource_session_status()` - Current session details

**PARALLEL BATCH 2: Market Status (4 tools)**
- `get_market_clock()` - Basic market status
- `get_extended_market_clock()` - Pre/post market details
- `resource_market_conditions()` - Overall market sentiment
- `resource_market_momentum()` - Market direction analysis

**PARALLEL BATCH 3: Account & Positions (6 tools)**
- `get_account_info()` - Buying power and restrictions
- `resource_account_status()` - Real-time account health
- `get_positions()` - Check for any open positions
- `resource_current_positions()` - Live P&L tracking
- `get_orders(status="open")` - Check for stale orders
- `resource_intraday_pnl()` - Today's performance tracking

**PARALLEL BATCH 4: Data Quality & Streaming (5 tools)**
- `resource_data_quality()` - Feed latency and quality
- `get_stock_stream_buffer_stats()` - Streaming infrastructure
- `list_active_stock_streams()` - Check existing streams
- `get_stock_quote("SPY")` - Test streaming latency
- `clear_stock_stream_buffers()` - Clear old streaming data

**PARALLEL BATCH 5: Trading Tools & Scanners (6 tools)**
- `get_stock_snapshots("SPY,QQQ")` - Market snapshot tool
- `scan_day_trading_opportunities()` - Active stock scanner
- `scan_explosive_momentum()` - High-volatility scanner
- `validate_extended_hours_order("SPY", "limit")` - Order validation
- `get_stock_peak_trough_analysis("SPY")` - Entry/exit signals
- High-liquidity scanner: `./trades_per_minute.sh -f combined.lis -t 500`

**CLAUDE EXECUTION INSTRUCTIONS:**
When user runs `/startup`, Claude MUST:
1. **Start server:** `python run_alpaca_mcp.py` 
2. **Execute ALL tools in a SINGLE parallel call** - Use one message with multiple tool invocations
3. **Generate comprehensive status report** with all results
4. **Identify top trading opportunities** from scanners
5. **Confirm all systems green for trading**

**CRITICAL:** NEVER execute tools sequentially - ALWAYS use parallel execution for maximum speed.

---

## ✅ READY TO TRADE VERIFICATION

### All Systems Green Checklist:
- [ ] ✅ Server health: All systems operational
- [ ] ✅ Market status: Trading session confirmed
- [ ] ✅ Account verified: Adequate buying power, no restrictions
- [ ] ✅ Data feeds: Low latency, high quality streaming
- [ ] ✅ Tools tested: Scanners and analysis tools responsive
- [ ] ✅ No stale positions/orders: Clean starting state
- [ ] ✅ Risk rules reviewed: Position sizing and stop procedures
- [ ] ✅ Regulatory compliance: PDT status confirmed

### Day Trading Flow Ready:
1. **Scanner** → Find opportunities with `scan_day_trading_opportunities()`
2. **Analysis** → Use `get_stock_peak_trough_analysis()` for entry signals  
3. **Streaming** → Start `start_global_stock_stream()` for real-time monitoring
4. **Execute** → Place limit orders with `place_stock_order()`
5. **Monitor** → Check fills and track with streaming data
6. **Exit** → Take profits aggressively, never sell for loss

---

## 🚨 EMERGENCY PROCEDURES

**Market Orders Emergency:**
- Only use if specifically instructed
- Speed over price when explicitly told to exit

**Stop All Trading:**
- `cancel_all_orders()` - Cancel all pending orders
- `close_all_positions()` - Emergency position exit
- `stop_global_stock_stream()` - Stop streaming data

**Declining Peaks Emergency:**
- If trapped in falling stock, use averaging down strategy
- Documented in DECLINING_PEAKS_STRATEGY.md
- Max 3x position size, 5¢ profit target

---

## 📋 TRADING BEST PRACTICES

### Entry Strategy:
- Wait for clear peak/trough signals
- Enter on support bounces, not resistance breaks
- Size positions based on liquidity (trades/minute)
- Always use limit orders at or below ask

### Exit Strategy:
- Take profits aggressively (2-5% for volatile stocks)
- Use trailing mental stops, not stop-loss orders
- Exit on declining peaks pattern
- Never turn a profit into a loss

### Risk Management:
- Position size: Max 10% of buying power per trade
- Daily loss limit: 2% of account value
- Win target: 3-5 profitable trades per day
- Time limit: 45 minutes max per position

---

**🚀 ONLY BEGIN DAY TRADING WHEN ALL ITEMS ARE CHECKED ✅**

**Remember: Speed beats perfection. Take profits aggressively. Never sell for loss.**

Use `/startup` to access this checklist before every trading session.