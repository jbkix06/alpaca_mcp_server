OK, now let's try something new - a new trading lesson.  Let's concentrate on USEG and the  │
│   snapshot, peak/trough, intraday, and real-time streaming tools.  Here's how it should       │
│   work.  Every 60 seconds, fetch a new snapshot data and use the peak/trough analysis tool    │
│   to look for a new trough, buy signal (assuming the tool fetches the intraday bar data).     │
│   When you receive a trough buy signal and price, then use the streaming tool to buy at the   │
│   lowest or best trade or quote price. It's important at this point to ensure the order is    │
│   filled at the low price before FOMO, so you have to monitor the pre-market order            │
│   aggressively and ensure it fills, before the price goes up.  Timing is critical, so be      │
│   alert.

Yes, I understand the trading strategy:

  60-Second Monitoring Cycle:
  1. Snapshot + Peak/Trough Analysis → Look for new trough/buy signals
  2. Buy Signal Triggered → Use streaming data for optimal entry price
  3. Aggressive Order Management → Monitor fill immediately to avoid FOMO

  Critical Timing Elements:
  - Monitor every 60 seconds for new troughs
  - When trough detected → act immediately with streaming data
  - Get best bid/ask or trade price for entry
  - Watch order fill aggressively before price runs up
  - Pre-market timing is crucial (less liquidity, wider spreads)

  Key Tools Sequence:
  - get_stock_snapshots + get_stock_peak_trough_analysis (every 60s)
  - On trough signal → get_stock_stream_data for real-time pricing
  - place_stock_order with optimal entry price
  - Monitor order status until filled

  Risk Management:
  - Must fill before FOMO kicks in
  - Use limit orders at streaming bid/ask levels
  - Monitor for quick fills in pre-market conditions

  Ready to start the 60-second monitoring cycle for USEG?
