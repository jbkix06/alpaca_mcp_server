import os
from dotenv import load_dotenv
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta, date
from mcp.server.fastmcp import FastMCP
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOrdersRequest, MarketOrderRequest, LimitOrderRequest, GetAssetsRequest, CreateWatchlistRequest, UpdateWatchlistRequest, GetCalendarRequest, GetCorporateAnnouncementsRequest, ClosePositionRequest, StopOrderRequest, StopLimitOrderRequest, TrailingStopOrderRequest, OptionLegRequest
from alpaca.trading.enums import OrderSide, TimeInForce, QueryOrderStatus, AssetStatus, CorporateActionType, CorporateActionDateType, OrderType, PositionIntent, ContractType, OrderClass
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.historical.option import OptionHistoricalDataClient
from alpaca.data.requests import Sort, StockBarsRequest, StockLatestQuoteRequest, StockTradesRequest, StockLatestTradeRequest, StockLatestBarRequest, OptionLatestQuoteRequest, OptionSnapshotRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.data.live.stock import StockDataStream
from alpaca.trading.models import Order
from alpaca.data.enums import DataFeed, OptionsFeed
from alpaca.common.enums import SupportedCurrencies

import time
from alpaca.common.exceptions import APIError

# Initialize FastMCP server
mcp = FastMCP("alpaca-trading")

# Initialize Alpaca clients using environment variables
load_dotenv()

API_KEY = os.getenv("ALPACA_API_KEY")
API_SECRET = os.getenv("ALPACA_SECRET_KEY")
PAPER = os.getenv("PAPER")
trade_api_url = os.getenv("trade_api_url")
trade_api_wss = os.getenv("trade_api_wss")
data_api_url = os.getenv("data_api_url")
stream_data_wss = os.getenv("stream_data_wss")

if not API_KEY or not API_SECRET:
    raise ValueError("Alpaca API credentials not found in environment variables.")

# Initialize clients
# For trading
trade_client = TradingClient(API_KEY, API_SECRET, paper=PAPER)
# For historical market data
stock_historical_data_client = StockHistoricalDataClient(API_KEY, API_SECRET)
stock_data_stream_client = StockDataStream(API_KEY, API_SECRET, url_override=stream_data_wss)
option_historical_data_client = OptionHistoricalDataClient(api_key=API_KEY, secret_key=API_SECRET)

@mcp.tool()
async def get_account_info() -> str:
    account = trade_client.get_account()
    info = f"""
            Account Information:
            -------------------
            Account ID: {account.id}
            Status: {account.status}
            Currency: {account.currency}
            Buying Power: ${float(account.buying_power):.2f}
            Cash: ${float(account.cash):.2f}
            Portfolio Value: ${float(account.portfolio_value):.2f}
            Equity: ${float(account.equity):.2f}
            Long Market Value: ${float(account.long_market_value):.2f}
            Short Market Value: ${float(account.short_market_value):.2f}
            Pattern Day Trader: {'Yes' if account.pattern_day_trader else 'No'}
            Day Trades Remaining: {account.daytrade_count if hasattr(account, 'daytrade_count') else 'Unknown'}
            """
    return info

@mcp.tool()
async def get_positions() -> str:
    positions = trade_client.get_all_positions()
    if not positions:
        return "No open positions found."
    result = "Current Positions:\n-------------------\n"
    for position in positions:
        result += f"""
                    Symbol: {position.symbol}
                    Quantity: {position.qty} shares
                    Market Value: ${float(position.market_value):.2f}
                    Average Entry Price: ${float(position.avg_entry_price):.2f}
                    Current Price: ${float(position.current_price):.2f}
                    Unrealized P/L: ${float(position.unrealized_pl):.2f} ({float(position.unrealized_plpc) * 100:.2f}%)
                    -------------------
                    """
    return result

@mcp.tool()
async def get_open_position(symbol: str) -> str:
    try:
        position = trade_client.get_open_position(symbol)
        is_option = len(symbol) > 6 and any(c in symbol for c in ['C', 'P'])
        quantity_text = f"{position.qty} contracts" if is_option else f"{position.qty}"
        return f"""
                Position Details for {symbol}:
                ---------------------------
                Quantity: {quantity_text}
                Market Value: ${float(position.market_value):.2f}
                Average Entry Price: ${float(position.avg_entry_price):.2f}
                Current Price: ${float(position.current_price):.2f}
                Unrealized P/L: ${float(position.unrealized_pl):.2f}
                """ 
    except Exception as e:
        return f"Error fetching position: {str(e)}"

@mcp.tool()
async def get_stock_quote(symbol: str) -> str:
    try:
        request_params = StockLatestQuoteRequest(symbol_or_symbols=symbol)
        quotes = stock_historical_data_client.get_stock_latest_quote(request_params)
        if symbol in quotes:
            quote = quotes[symbol]
            return f"""
                    Latest Quote for {symbol}:
                    ------------------------
                    Ask Price: ${quote.ask_price:.2f}
                    Bid Price: ${quote.bid_price:.2f}
                    Ask Size: {quote.ask_size}
                    Bid Size: {quote.bid_size}
                    Timestamp: {quote.timestamp}
                    """ 
        else:
            return f"No quote data found for {symbol}."
    except Exception as e:
        return f"Error fetching quote for {symbol}: {str(e)}"

@mcp.tool()
async def get_stock_bars(symbol: str, days: int = 5) -> str:
    try:
        start_time = datetime.now().date() - timedelta(days=days)
        request_params = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=TimeFrame.Day,
            start=start_time
        )
        bars = stock_historical_data_client.get_stock_bars(request_params)
        if bars[symbol]:
            result = f"Historical Data for {symbol} (Last {days} trading days):\n"
            result += "---------------------------------------------------\n"
            for bar in bars[symbol]:
                result += f"Date: {bar.timestamp.date()}, Open: ${bar.open:.2f}, High: ${bar.high:.2f}, Low: ${bar.low:.2f}, Close: ${bar.close:.2f}, Volume: {bar.volume}\n"
            return result
        else:
            return f"No historical data found for {symbol} in the last {days} days."
    except Exception as e:
        return f"Error fetching historical data for {symbol}: {str(e)}"

@mcp.tool()
async def get_stock_trades(
    symbol: str,
    days: int = 5,
    limit: Optional[int] = None,
    sort: Optional[str] = "asc",
    feed: Optional[str] = None,
    currency: Optional[str] = None,
    asof: Optional[str] = None
) -> str:
    try:
        start_time = datetime.now() - timedelta(days=days)
        sort_enum = Sort.ASC
        if sort and str(sort).lower() == "desc":
            sort_enum = Sort.DESC
        feed_enum = None
        if feed:
            try:
                feed_enum = DataFeed[feed.upper()]
            except Exception:
                feed_enum = None
        currency_enum = None
        if currency:
            try:
                currency_enum = SupportedCurrencies[currency.upper()]
            except Exception:
                currency_enum = None
        request_params = StockTradesRequest(
            symbol_or_symbols=symbol,
            start=start_time,
            end=datetime.now(),
            limit=limit,
            sort=sort_enum,
            feed=feed_enum,
            currency=currency_enum,
            asof=asof
        )
        trades = stock_historical_data_client.get_stock_trades(request_params)
        if symbol in trades:
            result = f"Historical Trades for {symbol} (Last {days} days):\n"
            result += "---------------------------------------------------\n"
            for trade in trades[symbol]:
                result += f"""
                    Time: {trade.timestamp}
                    Price: ${float(trade.price):.6f}
                    Size: {trade.size}
                    Exchange: {trade.exchange}
                    ID: {trade.id}
                    Conditions: {trade.conditions}
                    -------------------
                    """
            return result
        else:
            return f"No trade data found for {symbol} in the last {days} days."
    except Exception as e:
        return f"Error fetching trades: {str(e)}"

@mcp.tool()
async def get_stock_latest_trade(
    symbol: str,
    feed: Optional[str] = None,
    currency: Optional[str] = None
) -> str:
    try:
        feed_enum = None
        if feed:
            try:
                feed_enum = DataFeed[feed.upper()]
            except Exception:
                feed_enum = None
        currency_enum = None
        if currency:
            try:
                currency_enum = SupportedCurrencies[currency.upper()]
            except Exception:
                currency_enum = None
        request_params = StockLatestTradeRequest(
            symbol_or_symbols=symbol,
            feed=feed_enum,
            currency=currency_enum
        )
        latest_trades = stock_historical_data_client.get_stock_latest_trade(request_params)
        if symbol in latest_trades:
            trade = latest_trades[symbol]
            return f"""
                Latest Trade for {symbol}:
                ---------------------------
                Time: {trade.timestamp}
                Price: ${float(trade.price):.6f}
                Size: {trade.size}
                Exchange: {trade.exchange}
                ID: {trade.id}
                Conditions: {trade.conditions}
                """
        else:
            return f"No latest trade data found for {symbol}."
    except Exception as e:
        return f"Error fetching latest trade: {str(e)}"

@mcp.tool()
async def get_stock_latest_bar(
    symbol: str,
    feed: Optional[str] = None,
    currency: Optional[str] = None
) -> str:
    try:
        feed_enum = None
        if feed:
            try:
                feed_enum = DataFeed[feed.upper()]
            except Exception:
                feed_enum = None
        currency_enum = None
        if currency:
            try:
                currency_enum = SupportedCurrencies[currency.upper()]
            except Exception:
                currency_enum = None
        request_params = StockLatestBarRequest(
            symbol_or_symbols=symbol,
            feed=feed_enum,
            currency=currency_enum
        )
        latest_bars = stock_historical_data_client.get_stock_latest_bar(request_params)
        if symbol in latest_bars:
            bar = latest_bars[symbol]
            return f"""
                Latest Minute Bar for {symbol}:
                ---------------------------
                Time: {bar.timestamp}
                Open: ${float(bar.open):.2f}
                High: ${float(bar.high):.2f}
                Low: ${float(bar.low):.2f}
                Close: ${float(bar.close):.2f}
                Volume: {bar.volume}
                """
        else:
            return f"No latest bar data found for {symbol}."
    except Exception as e:
        return f"Error fetching latest bar: {str(e)}"

@mcp.tool()
async def get_orders(status: str = "all", limit: int = 10) -> str:
    try:
        if status.lower() == "open":
            query_status = QueryOrderStatus.OPEN
        elif status.lower() == "closed":
            query_status = QueryOrderStatus.CLOSED
        else:
            query_status = QueryOrderStatus.ALL
        request_params = GetOrdersRequest(
            status=query_status,
            limit=limit
        )
        orders = trade_client.get_orders(request_params)
        if not orders:
            return f"No {status} orders found."
        result = f"{status.capitalize()} Orders (Last {len(orders)}):\n"
        result += "-----------------------------------\n"
        for order in orders:
            result += f"""
                        Symbol: {order.symbol}
                        ID: {order.id}
                        Type: {order.type}
                        Side: {order.side}
                        Quantity: {order.qty}
                        Status: {order.status}
                        Submitted At: {order.submitted_at}
                        """
            if hasattr(order, 'filled_at') and order.filled_at:
                result += f"Filled At: {order.filled_at}\n"
            if hasattr(order, 'filled_avg_price') and order.filled_avg_price:
                result += f"Filled Price: ${float(order.filled_avg_price):.2f}\n"
            result += "-----------------------------------\n"
        return result
    except Exception as e:
        return f"Error fetching orders: {str(e)}"

@mcp.tool()
async def place_stock_order(
    symbol: str,
    side: str,
    quantity: float,
    order_type: str = "market",
    time_in_force: str = "day",
    limit_price: float = None,
    stop_price: float = None,
    trail_price: float = None,
    trail_percent: float = None,
    extended_hours: bool = False,
    client_order_id: str = None
) -> str:
    try:
        if side.lower() == "buy":
            order_side = OrderSide.BUY
        elif side.lower() == "sell":
            order_side = OrderSide.SELL
        else:
            return f"Invalid order side: {side}. Must be 'buy' or 'sell'."
        try:
            tif_enum = TimeInForce[time_in_force.upper()]
        except KeyError:
            return f"Invalid time_in_force: {time_in_force}."
        order_type_upper = order_type.upper()
        if order_type_upper == "MARKET":
            order_data = MarketOrderRequest(
                symbol=symbol,
                qty=quantity,
                side=order_side,
                type=OrderType.MARKET,
                time_in_force=tif_enum,
                extended_hours=extended_hours,
                client_order_id=client_order_id or f"order_{int(time.time())}"
            )
        elif order_type_upper == "LIMIT":
            if limit_price is None:
                return "limit_price is required for LIMIT orders."
            order_data = LimitOrderRequest(
                symbol=symbol,
                qty=quantity,
                side=order_side,
                type=OrderType.LIMIT,
                time_in_force=tif_enum,
                limit_price=limit_price,
                extended_hours=extended_hours,
                client_order_id=client_order_id or f"order_{int(time.time())}"
            )
        elif order_type_upper == "STOP":
            if stop_price is None:
                return "stop_price is required for STOP orders."
            order_data = StopOrderRequest(
                symbol=symbol,
                qty=quantity,
                side=order_side,
                type=OrderType.STOP,
                time_in_force=tif_enum,
                stop_price=stop_price,
                extended_hours=extended_hours,
                client_order_id=client_order_id or f"order_{int(time.time())}"
            )
        elif order_type_upper == "STOP_LIMIT":
            if stop_price is None or limit_price is None:
                return "Both stop_price and limit_price are required for STOP_LIMIT orders."
            order_data = StopLimitOrderRequest(
                symbol=symbol,
                qty=quantity,
                side=order_side,
                type=OrderType.STOP_LIMIT,
                time_in_force=tif_enum,
                stop_price=stop_price,
                limit_price=limit_price,
                extended_hours=extended_hours,
                client_order_id=client_order_id or f"order_{int(time.time())}"
            )
        elif order_type_upper == "TRAILING_STOP":
            if trail_price is None and trail_percent is None:
                return "Either trail_price or trail_percent is required for TRAILING_STOP orders."
            order_data = TrailingStopOrderRequest(
                symbol=symbol,
                qty=quantity,
                side=order_side,
                type=OrderType.TRAILING_STOP,
                time_in_force=tif_enum,
                trail_price=trail_price,
                trail_percent=trail_percent,
                extended_hours=extended_hours,
                client_order_id=client_order_id or f"order_{int(time.time())}"
            )
        else:
            return f"Invalid order type: {order_type}. Must be one of: MARKET, LIMIT, STOP, STOP_LIMIT, TRAILING_STOP."
        order = trade_client.submit_order(order_data)
        return f"""
Order Placed Successfully:
-------------------------
Order ID: {order.id}
Symbol: {order.symbol}
Side: {order.side}
Quantity: {order.qty}
Type: {order.type}
Time In Force: {order.time_in_force}
Status: {order.status}
Client Order ID: {order.client_order_id}
"""
    except Exception as e:
        return f"Error placing order: {str(e)}"

@mcp.tool()
async def cancel_all_orders() -> str:
    try:
        cancel_responses = trade_client.cancel_orders()
        if not cancel_responses:
            return "No orders were found to cancel."
        response_parts = ["Order Cancellation Results:"]
        response_parts.append("-" * 30)
        for response in cancel_responses:
            status = "Success" if response.status == 200 else "Failed"
            response_parts.append(f"Order ID: {response.id}")
            response_parts.append(f"Status: {status}")
            if response.body:
                response_parts.append(f"Details: {response.body}")
            response_parts.append("-" * 30)
        return "\n".join(response_parts)
    except Exception as e:
        return f"Error cancelling orders: {str(e)}"

@mcp.tool()
async def cancel_order_by_id(order_id: str) -> str:
    try:
        response = trade_client.cancel_order_by_id(order_id)
        status = "Success" if response.status == 200 else "Failed"
        result = f"""
        Order Cancellation Result:
        ------------------------
        Order ID: {response.id}
        Status: {status}
        """
        if response.body:
            result += f"Details: {response.body}\n"
        return result
    except Exception as e:
        return f"Error cancelling order {order_id}: {str(e)}"

@mcp.tool()
async def close_position(symbol: str, qty: Optional[str] = None, percentage: Optional[str] = None) -> str:
    try:
        close_options = None
        if qty or percentage:
            close_options = ClosePositionRequest(
                qty=qty,
                percentage=percentage
            )
        order = trade_client.close_position(symbol, close_options)
        return f"""
                Position Closed Successfully:
                ----------------------------
                Symbol: {symbol}
                Order ID: {order.id}
                Status: {order.status}
                """
    except APIError as api_error:
        error_message = str(api_error)
        if "42210000" in error_message and "would result in order size of zero" in error_message:
            return """
            Error: Invalid position closure request.
            The requested percentage would result in less than 1 share.
            Please either:
            1. Use a higher percentage
            2. Close the entire position (100%)
            3. Specify an exact quantity using the qty parameter
            """
        else:
            return f"Error closing position: {error_message}"
    except Exception as e:
        return f"Error closing position: {str(e)}"

@mcp.tool()
async def close_all_positions(cancel_orders: bool = False) -> str:
    try:
        close_responses = trade_client.close_all_positions(cancel_orders=cancel_orders)
        if not close_responses:
            return "No positions were found to close."
        response_parts = ["Position Closure Results:"]
        response_parts.append("-" * 30)
        for response in close_responses:
            response_parts.append(f"Symbol: {response.symbol}")
            response_parts.append(f"Status: {response.status}")
            if response.order_id:
                response_parts.append(f"Order ID: {response.order_id}")
            response_parts.append("-" * 30)
        return "\n".join(response_parts)
    except Exception as e:
        return f"Error closing positions: {str(e)}"

@mcp.tool()
async def get_asset_info(symbol: str) -> str:
    try:
        asset = trade_client.get_asset(symbol)
        return f"""
                Asset Information for {symbol}:
                ----------------------------
                Name: {asset.name}
                Exchange: {asset.exchange}
                Class: {asset.asset_class}
                Status: {asset.status}
                Tradable: {'Yes' if asset.tradable else 'No'}
                Marginable: {'Yes' if asset.marginable else 'No'}
                Shortable: {'Yes' if asset.shortable else 'No'}
                Easy to Borrow: {'Yes' if asset.easy_to_borrow else 'No'}
                Fractionable: {'Yes' if asset.fractionable else 'No'}
                """
    except Exception as e:
        return f"Error fetching asset information: {str(e)}"

@mcp.tool()
async def get_all_assets(
    status: Optional[str] = None,
    asset_class: Optional[str] = None,
    exchange: Optional[str] = None,
    attributes: Optional[str] = None
) -> str:
    try:
        filter_params = None
        if any([status, asset_class, exchange, attributes]):
            filter_params = GetAssetsRequest(
                status=status,
                asset_class=asset_class,
                exchange=exchange,
                attributes=attributes
            )
        assets = trade_client.get_all_assets(filter_params)
        if not assets:
            return "No assets found matching the criteria."
        response_parts = ["Available Assets:"]
        response_parts.append("-" * 30)
        for asset in assets:
            response_parts.append(f"Symbol: {asset.symbol}")
            response_parts.append(f"Name: {asset.name}")
            response_parts.append(f"Exchange: {asset.exchange}")
            response_parts.append(f"Class: {asset.asset_class}")
            response_parts.append(f"Status: {asset.status}")
            response_parts.append(f"Tradable: {'Yes' if asset.tradable else 'No'}")
            response_parts.append("-" * 30)
        return "\n".join(response_parts)
    except Exception as e:
        return f"Error fetching assets: {str(e)}"

@mcp.tool()
async def create_watchlist(name: str, symbols: List[str]) -> str:
    try:
        watchlist_data = CreateWatchlistRequest(name=name, symbols=symbols)
        watchlist = trade_client.create_watchlist(watchlist_data)
        return f"Watchlist '{name}' created successfully with {len(symbols)} symbols."
    except Exception as e:
        return f"Error creating watchlist: {str(e)}"

@mcp.tool()
async def get_watchlists() -> str:
    try:
        watchlists = trade_client.get_watchlists()
        result = "Watchlists:\n------------\n"
        for wl in watchlists:
            result += f"Name: {wl.name}\n"
            result += f"ID: {wl.id}\n"
            result += f"Created: {wl.created_at}\n"
            result += f"Updated: {wl.updated_at}\n"
            result += f"Symbols: {', '.join(getattr(wl, 'symbols', []) or [])}\n\n"
        return result
    except Exception as e:
        return f"Error fetching watchlists: {str(e)}"

@mcp.tool()
async def update_watchlist(watchlist_id: str, name: str = None, symbols: List[str] = None) -> str:
    try:
        update_request = UpdateWatchlistRequest(name=name, symbols=symbols)
        watchlist = trade_client.update_watchlist_by_id(watchlist_id, update_request)
        return f"Watchlist updated successfully: {watchlist.name}"
    except Exception as e:
        return f"Error updating watchlist: {str(e)}"

@mcp.tool()
async def get_market_clock() -> str:
    try:
        clock = trade_client.get_clock()
        return f"""
Market Status:
-------------
Current Time: {clock.timestamp}
Is Open: {'Yes' if clock.is_open else 'No'}
Next Open: {clock.next_open}
Next Close: {clock.next_close}
"""
    except Exception as e:
        return f"Error fetching market clock: {str(e)}"

@mcp.tool()
async def get_market_calendar(start_date: str, end_date: str) -> str:
    try:
        calendar = trade_client.get_calendar(start=start_date, end=end_date)
        result = f"Market Calendar ({start_date} to {end_date}):\n----------------------------\n"
        for day in calendar:
            result += f"Date: {day.date}, Open: {day.open}, Close: {day.close}\n"
        return result
    except Exception as e:
        return f"Error fetching market calendar: {str(e)}"

@mcp.tool()
async def get_corporate_announcements(
    ca_types: List[str],
    since: str,
    until: str,
    symbol: Optional[str] = None,
    cusip: Optional[str] = None,
    date_type: Optional[str] = None
) -> str:
    try:
        ca_type_enums = []
        for t in ca_types:
            try:
                ca_type_enums.append(CorporateActionType[t.upper()])
            except Exception:
                pass
        date_type_enum = None
        if date_type:
            try:
                date_type_enum = CorporateActionDateType[date_type.upper()]
            except Exception:
                date_type_enum = None
        try:
            since_date = datetime.strptime(since, "%Y-%m-%d").date()
            until_date = datetime.strptime(until, "%Y-%m-%d").date()
        except Exception:
            return "Invalid date format, use YYYY-MM-DD"
        request = GetCorporateAnnouncementsRequest(
            ca_types=ca_type_enums,
            since=since_date,
            until=until_date,
            symbol=symbol,
            cusip=cusip,
            date_type=date_type_enum
        )
        announcements = trade_client.get_corporate_announcements(request)
        result = "Corporate Announcements:\n----------------------\n"
        for ann in announcements:
            result += f"""
                        ID: {ann.id}
                        Corporate Action ID: {ann.corporate_action_id}
                        Type: {ann.ca_type}
                        Sub Type: {ann.ca_sub_type}
                        Initiating Symbol: {ann.initiating_symbol}
                        Target Symbol: {ann.target_symbol}
                        Declaration Date: {ann.declaration_date}
                        Ex Date: {ann.ex_date}
                        Record Date: {ann.record_date}
                        Payable Date: {ann.payable_date}
                        Cash: {ann.cash}
                        Old Rate: {ann.old_rate}
                        New Rate: {ann.new_rate}
                        ----------------------
                        """
        return result
    except Exception as e:
        return f"Error fetching corporate announcements: {str(e)}"

@mcp.tool()
async def get_option_contracts(
    underlying_symbol: str,
    expiration_date: Optional[str] = None,
    strike_price_gte: Optional[float] = None,
    strike_price_lte: Optional[float] = None,
    type: Optional[str] = None,
    status: Optional[str] = None,
    root_symbol: Optional[str] = None,
    limit: Optional[int] = None
) -> str:
    try:
        exp_date = None
        if expiration_date:
            try:
                exp_date = datetime.strptime(expiration_date, "%Y-%m-%d").date()
            except Exception:
                return "Invalid expiration_date format, use YYYY-MM-DD"
        contract_type = None
        if type:
            try:
                contract_type = ContractType[type.upper()]
            except Exception:
                contract_type = None
        asset_status = None
        if status:
            try:
                asset_status = AssetStatus[status.upper()]
            except Exception:
                asset_status = None
        request = GetOptionContractsRequest(
            underlying_symbols=[underlying_symbol],
            expiration_date=exp_date,
            strike_price_gte=strike_price_gte,
            strike_price_lte=strike_price_lte,
            type=contract_type,
            status=asset_status,
            root_symbol=root_symbol,
            limit=limit
        )
        response = trade_client.get_option_contracts(request)
        if not response or not response.option_contracts:
            return f"No option contracts found for {underlying_symbol} matching the criteria."
        result = f"Option Contracts for {underlying_symbol}:\n"
        result += "----------------------------------------\n"
        for contract in response.option_contracts:
            result += f"""
                Symbol: {contract.symbol}
                Name: {contract.name}
                Type: {contract.type}
                Strike Price: ${float(contract.strike_price):.2f}
                Expiration Date: {contract.expiration_date}
                Status: {contract.status}
                Root Symbol: {contract.root_symbol}
                Underlying Symbol: {contract.underlying_symbol}
                Exercise Style: {contract.style}
                Contract Size: {contract.size}
                Tradable: {'Yes' if contract.tradable else 'No'}
                Open Interest: {contract.open_interest}
                Close Price: ${float(contract.close_price) if contract.close_price else 'N/A'}
                Close Price Date: {contract.close_price_date}
                -------------------------
                """
        return result
    except Exception as e:
        return f"Error fetching option contracts: {str(e)}"

@mcp.tool()
async def get_option_latest_quote(
    symbol: str,
    feed: Optional[str] = None
) -> str:
    try:
        feed_enum = None
        if feed:
            try:
                feed_enum = OptionsFeed[feed.upper()]
            except Exception:
                feed_enum = None
        request = OptionLatestQuoteRequest(
            symbol_or_symbols=symbol,
            feed=feed_enum
        )
        quotes = option_historical_data_client.get_option_latest_quote(request)
        if symbol in quotes:
            quote = quotes[symbol]
            return f"""
                Latest Quote for {symbol}:
                ------------------------
                Ask Price: ${float(quote.ask_price):.2f}
                Ask Size: {quote.ask_size}
                Ask Exchange: {quote.ask_exchange}
                Bid Price: ${float(quote.bid_price):.2f}
                Bid Size: {quote.bid_size}
                Bid Exchange: {quote.bid_exchange}
                Conditions: {quote.conditions}
                Tape: {quote.tape}
                Timestamp: {quote.timestamp}
                """
        else:
            return f"No quote data found for {symbol}."
    except Exception as e:
        return f"Error fetching option quote: {str(e)}"

@mcp.tool()
async def get_option_snapshot(symbol_or_symbols: Union[str, List[str]], feed: Optional[str] = None) -> str:
    try:
        feed_enum = None
        if feed:
            try:
                feed_enum = OptionsFeed[feed.upper()]
            except Exception:
                feed_enum = None
        request = OptionSnapshotRequest(
            symbol_or_symbols=symbol_or_symbols,
            feed=feed_enum
        )
        snapshots = option_historical_data_client.get_option_snapshot(request)
        result = "Option Snapshots:\n"
        result += "================\n\n"
        symbols = [symbol_or_symbols] if isinstance(symbol_or_symbols, str) else symbol_or_symbols
        for symbol in symbols:
            snapshot = snapshots.get(symbol)
            if snapshot is None:
                result += f"No data available for {symbol}\n"
                continue
            result += f"Symbol: {symbol}\n"
            result += "-----------------\n"
            if snapshot.latest_quote:
                quote = snapshot.latest_quote
                result += f"Latest Quote:\n"
                result += f"  Bid Price: ${quote.bid_price:.6f}\n"
                result += f"  Bid Size: {quote.bid_size}\n"
                result += f"  Bid Exchange: {quote.bid_exchange}\n"
                result += f"  Ask Price: ${quote.ask_price:.6f}\n"
                result += f"  Ask Size: {quote.ask_size}\n"
                result += f"  Ask Exchange: {quote.ask_exchange}\n"
                if quote.conditions:
                    result += f"  Conditions: {quote.conditions}\n"
                if quote.tape:
                    result += f"  Tape: {quote.tape}\n"
                result += f"  Timestamp: {quote.timestamp.strftime('%Y-%m-%d %H:%M:%S.%f %Z')}\n"
            if snapshot.latest_trade:
                trade = snapshot.latest_trade
                result += f"Latest Trade:\n"
                result += f"  Price: ${trade.price:.6f}\n"
                result += f"  Size: {trade.size}\n"
                if trade.exchange:
                    result += f"  Exchange: {trade.exchange}\n"
                if trade.conditions:
                    result += f"  Conditions: {trade.conditions}\n"
                if trade.tape:
                    result += f"  Tape: {trade.tape}\n"
                if trade.id:
                    result += f"  Trade ID: {trade.id}\n"
                result += f"  Timestamp: {trade.timestamp.strftime('%Y-%m-%d %H:%M:%S.%f %Z')}\n"
            if snapshot.implied_volatility is not None:
                result += f"Implied Volatility: {snapshot.implied_volatility:.2%}\n"
            if snapshot.greeks:
                greeks = snapshot.greeks
                result += f"Greeks:\n"
                result += f"  Delta: {greeks.delta:.4f}\n"
                result += f"  Gamma: {greeks.gamma:.4f}\n"
                result += f"  Rho: {greeks.rho:.4f}\n"
                result += f"  Theta: {greeks.theta:.4f}\n"
                result += f"  Vega: {greeks.vega:.4f}\n"
            result += "\n"
        return result
    except Exception as e:
        return f"Error retrieving option snapshots: {str(e)}"

@mcp.tool()
async def place_option_market_order(
    legs: List[Dict[str, Any]],
    order_class: Optional[str] = None,
    quantity: int = 1,
    time_in_force: Optional[str] = "day",
    extended_hours: bool = False
) -> str:
    try:
        if not legs:
            return "Error: No option legs provided"
        if len(legs) > 4:
            return "Error: Maximum of 4 legs allowed for option orders"
        if quantity <= 0:
            return "Error: Quantity must be positive"
        order_class_enum = None
        if order_class:
            class_map = {
                "SIMPLE": OrderClass.SIMPLE,
                "BRACKET": OrderClass.BRACKET,
                "OCO": OrderClass.OCO,
                "OTO": OrderClass.OTO,
                "MLEG": OrderClass.MLEG,
            }
            oc_upper = order_class.upper()
            if oc_upper in class_map:
                order_class_enum = class_map[oc_upper]
            else:
                return f"Invalid order class: {order_class}. Must be one of: simple, bracket, oco, oto, mleg"
        else:
            order_class_enum = OrderClass.MLEG if len(legs) > 1 else OrderClass.SIMPLE
        tif_enum = None
        if time_in_force:
            try:
                tif_enum = TimeInForce[time_in_force.upper()]
            except Exception:
                return f"Invalid time_in_force: {time_in_force}"
        else:
            tif_enum = TimeInForce.DAY
        order_legs = []
        for leg in legs:
            if not isinstance(leg['ratio_qty'], int) or leg['ratio_qty'] <= 0:
                return f"Error: Invalid ratio_qty for leg {leg['symbol']}. Must be positive integer."
            if leg['side'].lower() == "buy":
                order_side = OrderSide.BUY
            elif leg['side'].lower() == "sell":
                order_side = OrderSide.SELL
            else:
                return f"Invalid order side: {leg['side']}. Must be 'buy' or 'sell'."
            order_legs.append(OptionLegRequest(
                symbol=leg['symbol'],
                side=order_side,
                ratio_qty=leg['ratio_qty']
            ))
        if order_class_enum == OrderClass.MLEG:
            order_data = MarketOrderRequest(
                qty=quantity,
                order_class=order_class_enum,
                time_in_force=tif_enum,
                extended_hours=extended_hours,
                client_order_id=f"mcp_opt_{int(time.time())}",
                type=OrderType.MARKET,
                legs=order_legs
            )
        else:
            order_data = MarketOrderRequest(
                symbol=order_legs[0].symbol,
                qty=quantity,
                order_class=order_class_enum,
                time_in_force=tif_enum,
                extended_hours=extended_hours,
                client_order_id=f"mcp_opt_{int(time.time())}",
                type=OrderType.MARKET
            )
        order = trade_client.submit_order(order_data)
        result = f"""
                Option Market Order Placed Successfully:
                --------------------------------------
                Order ID: {order.id}
                Client Order ID: {order.client_order_id}
                Order Class: {order.order_class}
                Order Type: {order.type}
                Time In Force: {order.time_in_force}
                Status: {order.status}
                Quantity: {order.qty}
                Created At: {order.created_at}
                Updated At: {order.updated_at}
                """
        if order_class_enum == OrderClass.MLEG and getattr(order, "legs", None):
            result += "\nLegs:\n"
            for leg in order.legs:
                result += f"""
                        Symbol: {leg.symbol}
                        Side: {leg.side}
                        Ratio Quantity: {leg.ratio_qty}
                        Status: {leg.status}
                        Asset Class: {leg.asset_class}
                        Created At: {leg.created_at}
                        Updated At: {leg.updated_at}
                        Filled Price: {leg.filled_avg_price if hasattr(leg, 'filled_avg_price') else 'Not filled'}
                        Filled Time: {leg.filled_at if hasattr(leg, 'filled_at') else 'Not filled'}
                        -------------------------
                        """
        else:
            result += f"""
                    Symbol: {order.symbol}
                    Side: {order_legs[0].side}
                    Filled Price: {order.filled_avg_price if hasattr(order, 'filled_avg_price') else 'Not filled'}
                    Filled Time: {order.filled_at if hasattr(order, 'filled_at') else 'Not filled'}
                    -------------------------
                    """
        return result
    except APIError as api_error:
        error_message = str(api_error)
        if "40310000" in error_message and "not eligible to trade uncovered option contracts" in error_message:
            # ... as in original, for brevity not repeated here
            return "Error: Account not eligible to trade uncovered option contracts."
        elif "403" in error_message:
            return f"Error: Permission denied for option trading. Original error: {error_message}"
        else:
            return f"Error placing option order: {error_message}"
    except Exception as e:
        return f"Unexpected error placing option order: {str(e)}"

if __name__ == "__main__":  
    mcp.run(transport='stdio')
