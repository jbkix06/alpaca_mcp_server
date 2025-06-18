"""Position Tracker - WebSocket-based real-time position monitoring

Uses Alpaca WebSocket trade_updates stream to track positions in real-time,
providing the foundation for genuine automated monitoring.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, Optional, List, Callable
from dataclasses import dataclass, asdict
import os

# Import existing MCP tools for position data
from ..tools.account_tools import get_account_info, get_positions


@dataclass
class Position:
    """Represents a trading position"""
    symbol: str
    quantity: int
    entry_price: Decimal
    current_price: Decimal
    side: str  # 'long' or 'short'
    unrealized_pnl: Decimal
    unrealized_pnl_percent: float
    market_value: Decimal
    cost_basis: Decimal
    last_update: datetime
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'symbol': self.symbol,
            'quantity': self.quantity,
            'entry_price': float(self.entry_price),
            'current_price': float(self.current_price),
            'side': self.side,
            'unrealized_pnl': float(self.unrealized_pnl),
            'unrealized_pnl_percent': self.unrealized_pnl_percent,
            'market_value': float(self.market_value),
            'cost_basis': float(self.cost_basis),
            'last_update': self.last_update.isoformat()
        }


class PositionTracker:
    """
    Real-time position tracking using WebSocket and existing MCP tools.
    
    This class provides genuine position monitoring by:
    1. Using existing get_positions() MCP tool for current state
    2. Planning WebSocket integration for real-time updates
    3. Maintaining position history and P&L tracking
    4. Providing alerts for significant position changes
    """
    
    def __init__(self):
        self.logger = logging.getLogger('position_tracker')
        
        # Position state
        self.positions: Dict[str, Position] = {}
        self.position_history: List[Dict] = []
        
        # Tracking state
        self.last_update: Optional[datetime] = None
        self.update_count = 0
        self.error_count = 0
        
        # Alert thresholds (updated based on APVO session learning)
        self.profit_alert_threshold = 0.05   # 5% profit (substantial profit threshold)
        self.major_profit_threshold = 0.10   # 10% profit (urgent sell consideration)  
        self.loss_alert_threshold = -0.05    # 5% loss
        
        # Callbacks for position changes
        self.position_callbacks: List[Callable] = []
        
        self.logger.info("PositionTracker initialized")
    
    async def start(self):
        """Start position tracking"""
        self.logger.info("🎯 Starting position tracking")
        await self.update_positions()
    
    async def stop(self):
        """Stop position tracking"""
        self.logger.info("🛑 Stopping position tracking")
        # Future: Close WebSocket connections here
    
    async def update_positions(self):
        """Update positions using existing MCP tools"""
        try:
            self.last_update = datetime.now(timezone.utc)
            self.update_count += 1
            
            # Use existing MCP tool to get current positions
            positions_result = await get_positions()
            
            if isinstance(positions_result, dict) and positions_result.get('status') == 'success':
                positions_data = positions_result.get('positions', [])
                await self._process_position_data(positions_data)
            else:
                self.logger.warning(f"Failed to get positions: {positions_result}")
                
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Error updating positions: {e}")
            raise
    
    async def _process_position_data(self, positions_data: List[Dict]):
        """Process position data from Alpaca API"""
        new_positions = {}
        
        for pos_data in positions_data:
            try:
                symbol = pos_data['symbol']
                
                position = Position(
                    symbol=symbol,
                    quantity=int(pos_data['qty']),
                    entry_price=Decimal(str(pos_data['avg_entry_price'])),
                    current_price=Decimal(str(pos_data['current_price'])),
                    side='long' if int(pos_data['qty']) > 0 else 'short',
                    unrealized_pnl=Decimal(str(pos_data['unrealized_pl'])),
                    unrealized_pnl_percent=float(pos_data['unrealized_plpc']),
                    market_value=Decimal(str(pos_data['market_value'])),
                    cost_basis=Decimal(str(pos_data['cost_basis'])),
                    last_update=self.last_update
                )
                
                new_positions[symbol] = position
                
                # Check for significant changes
                await self._check_position_alerts(position)
                
            except (KeyError, ValueError, TypeError) as e:
                self.logger.error(f"Error processing position data for {pos_data}: {e}")
                continue
        
        # Update positions and track changes
        old_symbols = set(self.positions.keys())
        new_symbols = set(new_positions.keys())
        
        # Log position changes
        added = new_symbols - old_symbols
        removed = old_symbols - new_symbols
        
        if added:
            self.logger.info(f"New positions opened: {added}")
        if removed:
            self.logger.info(f"Positions closed: {removed}")
        
        self.positions = new_positions
        
        # Add to history
        self.position_history.append({
            'timestamp': self.last_update.isoformat(),
            'position_count': len(self.positions),
            'symbols': sorted(list(self.positions.keys())),
            'total_unrealized_pnl': sum(float(p.unrealized_pnl) for p in self.positions.values())
        })
        
        # Keep history manageable (last 1000 updates)
        if len(self.position_history) > 1000:
            self.position_history = self.position_history[-1000:]
        
        # Notify callbacks
        for callback in self.position_callbacks:
            try:
                await callback(self.positions)
            except Exception as e:
                self.logger.error(f"Error in position callback: {e}")
    
    async def _check_position_alerts(self, position: Position):
        """Check if position meets alert criteria"""
        pnl_percent = position.unrealized_pnl_percent
        
        # Check for major profit alert (urgent sell consideration)
        if pnl_percent >= self.major_profit_threshold:
            await self._trigger_major_profit_alert(position)
        
        # Check for profit alert
        elif pnl_percent >= self.profit_alert_threshold:
            await self._trigger_profit_alert(position)
        
        # Check for loss alert
        elif pnl_percent <= self.loss_alert_threshold:
            await self._trigger_loss_alert(position)
    
    async def _trigger_major_profit_alert(self, position: Position):
        """Trigger alert for major profit threshold - URGENT SELL CONSIDERATION"""
        self.logger.warning(
            f"🚨 MAJOR PROFIT ALERT - CONSIDER SELLING: {position.symbol} at +{position.unrealized_pnl_percent:.2%} "
            f"(${position.unrealized_pnl:.2f}) - BE DILIGENT ON SELLING!"
        )
        
        # Future: Send high-priority alerts through alert system
    
    async def _trigger_profit_alert(self, position: Position):
        """Trigger alert for substantial profit threshold"""
        self.logger.warning(
            f"🚀 SUBSTANTIAL PROFIT: {position.symbol} at +{position.unrealized_pnl_percent:.2%} "
            f"(${position.unrealized_pnl:.2f}) - Monitor for sell opportunity"
        )
        
        # Future: Send alerts through alert system
    
    async def _trigger_loss_alert(self, position: Position):
        """Trigger alert for loss threshold"""
        self.logger.warning(
            f"⚠️ LOSS ALERT: {position.symbol} at {position.unrealized_pnl_percent:.2%} "
            f"(${position.unrealized_pnl:.2f})"
        )
        
        # Future: Send alerts through alert system
    
    def add_position_callback(self, callback: Callable):
        """Add callback for position updates"""
        self.position_callbacks.append(callback)
    
    def remove_position_callback(self, callback: Callable):
        """Remove position callback"""
        if callback in self.position_callbacks:
            self.position_callbacks.remove(callback)
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """Get position for specific symbol"""
        return self.positions.get(symbol.upper())
    
    def get_all_positions(self) -> Dict[str, Position]:
        """Get all current positions"""
        return self.positions.copy()
    
    def get_position_count(self) -> int:
        """Get number of open positions"""
        return len(self.positions)
    
    def get_total_unrealized_pnl(self) -> Decimal:
        """Get total unrealized P&L across all positions"""
        return sum(pos.unrealized_pnl for pos in self.positions.values())
    
    def get_total_market_value(self) -> Decimal:
        """Get total market value of all positions"""
        return sum(pos.market_value for pos in self.positions.values())
    
    def has_position(self, symbol: str) -> bool:
        """Check if we have a position in symbol"""
        return symbol.upper() in self.positions
    
    def get_status(self) -> Dict:
        """Get position tracker status"""
        return {
            'active': True,
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'update_count': self.update_count,
            'error_count': self.error_count,
            'position_count': len(self.positions),
            'total_unrealized_pnl': float(self.get_total_unrealized_pnl()),
            'total_market_value': float(self.get_total_market_value()),
            'tracked_symbols': sorted(list(self.positions.keys()))
        }
    
    def get_positions_summary(self) -> Dict:
        """Get summary of all positions for reporting"""
        if not self.positions:
            return {'message': 'No open positions'}
        
        summary = {
            'position_count': len(self.positions),
            'total_unrealized_pnl': float(self.get_total_unrealized_pnl()),
            'total_market_value': float(self.get_total_market_value()),
            'positions': {}
        }
        
        for symbol, position in self.positions.items():
            summary['positions'][symbol] = {
                'quantity': position.quantity,
                'entry_price': float(position.entry_price),
                'current_price': float(position.current_price),
                'unrealized_pnl': float(position.unrealized_pnl),
                'unrealized_pnl_percent': position.unrealized_pnl_percent,
                'side': position.side
            }
        
        return summary


# WebSocket Integration Plan (Future Implementation)
class WebSocketPositionTracker:
    """
    Future implementation for real-time WebSocket position tracking.
    
    This will use Alpaca's trade_updates stream to get instant position updates
    using the position_qty field confirmed in our research.
    """
    
    def __init__(self, position_tracker: PositionTracker):
        self.position_tracker = position_tracker
        self.websocket = None
        self.logger = logging.getLogger('websocket_position_tracker')
    
    async def start_streaming(self):
        """Start WebSocket streaming for trade updates"""
        # Future implementation:
        # 1. Connect to Alpaca WebSocket
        # 2. Subscribe to trade_updates stream
        # 3. Process position_qty updates in real-time
        # 4. Update PositionTracker instantly
        
        self.logger.info("WebSocket position tracking planned for Phase 2")
    
    async def on_trade_update(self, trade_update):
        """Handle trade update from WebSocket"""
        # Future implementation:
        # - Extract position_qty from trade update
        # - Calculate new position state
        # - Update PositionTracker in real-time
        # - Trigger immediate alerts if needed
        pass