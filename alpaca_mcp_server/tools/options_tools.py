"""Options trading tools and contract information."""

from typing import Optional
from datetime import date
from alpaca.data.requests import OptionChainRequest, OptionLatestQuoteRequest
from alpaca.data.enums import OptionsFeed
from alpaca.trading.enums import ContractType, AssetStatus
from ..config.settings import get_option_historical_client


async def get_option_contracts(
    underlying_symbol: str,
    expiration_date: Optional[date] = None,
    strike_price_gte: Optional[str] = None,
    strike_price_lte: Optional[str] = None,
    type: Optional[ContractType] = None,
    status: Optional[AssetStatus] = None,
    root_symbol: Optional[str] = None,
    limit: Optional[int] = None,
) -> str:
    """
    Retrieves metadata for option contracts based on specified criteria.

    Args:
        underlying_symbol (str): The symbol of the underlying asset (e.g., 'AAPL')
        expiration_date (Optional[date]): Optional expiration date for the options
        strike_price_gte (Optional[str]): Optional minimum strike price
        strike_price_lte (Optional[str]): Optional maximum strike price
        type (Optional[ContractType]): Optional contract type (CALL or PUT)
        status (Optional[AssetStatus]): Optional asset status filter
        root_symbol (Optional[str]): Optional root symbol for the option
        limit (Optional[int]): Optional maximum number of contracts to return

    Returns:
        str: Formatted string containing option contract metadata
    """
    try:
        client = get_option_historical_client()
        request = OptionChainRequest(
            underlying_symbol=underlying_symbol,
            expiration_date=expiration_date,
            strike_price_gte=strike_price_gte,
            strike_price_lte=strike_price_lte,
            contract_type=type,
            limit=limit,
        )

        contracts = client.get_option_chain(request)

        if not contracts:
            return f"No option contracts found for {underlying_symbol}"

        result = f"Option Contracts for {underlying_symbol}:\n" + "=" * 50 + "\n"
        for contract in contracts:
            result += f"""
Contract: {contract.symbol}
Name: {contract.name}
Type: {contract.type}
Strike Price: ${contract.strike_price}
Expiration: {contract.expiration_date}
Status: {contract.status}
Exchange: {contract.exchange}
---
"""
        return result

    except Exception as e:
        return f"Error fetching option contracts: {str(e)}"


async def get_option_latest_quote(
    symbol: str, feed: Optional[OptionsFeed] = None
) -> str:
    """
    Retrieves and formats the latest quote for an option contract.

    Args:
        symbol (str): The option contract symbol (e.g., 'AAPL230616C00150000')
        feed (Optional[OptionsFeed]): The source feed of the data

    Returns:
        str: Formatted string containing the latest quote information
    """
    try:
        client = get_option_historical_client()
        request = OptionLatestQuoteRequest(symbol_or_symbols=symbol, feed=feed)

        quote = client.get_option_latest_quote(request)

        if symbol in quote:
            q = quote[symbol]
            return f"""
Latest Quote for {symbol}:
-------------------------
Ask Price: ${q.ask}
Ask Size: {q.ask_size}
Bid Price: ${q.bid}
Bid Size: {q.bid_size}
Ask Exchange: {q.ask_exchange}
Bid Exchange: {q.bid_exchange}
Timestamp: {q.timestamp}
"""
        else:
            return f"No quote data found for {symbol}"

    except Exception as e:
        return f"Error fetching option quote: {str(e)}"


async def get_option_snapshot(symbol: str) -> str:
    """
    Get comprehensive option snapshot with latest quote, trade, and Greeks.

    Args:
        symbol (str): The option contract symbol

    Returns:
        str: Formatted string containing comprehensive option data
    """
    try:
        client = get_option_historical_client()
        snapshot = client.get_option_snapshot(symbol)

        if not snapshot:
            return f"No snapshot data found for {symbol}"

        return f"""
Option Snapshot for {symbol}:
============================
Latest Quote:
  Ask: ${snapshot.latest_quote.ask} x {snapshot.latest_quote.ask_size}
  Bid: ${snapshot.latest_quote.bid} x {snapshot.latest_quote.bid_size}
  
Latest Trade:
  Price: ${snapshot.latest_trade.price}
  Size: {snapshot.latest_trade.size}
  Exchange: {snapshot.latest_trade.exchange}
  
Greeks (if available):
  Delta: {getattr(snapshot, 'delta', 'N/A')}
  Gamma: {getattr(snapshot, 'gamma', 'N/A')}
  Theta: {getattr(snapshot, 'theta', 'N/A')}
  Vega: {getattr(snapshot, 'vega', 'N/A')}
  
Implied Volatility: {getattr(snapshot, 'implied_volatility', 'N/A')}
Open Interest: {getattr(snapshot, 'open_interest', 'N/A')}
"""

    except Exception as e:
        return f"Error fetching option snapshot: {str(e)}"
