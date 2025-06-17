"""Asset information and search tools."""

from typing import Optional
from alpaca.trading.requests import GetAssetsRequest
from alpaca.trading.enums import AssetStatus, AssetClass, AssetExchange
from ...config.settings import get_trading_client
from ...utils.tickers import TickerList


async def get_all_assets(
    status: Optional[str] = None,
    asset_class: Optional[str] = None,
    exchange: Optional[str] = None,
    attributes: Optional[str] = None,
    tradable_only: bool = False,
    max_results: int = 1000,
    use_ticker_list: bool = False,
) -> str:
    """
    Get all available assets with optional filtering.

    Args:
        status: Filter by asset status (e.g., 'active', 'inactive')
        asset_class: Filter by asset class (e.g., 'us_equity', 'crypto')
        exchange: Filter by exchange (e.g., 'NYSE', 'NASDAQ')
        attributes: Comma-separated values to query for multiple attributes
        tradable_only: If True, return only tradable assets
        max_results: Maximum number of results to return (default: 1000)
        use_ticker_list: If True, use TickerList class for optimal filtering
    """
    try:
        # Use TickerList for tradable US equity assets (optimal path)
        if use_ticker_list or (tradable_only and asset_class == "us_equity"):
            try:
                ticker_list = TickerList()
                assets = ticker_list.rest_api.list_assets(status="active")
                
                # Filter using TickerList validation logic
                filtered_assets = [
                    asset for asset in assets 
                    if asset.tradable and ticker_list.is_valid_symbol(asset.symbol)
                ]
                
                # Limit results
                limited_assets = filtered_assets[:max_results]
                
                # Format response
                response_parts = [
                    f"Found {len(limited_assets)} tradable US equity assets (≤4 chars, showing up to {max_results}):"
                ]
                response_parts.append("-" * 70)

                for asset in limited_assets:
                    response_parts.append(f"Symbol: {asset.symbol}")
                    response_parts.append(f"Name: {asset.name}")
                    response_parts.append(f"Exchange: {asset.exchange}")
                    response_parts.append(f"Status: {asset.status}")
                    response_parts.append("Tradable: Yes")
                    response_parts.append("-" * 30)

                if len(filtered_assets) > max_results:
                    response_parts.append(f"... and {len(filtered_assets) - max_results} more tradable assets")
                
                response_parts.append(f"\nSummary: {len(limited_assets)} shown of {len(filtered_assets)} total tradable assets")
                response_parts.append("Filter: Active, tradable, US equity, ≤4 characters, alphabetic only, no TEST symbols")

                return "\n".join(response_parts)
                
            except Exception as e:
                return f"Error using TickerList: {str(e)}"

        # Fallback to original client method
        client = get_trading_client()

        # Create filter if any parameters are provided
        filter_params = None
        if any([status, asset_class, exchange, attributes]):
            # Convert string parameters to enums
            status_enum = None
            if status:
                try:
                    status_enum = AssetStatus(status)
                except ValueError:
                    status_enum = None
            
            asset_class_enum = None
            if asset_class:
                try:
                    asset_class_enum = AssetClass(asset_class)
                except ValueError:
                    asset_class_enum = None
            
            exchange_enum = None
            if exchange:
                try:
                    exchange_enum = AssetExchange(exchange)
                except ValueError:
                    exchange_enum = None
            
            filter_params = GetAssetsRequest(
                status=status_enum,
                asset_class=asset_class_enum,
                exchange=exchange_enum,
                attributes=attributes,
            )

        # Get all assets
        assets = client.get_all_assets(filter_params)

        if not assets:
            return "No assets found matching the criteria."

        # Apply additional filtering
        filtered_assets = assets
        if tradable_only:
            filtered_assets = [asset for asset in assets if asset.tradable]

        # Filter for stock symbols ≤4 characters if asset_class is us_equity
        if asset_class == "us_equity":
            filtered_assets = [
                asset for asset in filtered_assets 
                if len(asset.symbol) <= 4 and asset.symbol.isalpha()
            ]

        # Limit results
        limited_assets = filtered_assets[:max_results]

        if not limited_assets:
            return f"No assets found matching the criteria. Total assets before filtering: {len(assets)}"

        # Format the response
        response_parts = [f"Found {len(limited_assets)} assets (showing up to {max_results}):"]
        response_parts.append("-" * 50)

        for asset in limited_assets:
            response_parts.append(f"Symbol: {asset.symbol}")
            response_parts.append(f"Name: {asset.name}")
            response_parts.append(f"Exchange: {asset.exchange}")
            response_parts.append(f"Class: {asset.asset_class}")
            response_parts.append(f"Status: {asset.status}")
            response_parts.append(f"Tradable: {'Yes' if asset.tradable else 'No'}")
            response_parts.append("-" * 30)

        if len(filtered_assets) > max_results:
            response_parts.append(f"... and {len(filtered_assets) - max_results} more assets matching criteria")
        
        response_parts.append(f"\nSummary: {len(limited_assets)} shown of {len(filtered_assets)} matching assets")

        return "\n".join(response_parts)

    except Exception as e:
        return f"Error fetching assets: {str(e)}"


async def get_asset_info(symbol: str) -> str:
    """
    Retrieves and formats detailed information about a specific asset.

    Args:
        symbol (str): The symbol of the asset to get information for

    Returns:
        str: Formatted string containing asset details
    """
    try:
        client = get_trading_client()
        asset = client.get_asset(symbol)
        return f"""
Asset Information for {symbol}:
----------------------------
Name: {asset.name}
Exchange: {asset.exchange}
Class: {asset.asset_class}
Status: {asset.status}
Tradable: {"Yes" if asset.tradable else "No"}
Marginable: {"Yes" if asset.marginable else "No"}
Shortable: {"Yes" if asset.shortable else "No"}
Easy to Borrow: {"Yes" if asset.easy_to_borrow else "No"}
Fractionable: {"Yes" if asset.fractionable else "No"}
"""
    except Exception as e:
        return f"Error fetching asset info for {symbol}: {str(e)}"
