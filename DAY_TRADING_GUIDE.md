# COMPREHENSIVE DAY TRADING GUIDE

## Table of Contents
1. [Core Trading Rules & Safety](#core-trading-rules--safety)
2. [Startup Procedures](#startup-procedures)
3. [Trading Strategies](#trading-strategies)
4. [Real Trading Lessons](#real-trading-lessons)
5. [Emergency Procedures](#emergency-procedures)
6. [Performance Tracking](#performance-tracking)

---

## Core Trading Rules & Safety

### 🚨 NON-NEGOTIABLE TRADING RULES

#### Order Management Rules
- ❌ **NEVER use market orders** (unless specifically instructed)
- ❌ **NEVER sell for a loss** (unless specifically instructed)  
- ✅ **ALWAYS use limit orders** for precise execution
- ✅ **Use 4 decimal places** for penny stocks ($0.0118 format)
- ✅ **Minimum 1,000 trades/minute** for liquidity requirements

#### Speed Requirements
- ⚡ **React within 2-3 seconds** when profit appears
- ⚡ **Monitor streaming data** every 1-3 seconds during active trades
- ⚡ **Check order fills immediately** after placement
- ⚡ **Document entry price** immediately after fill verification

#### Post-Order Fill Procedure (MANDATORY)
After ANY order fills:
1. `get_orders(status="all", limit=5)` - **Verify actual fill price**
2. `get_positions()` - **Confirm position and entry price**  
3. **Write down and verify fill price** - never rely on memory
4. Start appropriate monitoring (streaming for profits, quotes for losses)

### 🎯 TRADING FOCUS

**Target:** Explosive penny stocks and momentum plays (+20% to +500% moves)
**Range:** $0.01 to $10.00 stocks with extreme volatility
**Liquidity:** Minimum 500-1000 trades/minute requirement
**Execution:** Limit orders for precision, streaming data for speed

### ⚖️ REGULATORY COMPLIANCE

#### Pattern Day Trader (PDT) Rule
- **$25,000 minimum** equity required for unlimited day trades
- **Day trade:** Buy and sell same security on same day
- **Restriction:** 3 day trades per 5 business days if under $25k
- **This account:** PDT enabled with unlimited day trades

#### Risk Disclosures
⚠️ **Day trading involves substantial risk of loss**
⚠️ **Most day traders lose money**
⚠️ **Only trade with capital you can afford to lose**
⚠️ **Paper trading recommended for practice**

---

## Startup Procedures

### 🚀 PARALLEL STARTUP EXECUTION

**COMMAND:** `/startup` - Executes all day trading startup checks in parallel for maximum speed

#### PARALLEL BATCH 1: Core System Health (4 tools)
- `health_check()` - Overall system health
- `resource_server_health()` - Server performance metrics  
- `resource_api_status()` - API connectivity status
- `resource_session_status()` - Current session details

#### PARALLEL BATCH 2: Market Status (4 tools)
- `get_market_clock()` - Basic market status
- `get_extended_market_clock()` - Pre/post market details
- `resource_market_conditions()` - Overall market sentiment
- `resource_market_momentum()` - Market direction analysis

#### PARALLEL BATCH 3: Account & Positions (6 tools)
- `get_account_info()` - Buying power and restrictions
- `resource_account_status()` - Real-time account health
- `get_positions()` - Check for any open positions
- `resource_current_positions()` - Live P&L tracking
- `get_orders(status="open")` - Check for stale orders
- `resource_intraday_pnl()` - Today's performance tracking

#### PARALLEL BATCH 4: Data Quality & Streaming (5 tools)
- `resource_data_quality()` - Feed latency and quality
- `get_stock_stream_buffer_stats()` - Streaming infrastructure
- `list_active_stock_streams()` - Check existing streams
- `get_stock_quote("SPY")` - Test streaming latency
- `clear_stock_stream_buffers()` - Clear old streaming data

#### PARALLEL BATCH 5: Trading Tools & Scanners (6 tools)
- `get_stock_snapshots("SPY,QQQ")` - Market snapshot tool
- `scan_day_trading_opportunities()` - Active stock scanner
- `scan_explosive_momentum()` - High-volatility scanner
- `validate_extended_hours_order("SPY", "limit")` - Order validation
- `get_stock_peak_trough_analysis("SPY")` - Entry/exit signals
- **High-liquidity scanner:** `./trades_per_minute.sh -f combined.lis -t 500`

### 🔍 HIGH-LIQUIDITY STOCK SCANNER (CRITICAL)

**ALWAYS use trades_per_minute.sh script instead of MCP scanner functions:**

```bash
./trades_per_minute.sh -f combined.lis -t 500
```

**Analysis procedure:**
- Scan all 10,112 stocks in combined.lis
- Identify stocks with 1000+ trades/minute (Tier 1 targets)
- Identify stocks with 500-999 trades/minute (Tier 2 targets)
- **REJECT any stocks below 500 trades/minute** (insufficient liquidity)
- Prioritize explosive momentum stocks (>20% change) with adequate liquidity

**Example output analysis:**
```
Symbol  Trades/Min  Change%
------   ---------  -------
TSLA          6436    3.13%  ← TIER 1: Ultra-high liquidity
RBNE          2284   380.9%  ← TIER 1: Explosive momentum  
HOVR          1105   36.48%  ← TIER 1: High momentum
ORCL           994    7.46%  ← TIER 2: Just below 1000
```

### ⚡ 8 AM EDT ALGORITHMIC TRADING FRENZY

**CRITICAL MARKET PHENOMENON:** Every trading day at exactly 8:00 AM EDT, massive algorithmic/institutional trading activity creates extreme volatility.

**What Happens:**
- **Tens of thousands of trades** execute within minutes (40K+ trades common)
- **Extreme price swings** - stocks can move 50-200% in minutes
- **Massive volume spikes** - 10x-50x normal pre-market volume

**Trading Strategy During 8 AM Frenzy:**
- **DO NOT TRADE** during 8:00-8:10 AM EDT period
- **Algorithms control the market** - human traders get crushed
- **Wait for 8:15 AM** when algorithmic activity subsides
- **Use 8 AM data** to identify which stocks institutions are targeting

---

## Trading Strategies

### 🎯 LIGHTNING-FAST PROFIT TAKING (PRIMARY STRATEGY)

**PRIORITY #1: PREVENT DECLINING PEAKS SCENARIOS**

```python
def aggressive_profit_monitoring():
    """Execute IMMEDIATELY on ANY profit opportunity"""
    
    while position_open:
        current_pnl = calculate_unrealized_pnl()
        
        # ANY PROFIT = IMMEDIATE EXIT
        if current_pnl > 0:
            execute_immediate_exit(reason="PROFIT_PRESERVATION")
            break
            
        # Check every 10 seconds when near breakeven
        time.sleep(10)
```

#### Execution Hierarchy
1. **FIRST PROFIT SPIKE → EXIT** (Target: 10-second execution)
2. **SECOND PROFIT SPIKE → EMERGENCY EXIT** (Target: 5-second execution)  
3. **Third opportunity missed → Forced into declining peaks strategy**

### 📈 PEAK/TROUGH ANALYSIS STRATEGY

#### Entry Strategy
- Wait for clear TROUGH signals from `get_stock_peak_trough_analysis()`
- Enter on support bounces, not resistance breaks
- Size positions based on liquidity (trades/minute)
- Always use limit orders at or below ask

#### Exit Strategy (REFINED FROM RBNE LESSONS)
- **Don't exit on first small bounce** - wait for PEAK signal
- Use peak/trough tool for BOTH entry AND exit timing
- Follow signals, not emotions
- Exit patience is as important as entry patience

**INTEGRATED TOOL USAGE:**
1. Peak/trough analysis for signals (60-second cycles)
2. Streaming data for execution timing (when signals appear)
3. **NOT:** Streaming for "checking if profitable"

### 🛑 DECLINING PEAKS EXIT STRATEGY (EMERGENCY ONLY)

⚠️ **WARNING: This is a HIGH-RISK emergency strategy that should be AVOIDED through aggressive profit-taking earlier in the trade.**

#### When to Use
- Stock shows 3+ declining peaks (distribution/liquidation phase)
- Pre-market (4-9:30 AM) or post-market (4-8 PM) preferred
- Existing position needs capital preservation exit
- Institutional selling pressure evident

#### Strategy Execution
```bash
declining_peaks_exit [SYMBOL] [MAX_MULTIPLIER] [PROFIT_CENTS]
```

**Example:** `declining_peaks_exit USEG 3 5` (max 3x position, 5¢ profit target)

#### Critical Rules
- Max 3x position multiplier (not 50x like USEG example)
- Exit immediately when profit target hit (speed critical)
- 30-day blacklist after successful exit (wash sale prevention)
- 5% stop loss below new average cost
- Time limit: 45 minutes maximum

---

## Real Trading Lessons

### 📚 RBNE TRADING SESSION - June 13, 2025

#### Critical Execution Errors & Lessons

1. **FAILED TO TRACK ENTRY PRICE**
   - **Error:** Placed sell limit at $9.98 thinking it was breakeven
   - **Reality:** Actual fill was $9.98, got lucky with $10.00 execution
   - **Lesson:** ALWAYS write down and verify fill price immediately
   - **Solution:** Create position tracker:
     ```
     POSITION TRACKER:
     Symbol: RBNE
     Entry Time: 08:39:39 EDT
     Entry Price: $9.98 (VERIFIED)
     Quantity: 5,000
     Total Cost: $49,900
     Target Exit: Entry + $0.XX
     ```

2. **POSITION SIZE ERROR: 10x Too Small**
   - **Requested:** $50,000
   - **Executed:** $5,000 (~$49,900)
   - **Impact:** Reduced profit potential by 90%
   - **Formula:** Shares = Capital / Price (Round down for safety)

3. **PREMATURE EXIT: Ignored Peak/Trough Analysis**
   - **My Exit:** $10.00 (first tiny bounce)
   - **Optimal Exit:** $12.95+ (based on peak detection)
   - **Money Left:** $14,750 ($2.95 × 5,000 shares)
   - **Lesson:** Use peak/trough tool for BOTH entry AND exit

#### The Patience Paradox
**The Hardest Part:** Being patient when you have a profit
- Natural instinct: "Take it before it disappears!"
- Professional approach: "Follow the signals, not emotions"

**Two-Phase Patience Required:**
1. **Entry Patience:** ✅ Successfully waited for trough signal
2. **Exit Patience:** ❌ Failed - took first profit opportunity

### 📊 USEG STRATEGY SHIFT LESSONS

#### Speed vs. Analysis Balance

**OLD THINKING (USEG Lessons):**
- "ANY profit = exit immediately"
- "Speed over perfection"
- "Don't be greedy"

**REFINED THINKING (RBNE Lessons):**
- "Use tools to maximize profitable exits"
- "Patient entries deserve patient exits"
- "Follow signals, not emotions"
- "Speed on declining peaks, patience on rising trends"

#### Critical Mindset Shifts
❌ **WRONG:** "Let me analyze if this is the perfect exit"  
✅ **CORRECT:** "PROFIT = SELL NOW" (for declining peaks only)

❌ **WRONG:** "Maybe it will go higher"  
✅ **CORRECT:** "Follow peak/trough signals for rising trends"

❌ **WRONG:** "Let me check the signals first"  
✅ **CORRECT:** "Use signals to guide timing, not override them"

### 🎯 KEY SUCCESS FACTORS

#### Execution Speed Rankings
1. **LIGHTNING FAST PROFIT-TAKING** (Prevents declining peaks scenarios)
2. **Follow Peak/Trough Signals** (For optimal entry/exit timing)
3. **Speed Over Perfection** (When emergency exit needed)
4. **Small Profits Compound** ($50 taken > $500 missed)
5. **Exit Discipline** (When tools signal exit, execute immediately)

---

## Emergency Procedures

### 🚨 STOP ALL TRADING
```bash
cancel_all_orders()    # Cancel all pending orders
close_all_positions()  # Emergency position exit
stop_global_stock_stream()  # Stop streaming data
```

### 🛑 DECLINING PEAKS EMERGENCY SEQUENCE

#### Phase 1: Pattern Recognition (60-second cycles)
```python
def detect_declining_peaks_pattern(symbol):
    snapshot = get_stock_snapshots(symbol)
    analysis = get_stock_peak_trough_analysis(symbol, window=5)
    
    # Extract last 3 peaks
    peaks = analysis.get_peaks()[-3:]
    
    if len(peaks) >= 3 and peaks_are_declining(peaks):
        return {"pattern_confirmed": True}
    return {"pattern_confirmed": False}
```

#### Phase 2: Position Building with Limits
```python
def execute_averaging_down(symbol, max_multiplier, current_position):
    # Calculate safe position size
    additional_shares = min(
        current_position.qty * max_multiplier,
        available_buying_power * 0.1,  # Max 10% of buying power
        10000 / current_anomalous_price  # Max $10K position
    )
    
    # Execute limit order at anomalous low
    order = place_stock_order(
        symbol=symbol,
        side="buy",
        quantity=additional_shares,
        order_type="limit",
        limit_price=get_best_bid_price(),
        extended_hours=True
    )
```

#### Phase 3: Lightning Fast Exit
```python
def execute_profit_exit(symbol, new_avg_cost, profit_target_cents):
    exit_price = new_avg_cost + (profit_target_cents / 100)
    
    while True:
        stream_data = get_stock_stream_data(symbol, "quotes", recent_seconds=3)
        current_bid = stream_data.current_bid
        
        if current_bid >= exit_price:
            # IMMEDIATE EXECUTION - NO HESITATION
            sell_order = place_stock_order(
                symbol=symbol,
                side="sell",
                quantity=total_position_size,
                order_type="limit",
                limit_price=current_bid,
                extended_hours=True
            )
            break
        
        time.sleep(2)  # Check every 2 seconds
```

### 📋 EMERGENCY SAFETY MECHANISMS

#### Position Size Protection
```python
MAX_POSITION_MULTIPLIERS = {
    "conservative": 2,
    "moderate": 3,
    "aggressive": 5
}

MAX_CAPITAL_RISK = 0.15  # Never risk more than 15% of account
```

#### Time-Based Exits
- Maximum 45 minutes from start to finish
- Force exit if time limit reached

#### Emergency Stop Loss
- 5% stop loss below new average cost
- Immediate market exit if triggered

---

## Performance Tracking

### 📊 Trade Documentation Template

For every trade, document:
```
TRADE LOG:
Symbol: 
Entry Signal: Trough at $X.XX
Entry Fill: $X.XX (VERIFIED)
Position Size: X shares ($XX,XXX)
Peak Signal: $X.XX
Exit Fill: $X.XX
Profit/Loss: $XXX
Peak Accuracy: Did I wait for peak? Y/N
Size Accuracy: Correct position size? Y/N
Speed Score: Exit within target time? Y/N
```

### 🎯 Success Metrics

#### Target Performance
- **Win Rate:** 70%+ (take small profits consistently)
- **Average Profit:** $100-$500 per trade
- **Time to Exit:** 15-45 minutes maximum
- **Risk/Reward:** 1:2 minimum (risk 2¢ to make 4¢)

#### Red Flags to Stop Strategy
- Win rate drops below 60%
- Average holding time exceeds 1 hour
- Stop losses triggered > 20% of trades
- Extended hours liquidity issues

### 📈 Daily Performance Context

#### Ready to Trade Verification
- [ ] ✅ Server health: All systems operational
- [ ] ✅ Market status: Trading session confirmed
- [ ] ✅ Account verified: Adequate buying power, no restrictions
- [ ] ✅ Data feeds: Low latency, high quality streaming
- [ ] ✅ **Liquidity scanner: trades_per_minute.sh executed**
- [ ] ✅ **Qualified targets: Only 500+ trades/minute stocks**
- [ ] ✅ Technical analysis: Peak/trough signals ready
- [ ] ✅ No stale positions/orders: Clean starting state
- [ ] ✅ Risk rules reviewed: Position sizing confirmed

### 🚀 Day Trading Flow Ready

1. **Scanner** → Use `./trades_per_minute.sh -f combined.lis -t 500`
2. **Filter** → Only trade stocks with 1000+ trades/minute (500+ minimum)
3. **Analysis** → Use `get_stock_peak_trough_analysis()` for entry signals  
4. **Streaming** → Start `start_global_stock_stream()` for real-time monitoring
5. **Execute** → Place limit orders with `place_stock_order()`
6. **Monitor** → Check fills and track with streaming data
7. **Exit** → Follow peak/trough signals for rising trends, immediate exit for declining peaks

---

**🚀 ONLY BEGIN DAY TRADING WHEN ALL ITEMS ARE CHECKED ✅**

**Remember:** Speed + Signals = Success. Follow the tools, trust the process, document everything.

---

*Built from real trading sessions and lessons learned. Updated June 13, 2025.*