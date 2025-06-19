"""FastAPI-based Hybrid Trading Service

Production-ready monitoring service with REST API, WebSocket streaming,
and persistent background monitoring for automated trading signals.
"""

import asyncio
import json
import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import asdict

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

from .position_tracker import PositionTracker
from .signal_detector import SignalDetector
from .alert_system import AlertSystem
from .hybrid_service import ServiceConfig, ServiceStatus
from .streaming_integration import AlpacaStreamingService
from .desktop_notifications import DesktopNotificationService
from .trade_confirmation import TradeConfirmationService
from ..config import get_global_config, get_scanner_config, get_system_config


class AddSymbolsRequest(BaseModel):
    symbols: List[str] = Field(..., description="List of stock symbols to add")


class RemoveSymbolsRequest(BaseModel):
    symbols: List[str] = Field(..., description="List of stock symbols to remove")


class OrderCheckRequest(BaseModel):
    order_info: Optional[Dict] = Field(None, description="Order information for tracking")


class ScanSyncRequest(BaseModel):
    min_trades_per_minute: int = Field(500, description="Minimum trades per minute for active stocks")
    min_percent_change: float = Field(5.0, description="Minimum percentage change")
    max_symbols: int = Field(20, description="Maximum symbols to monitor")
    force_update: bool = Field(False, description="Force update even if symbols are the same")


class AutoScanConfigRequest(BaseModel):
    enabled: bool = Field(..., description="Enable/disable automatic scanning")
    interval_seconds: int = Field(60, description="Scan interval in seconds (minimum 30)")
    min_trades_per_minute: int = Field(500, description="Minimum trades per minute threshold")
    min_percent_change: float = Field(5.0, description="Minimum percentage change threshold")
    max_symbols: int = Field(20, description="Maximum symbols to monitor")


class TradeConfirmationRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol")
    action: str = Field(..., description="BUY or SELL")
    quantity: int = Field(..., description="Number of shares")
    expected_price: float = Field(..., description="Expected execution price")


class ConfirmExecutionRequest(BaseModel):
    trade_id: str = Field(..., description="Trade confirmation ID")
    actual_price: float = Field(..., description="Actual execution price")
    fill_timestamp: str = Field(..., description="Execution timestamp")
    screenshot_path: Optional[str] = Field(None, description="Path to screenshot proof")


class OrderRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol")
    side: str = Field(..., description="buy or sell")
    quantity: int = Field(..., description="Number of shares")
    order_type: str = Field("limit", description="Order type")
    limit_price: Optional[float] = Field(None, description="Limit price for limit orders")
    time_in_force: str = Field("day", description="Time in force")


class MonitoringServiceAPI:
    """Core monitoring service with FastAPI integration"""
    
    def __init__(self):
        self.config = ServiceConfig()
        self.logger = self._setup_logging()
        
        # Service state
        self.active = False
        self.start_time: Optional[datetime] = None
        self.last_check: Optional[datetime] = None
        self.check_count = 0
        self.error_count = 0
        
        # Initialize core components immediately for API availability
        try:
            self.position_tracker = PositionTracker()
            self.signal_detector = SignalDetector()
            self.alert_system = AlertSystem(self.config.alert_channels)
            self.desktop_notifications = DesktopNotificationService()
            self.trade_confirmation = TradeConfirmationService(self.desktop_notifications)
            self.streaming_service = AlpacaStreamingService()
            self.logger.info("All services initialized successfully")
        except Exception as e:
            self.logger.warning(f"Some services failed to initialize: {e}")
            # Initialize with minimal fallback services to ensure API responses work
            self.position_tracker = PositionTracker() if not hasattr(self, 'position_tracker') else self.position_tracker
            self.signal_detector = SignalDetector() if not hasattr(self, 'signal_detector') else self.signal_detector
            self.alert_system = AlertSystem([]) if not hasattr(self, 'alert_system') else self.alert_system
            self.desktop_notifications = DesktopNotificationService() if not hasattr(self, 'desktop_notifications') else self.desktop_notifications
            self.trade_confirmation = TradeConfirmationService(self.desktop_notifications) if not hasattr(self, 'trade_confirmation') else self.trade_confirmation
            self.streaming_service = AlpacaStreamingService() if not hasattr(self, 'streaming_service') else self.streaming_service
        
        # Monitoring state
        self.watchlist: Set[str] = set()
        self.current_signals: List[Dict] = []
        self.signal_history: List[Dict] = []
        self.monitoring_task: Optional[asyncio.Task] = None
        
        # Auto-scanning configuration from global config
        scanner_config = get_scanner_config()
        self.auto_scan_enabled = True
        self.scan_interval_seconds = scanner_config.active_scan_interval_seconds
        self.scan_params = {
            "min_trades_per_minute": None,  # Use global config defaults
            "min_percent_change": None,     # Use global config defaults
            "max_symbols": None             # Use global config defaults
        }
        self.last_scan_time: Optional[datetime] = None
        
        # Hibernation mode for resource optimization from global config
        system_config = get_system_config()
        self.hibernation_enabled = system_config.hibernation_enabled
        self.is_hibernating = False
        self.hibernation_reason: Optional[str] = None
        
        # WebSocket connections for real-time updates
        self.websocket_connections: Set[WebSocket] = set()
        
        # Communication files
        self.state_dir = Path("monitoring_data")
        self.state_dir.mkdir(exist_ok=True)
        
        self.logger.info("MonitoringServiceAPI initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Set up structured logging for audit trail"""
        logger = logging.getLogger('fastapi_monitoring_service')
        logger.setLevel(logging.INFO)
        
        # Remove existing handlers to avoid duplicates
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # File handler for permanent audit trail
        log_path = Path("fastapi_monitoring.log")
        fh = logging.FileHandler(log_path)
        fh.setLevel(logging.INFO)
        
        # Console handler for real-time monitoring
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Structured formatter for audit compliance
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
        
        return logger
    
    async def startup(self):
        """Initialize service components on startup"""
        try:
            self.logger.info("🚀 Starting FastAPI Monitoring Service")
            
            # Initialize components
            self.position_tracker = PositionTracker()
            self.signal_detector = SignalDetector()
            self.alert_system = AlertSystem(self.config.alert_channels)
            self.streaming_service = AlpacaStreamingService()
            self.desktop_notifications = DesktopNotificationService()
            self.trade_confirmation = TradeConfirmationService(self.desktop_notifications)
            
            # Load previous state if exists
            await self._load_state()
            
            # Mark service as active
            self.active = True
            self.start_time = datetime.now(timezone.utc)
            self.last_check = None
            self.check_count = 0
            self.error_count = 0
            
            # Check positions immediately on startup
            if self.position_tracker:
                await self.position_tracker.update_positions()
                initial_position_count = len(self.position_tracker.positions)
                self._last_position_count = initial_position_count
                
                if initial_position_count > 0:
                    position_symbols = list(self.position_tracker.positions.keys())
                    self.logger.warning(f"🔔 STARTUP: Found {initial_position_count} existing positions: {position_symbols}")
                    
                    # Alert about existing positions
                    await self.alert_system.send_alert(
                        "📊 Existing Positions Detected at Startup",
                        f"Found {initial_position_count} open positions: {', '.join(position_symbols)}",
                        priority="high"
                    )
                else:
                    self.logger.info("✅ STARTUP: No existing positions found")
            
            # Setup streaming callbacks and start
            if self.streaming_service:
                self.streaming_service.set_callbacks(
                    on_trade_update=self._handle_trade_update,
                    on_profit_spike=self._handle_profit_spike
                )
                await self.streaming_service.start()
                if self.watchlist:
                    await self.streaming_service.subscribe_market_data(list(self.watchlist))
            
            # Start background monitoring task
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            
            # Send startup alert
            await self.alert_system.send_alert(
                "🚀 FastAPI Monitoring Service STARTED",
                f"Service running with {len(self.watchlist)} symbols in watchlist",
                priority="info"
            )
            
            # Save initial state
            await self._save_state()
            
            self.logger.info("✅ FastAPI Monitoring Service started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start service: {e}")
            self.active = False
            raise
    
    async def shutdown(self):
        """Clean shutdown of service components"""
        try:
            self.logger.info("🛑 Stopping FastAPI Monitoring Service")
            
            # Mark as inactive
            self.active = False
            
            # Cancel monitoring task
            if self.monitoring_task and not self.monitoring_task.done():
                self.monitoring_task.cancel()
                try:
                    await self.monitoring_task
                except asyncio.CancelledError:
                    pass
            
            # Close WebSocket connections
            for websocket in self.websocket_connections.copy():
                try:
                    await websocket.close()
                except:
                    pass
            self.websocket_connections.clear()
            
            # Clean shutdown of components
            if self.streaming_service:
                await self.streaming_service.stop()
            
            if self.position_tracker:
                await self.position_tracker.stop()
            
            # Save final state
            await self._save_state()
            
            # Send shutdown alert
            if self.alert_system:
                uptime = time.time() - self.start_time.timestamp() if self.start_time else 0
                await self.alert_system.send_alert(
                    "🛑 FastAPI Monitoring Service STOPPED",
                    f"Service stopped after {uptime:.0f} seconds uptime. "
                    f"Completed {self.check_count} monitoring cycles.",
                    priority="warning"
                )
            
            self.logger.info("✅ FastAPI Monitoring Service stopped gracefully")
            
        except Exception as e:
            self.logger.error(f"Error during service shutdown: {e}")
    
    async def get_health(self) -> Dict:
        """Health check endpoint"""
        uptime = 0
        if self.start_time:
            uptime = time.time() - self.start_time.timestamp()
        
        return {
            "status": "healthy" if self.active else "inactive",
            "uptime_seconds": uptime,
            "check_count": self.check_count,
            "error_count": self.error_count,
            "watchlist_size": len(self.watchlist),
            "active_positions": len(self.position_tracker.positions) if self.position_tracker else 0,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def get_status(self) -> ServiceStatus:
        """Get detailed service status"""
        uptime = 0
        if self.start_time:
            uptime = time.time() - self.start_time.timestamp()
        
        return ServiceStatus(
            active=self.active,
            start_time=self.start_time,
            last_check=self.last_check,
            watchlist_size=len(self.watchlist),
            active_positions=len(self.position_tracker.positions) if self.position_tracker else 0,
            signals_detected_today=len([s for s in self.signal_history 
                                      if s.get('timestamp', '').startswith(datetime.now().strftime('%Y-%m-%d'))]),
            uptime_seconds=uptime,
            check_count=self.check_count,
            error_count=self.error_count
        )
    
    async def get_watchlist(self) -> Dict:
        """Get current watchlist"""
        return {
            "watchlist": sorted(list(self.watchlist)),
            "size": len(self.watchlist),
            "limit": self.config.watchlist_size_limit,
            "last_updated": self.last_check.isoformat() if self.last_check else None
        }
    
    async def add_symbols(self, symbols: List[str]) -> Dict:
        """Add symbols to watchlist"""
        added = []
        errors = []
        
        for symbol in symbols:
            symbol = symbol.upper().strip()
            if len(self.watchlist) >= self.config.watchlist_size_limit:
                errors.append(f"Watchlist limit reached ({self.config.watchlist_size_limit})")
                break
            if symbol not in self.watchlist:
                self.watchlist.add(symbol)
                added.append(symbol)
        
        if added:
            await self._save_state()
            self.logger.info(f"Added to watchlist: {added}")
            
            # Update streaming subscriptions for new symbols
            if self.streaming_service and self.streaming_service.is_running:
                try:
                    await self.streaming_service.subscribe_market_data(added)
                    self.logger.info(f"Added streaming subscriptions for: {added}")
                except Exception as e:
                    self.logger.error(f"Failed to subscribe to streaming for {added}: {e}")
            
            # Send WebSocket update
            await self._broadcast_update({
                "type": "watchlist_update",
                "action": "added",
                "symbols": added,
                "watchlist_size": len(self.watchlist)
            })
            
            if self.alert_system:
                await self.alert_system.send_alert(
                    "📊 Watchlist Updated",
                    f"Added symbols: {', '.join(added)}. Total watchlist: {len(self.watchlist)}",
                    priority="info"
                )
            
            # Check hibernation conditions after adding symbols
            if self.hibernation_enabled:
                try:
                    await self.check_hibernation_conditions()
                except Exception as e:
                    self.logger.error(f"❌ Hibernation check failed after adding symbols: {e}")
        
        return {
            "status": "success",
            "added": added,
            "errors": errors,
            "watchlist_size": len(self.watchlist),
            "current_watchlist": sorted(list(self.watchlist))
        }
    
    async def remove_symbols(self, symbols: List[str]) -> Dict:
        """Remove symbols from watchlist"""
        removed = []
        
        for symbol in symbols:
            symbol = symbol.upper().strip()
            if symbol in self.watchlist:
                self.watchlist.remove(symbol)
                removed.append(symbol)
        
        if removed:
            await self._save_state()
            self.logger.info(f"Removed from watchlist: {removed}")
            
            # Update streaming subscriptions for removed symbols
            if self.streaming_service and self.streaming_service.is_running:
                try:
                    await self.streaming_service.unsubscribe_market_data(removed)
                    self.logger.info(f"Removed streaming subscriptions for: {removed}")
                except Exception as e:
                    self.logger.error(f"Failed to unsubscribe from streaming for {removed}: {e}")
            
            # Send WebSocket update
            await self._broadcast_update({
                "type": "watchlist_update",
                "action": "removed",
                "symbols": removed,
                "watchlist_size": len(self.watchlist)
            })
            
            if self.alert_system:
                await self.alert_system.send_alert(
                    "📊 Watchlist Updated",
                    f"Removed symbols: {', '.join(removed)}. Total watchlist: {len(self.watchlist)}",
                    priority="info"
                )
            
            # Check hibernation conditions after removing symbols
            if self.hibernation_enabled:
                try:
                    await self.check_hibernation_conditions()
                except Exception as e:
                    self.logger.error(f"❌ Hibernation check failed after removing symbols: {e}")
        
        return {
            "status": "success",
            "removed": removed,
            "watchlist_size": len(self.watchlist),
            "current_watchlist": sorted(list(self.watchlist))
        }
    
    async def sync_with_scanner_results(self, scan_params: Dict) -> Dict:
        """Sync watchlist with active scanner results"""
        try:
            # Use MCP scan tool for accurate results - same tool as /alpaca-trading:scan
            from ..tools.day_trading_scanner import scan_day_trading_opportunities
            
            # Call the MCP scan tool with exact parameters
            scan_result_text = await scan_day_trading_opportunities(
                symbols="ALL",
                min_trades_per_minute=scan_params.get("min_trades_per_minute", 500),
                min_percent_change=scan_params.get("min_percent_change", 10.0),
                max_symbols=scan_params.get("max_symbols", 20),
                sort_by="trades"
            )
            
            # Extract active symbols from scan result text
            active_symbols = set()
            if scan_result_text:
                # Look for the specific data table format in scan results
                lines = scan_result_text.split('\n')
                in_data_section = False
                
                for line in lines:
                    line = line.strip()
                    
                    # Start of data table (look for header with "Rank Symbol")
                    if "Rank Symbol" in line or "Rank  Symbol" in line:
                        in_data_section = True
                        continue
                    
                    # End of data table (empty line or section break)
                    if in_data_section and (not line or line.startswith('**') or line.startswith('=')):
                        break
                    
                    # Parse data rows (should start with a number and have symbol as second element)
                    if in_data_section and line and line[0].isdigit():
                        parts = line.split()
                        if len(parts) >= 2:
                            potential_symbol = parts[1].strip()
                            # Validate: 1-5 chars, all uppercase letters, no common words
                            if (1 <= len(potential_symbol) <= 5 and 
                                potential_symbol.isalpha() and 
                                potential_symbol.isupper() and
                                potential_symbol not in ['FOR', 'SCAN', 'TRY', 'THE', 'AND', 'WITH']):
                                active_symbols.add(potential_symbol)
            
            # Get active positions to protect from removal
            protected_symbols = set()
            if self.position_tracker:
                await self.position_tracker.update_positions()
                protected_symbols = set(self.position_tracker.positions.keys())
            
            # Compare with current watchlist
            current_watchlist = set(self.watchlist)
            to_add = active_symbols - current_watchlist
            
            # CRITICAL: Never remove symbols with active positions
            potential_removals = current_watchlist - active_symbols
            to_remove = potential_removals - protected_symbols
            protected_from_removal = potential_removals & protected_symbols
            
            if protected_from_removal:
                self.logger.warning(f"Protected symbols with active positions from removal: {protected_from_removal}")
                # Keep protected symbols in active list for continued monitoring
                active_symbols.update(protected_from_removal)
            
            # Only proceed if there are changes or force_update is True
            if not to_add and not to_remove and not scan_params.get("force_update", False):
                message = "Watchlist already synced with active stocks"
                if protected_from_removal:
                    message += f". Protected {len(protected_from_removal)} position stocks from removal."
                    
                return {
                    "status": "no_changes",
                    "message": message,
                    "protected": sorted(list(protected_from_removal)) if protected_from_removal else [],
                    "active_symbols": sorted(list(active_symbols)),
                    "watchlist_size": len(self.watchlist)
                }
            
            sync_results = []
            
            # Remove inactive symbols
            if to_remove:
                remove_result = await self.remove_symbols(list(to_remove))
                sync_results.append(f"Removed {len(to_remove)} inactive symbols")
            
            # Add new active symbols
            if to_add:
                add_result = await self.add_symbols(list(to_add))
                sync_results.append(f"Added {len(to_add)} new active symbols")
            
            self.logger.info(f"Watchlist synced with scanner: +{len(to_add)}, -{len(to_remove)}")
            
            sync_message = f"Watchlist synced with active stocks. {'; '.join(sync_results)}"
            if protected_from_removal:
                sync_message += f" Protected {len(protected_from_removal)} position stocks from removal."
            
            return {
                "status": "success",
                "message": sync_message,
                "added": sorted(list(to_add)),
                "removed": sorted(list(to_remove)),
                "protected": sorted(list(protected_from_removal)) if protected_from_removal else [],
                "active_symbols": sorted(list(active_symbols)),
                "watchlist_size": len(self.watchlist),
                "scan_parameters": scan_params
            }
            
        except Exception as e:
            self.logger.error(f"Failed to sync with scanner results: {e}")
            return {
                "status": "error",
                "message": f"Sync failed: {str(e)}",
                "watchlist_size": len(self.watchlist)
            }
    
    async def configure_auto_scan(self, config: Dict) -> Dict:
        """Configure automatic scanning parameters"""
        try:
            # Validate interval (minimum 30 seconds)
            interval = max(30, config.get("interval_seconds", 60))
            
            # Update configuration
            old_enabled = self.auto_scan_enabled
            self.auto_scan_enabled = config.get("enabled", True)
            self.scan_interval_seconds = interval
            self.scan_params = {
                "min_trades_per_minute": config.get("min_trades_per_minute", 500),
                "min_percent_change": config.get("min_percent_change", 5.0),
                "max_symbols": config.get("max_symbols", 20)
            }
            
            # Reset scan timer if enabled/disabled changed
            if old_enabled != self.auto_scan_enabled:
                self.last_scan_time = None
            
            await self._save_state()
            
            status_msg = "enabled" if self.auto_scan_enabled else "disabled"
            self.logger.info(f"📊 Auto-scanning {status_msg}: {interval}s interval, {self.scan_params}")
            
            return {
                "status": "success",
                "message": f"Auto-scanning {status_msg}",
                "config": {
                    "enabled": self.auto_scan_enabled,
                    "interval_seconds": self.scan_interval_seconds,
                    **self.scan_params
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to configure auto-scan: {e}")
            return {
                "status": "error",
                "message": f"Configuration failed: {str(e)}"
            }
    
    async def get_auto_scan_status(self) -> Dict:
        """Get current auto-scanning configuration and status"""
        next_scan = None
        if self.auto_scan_enabled and self.last_scan_time:
            next_scan_time = self.last_scan_time.timestamp() + self.scan_interval_seconds
            next_scan = datetime.fromtimestamp(next_scan_time, timezone.utc).isoformat()
        
        return {
            "enabled": self.auto_scan_enabled,
            "interval_seconds": self.scan_interval_seconds,
            "last_scan": self.last_scan_time.isoformat() if self.last_scan_time else None,
            "next_scan": next_scan,
            "scan_parameters": self.scan_params
        }
    
    async def check_hibernation_conditions(self) -> bool:
        """Check if system should enter hibernation mode"""
        if not self.hibernation_enabled:
            return False
        
        # Get current positions
        position_count = 0
        if self.position_tracker:
            await self.position_tracker.update_positions()
            position_count = len(self.position_tracker.positions)
        
        # Check conditions for hibernation
        no_watchlist = len(self.watchlist) == 0
        no_positions = position_count == 0
        
        should_hibernate = no_watchlist and no_positions
        
        if should_hibernate and not self.is_hibernating:
            await self._enter_hibernation()
        elif not should_hibernate and self.is_hibernating:
            await self._exit_hibernation()
        
        return self.is_hibernating
    
    async def _enter_hibernation(self):
        """Enter hibernation mode - stop streaming to save resources"""
        if self.is_hibernating:
            return
        
        self.logger.info("💤 Entering hibernation mode: No active stocks or positions to monitor")
        
        # Stop streaming service
        if self.streaming_service and self.streaming_service.is_running:
            try:
                await self.streaming_service.stop()
                self.logger.info("🛑 Streaming service stopped for hibernation")
            except Exception as e:
                self.logger.error(f"Error stopping streaming for hibernation: {e}")
        
        self.is_hibernating = True
        self.hibernation_reason = f"No watchlist ({len(self.watchlist)}) and no positions"
        
        # Broadcast hibernation status
        await self._broadcast_update({
            "type": "hibernation_started",
            "reason": self.hibernation_reason,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    async def _exit_hibernation(self):
        """Exit hibernation mode - restart streaming"""
        if not self.is_hibernating:
            return
        
        self.logger.info("🔥 Exiting hibernation mode: Active stocks or positions detected")
        
        # Restart streaming service if there are symbols to monitor
        if len(self.watchlist) > 0 and self.streaming_service:
            try:
                await self.streaming_service.start()
                await self.streaming_service.subscribe_market_data(list(self.watchlist))
                self.logger.info(f"🚀 Streaming service restarted for {len(self.watchlist)} symbols")
            except Exception as e:
                self.logger.error(f"Error restarting streaming after hibernation: {e}")
        
        self.is_hibernating = False
        old_reason = self.hibernation_reason
        self.hibernation_reason = None
        
        # Broadcast wake status
        await self._broadcast_update({
            "type": "hibernation_ended",
            "previous_reason": old_reason,
            "watchlist_size": len(self.watchlist),
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    async def get_hibernation_status(self) -> Dict:
        """Get current hibernation status with fresh data"""
        # Get fresh position count
        position_count = 0
        if self.position_tracker:
            await self.position_tracker.update_positions()
            position_count = len(self.position_tracker.positions)
        
        return {
            "hibernation_enabled": self.hibernation_enabled,
            "is_hibernating": self.is_hibernating,
            "hibernation_reason": self.hibernation_reason,
            "watchlist_size": len(self.watchlist),
            "active_positions": position_count,
            "streaming_active": self.streaming_service.is_running if self.streaming_service else False
        }
    
    async def get_positions(self) -> Dict:
        """Get current positions"""
        if not self.position_tracker:
            return {"positions": [], "count": 0}
        
        await self.position_tracker.update_positions()
        positions = []
        
        for symbol, position in self.position_tracker.positions.items():
            positions.append({
                "symbol": symbol,
                "quantity": float(position.qty),
                "market_value": float(position.market_value),
                "unrealized_pl": float(position.unrealized_pl),
                "unrealized_plpc": float(position.unrealized_plpc),
                "avg_entry_price": float(position.avg_entry_price),
                "current_price": float(position.current_price) if position.current_price else None
            })
        
        return {
            "positions": positions,
            "count": len(positions),
            "total_market_value": sum(float(p.market_value) for p in self.position_tracker.positions.values()),
            "total_unrealized_pl": sum(float(p.unrealized_pl) for p in self.position_tracker.positions.values())
        }
    
    async def get_signals(self) -> Dict:
        """Get current trading signals"""
        return {
            "current_signals": self.current_signals,
            "signal_count": len(self.current_signals),
            "last_updated": self.last_check.isoformat() if self.last_check else None
        }
    
    async def check_positions_after_order(self, order_info: Optional[Dict] = None) -> Dict:
        """Check positions immediately after an order"""
        if not self.position_tracker:
            return {"status": "error", "message": "Position tracker not available"}
        
        try:
            # Force immediate position update
            await self.position_tracker.update_positions()
            position_count = len(self.position_tracker.positions)
            position_symbols = list(self.position_tracker.positions.keys())
            
            # Log the check
            if order_info:
                self.logger.warning(f"🔔 POST-ORDER CHECK: After {order_info.get('action', 'order')}, found {position_count} positions: {position_symbols}")
            else:
                self.logger.warning(f"🔔 POSITION CHECK: Currently {position_count} positions: {position_symbols}")
            
            # Send WebSocket update
            await self._broadcast_update({
                "type": "position_update",
                "position_count": position_count,
                "positions": position_symbols,
                "order_info": order_info
            })
            
            # Send alert
            if self.alert_system:
                message = f"Post-order position check: {position_count} positions"
                if position_symbols:
                    message += f" ({', '.join(position_symbols)})"
                
                await self.alert_system.send_alert(
                    "📊 Position Status Check",
                    message,
                    priority="high"
                )
            
            # Update tracking
            self._last_position_count = position_count
            
            return {
                "status": "success",
                "position_count": position_count,
                "positions": position_symbols,
                "message": f"Found {position_count} positions: {position_symbols}"
            }
            
        except Exception as e:
            self.logger.error(f"Error checking positions after order: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _monitoring_loop(self):
        """Main monitoring loop - runs continuously"""
        self.logger.info("🔄 Starting FastAPI monitoring loop")
        
        while self.active:
            try:
                await self._monitoring_cycle()
                await asyncio.sleep(self.config.check_interval)
                
            except asyncio.CancelledError:
                self.logger.info("Monitoring loop cancelled")
                break
            except Exception as e:
                self.error_count += 1
                self.logger.error(f"Error in monitoring cycle: {e}")
                
                # Send error alert if too many errors
                if self.error_count % 10 == 0:
                    await self.alert_system.send_alert(
                        "🚨 Monitoring Errors",
                        f"Service has encountered {self.error_count} errors. Latest: {e}",
                        priority="warning"
                    )
                
                # Continue monitoring despite errors
                await asyncio.sleep(self.config.check_interval)
    
    async def _monitoring_cycle(self):
        """Single monitoring cycle"""
        self.last_check = datetime.now(timezone.utc)
        self.check_count += 1
        
        # Log heartbeat every 100 cycles
        if self.check_count % 100 == 0:
            position_count = len(self.position_tracker.positions) if self.position_tracker else 0
            self.logger.info(f"💓 FastAPI Heartbeat - Cycle {self.check_count}, Watchlist: {len(self.watchlist)}, Positions: {position_count}")
        
        # Update positions
        if self.position_tracker:
            await self.position_tracker.update_positions()
            
            # Log position changes
            position_count = len(self.position_tracker.positions)
            if hasattr(self, '_last_position_count') and self._last_position_count != position_count:
                change_data = {
                    "type": "position_change",
                    "previous_count": getattr(self, '_last_position_count', 0),
                    "current_count": position_count,
                    "change": "increase" if position_count > self._last_position_count else "decrease"
                }
                
                # Broadcast to WebSocket clients
                await self._broadcast_update(change_data)
                
                if position_count > self._last_position_count:
                    self.logger.warning(f"🔔 NEW POSITIONS DETECTED: {position_count} total positions now active")
                elif position_count < self._last_position_count:
                    self.logger.warning(f"🔔 POSITIONS CLOSED: {position_count} positions remaining (was {self._last_position_count})")
                    
                # Alert about position changes
                if self.alert_system:
                    await self.alert_system.send_alert(
                        "📊 Position Change Detected",
                        f"Position count changed from {getattr(self, '_last_position_count', 0)} to {position_count}",
                        priority="high"
                    )
            
            self._last_position_count = position_count
        
        # Detect signals for watchlist
        if self.signal_detector and self.watchlist:
            new_signals = await self.signal_detector.scan_for_signals(
                list(self.watchlist),
                confidence_threshold=self.config.signal_confidence_threshold
            )
            
            # Process new signals
            for signal in new_signals:
                await self._process_signal(signal)
        
        # Automatic watchlist synchronization with scanner results
        if self.auto_scan_enabled:
            now = datetime.now(timezone.utc)
            if (self.last_scan_time is None or 
                (now - self.last_scan_time).total_seconds() >= self.scan_interval_seconds):
                
                try:
                    self.logger.info("🔍 Starting automatic watchlist sync with scanner")
                    sync_result = await self.sync_with_scanner_results(self.scan_params)
                    self.last_scan_time = now
                    
                    if sync_result.get("status") in ["success", "no_changes"]:
                        self.logger.info(f"📊 Auto-scan completed: {sync_result.get('message', 'No changes')}")
                        
                        # Broadcast scan results to WebSocket clients
                        await self._broadcast_update({
                            "type": "auto_scan_update",
                            "result": sync_result,
                            "timestamp": now.isoformat()
                        })
                    else:
                        self.logger.warning(f"⚠️ Auto-scan had issues: {sync_result.get('message', 'Unknown error')}")
                        
                except Exception as e:
                    self.logger.error(f"❌ Auto-scan failed: {e}")
                    self.error_count += 1
        
        # Check hibernation conditions after auto-scan
        if self.hibernation_enabled:
            try:
                await self.check_hibernation_conditions()
            except Exception as e:
                self.logger.error(f"❌ Hibernation check failed: {e}")
        
        # Save state periodically
        if self.check_count % 50 == 0:  # Every ~100 seconds
            await self._save_state()
    
    async def _process_signal(self, signal: Dict):
        """Process a detected trading signal"""
        signal['timestamp'] = datetime.now(timezone.utc).isoformat()
        signal['id'] = f"{signal['symbol']}_{int(time.time())}"
        
        # Add to current signals
        self.current_signals.append(signal)
        self.signal_history.append(signal)
        
        # Keep only recent signals in current list
        cutoff_time = time.time() - 3600  # 1 hour
        self.current_signals = [
            s for s in self.current_signals 
            if datetime.fromisoformat(s['timestamp'].replace('Z', '+00:00')).timestamp() > cutoff_time
        ]
        
        # Broadcast signal to WebSocket clients
        await self._broadcast_update({
            "type": "new_signal",
            "signal": signal
        })
        
        # Send alert for high-confidence signals
        if signal.get('confidence', 0) >= self.config.signal_confidence_threshold:
            await self._send_signal_alert(signal)
        
        self.logger.info(f"Signal detected: {signal['symbol']} - {signal['signal_type']} (confidence: {signal.get('confidence', 0):.2f})")
    
    async def _send_signal_alert(self, signal: Dict):
        """Send alert for trading signal"""
        signal_emoji = "🚀" if signal['signal_type'] == 'fresh_trough' else "⚠️"
        
        message = (
            f"{signal_emoji} TRADING SIGNAL: {signal['symbol']}\n"
            f"Type: {signal['signal_type']}\n"
            f"Price: ${signal.get('price', 'N/A')}\n" 
            f"Confidence: {signal.get('confidence', 0):.1%}\n"
            f"Action: {signal.get('action', 'analyze')}"
        )
        
        await self.alert_system.send_alert(
            f"Trading Signal: {signal['symbol']}",
            message,
            priority="high"
        )
    
    async def _broadcast_update(self, data: Dict):
        """Broadcast update to all connected WebSocket clients"""
        if not self.websocket_connections:
            return
        
        message = json.dumps({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **data
        })
        
        # Send to all connected clients
        disconnected = set()
        for websocket in self.websocket_connections:
            try:
                await websocket.send_text(message)
            except:
                disconnected.add(websocket)
        
        # Remove disconnected clients
        self.websocket_connections -= disconnected
    
    async def _save_state(self):
        """Save service state to disk"""
        try:
            state = {
                "active": self.active,
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "last_check": self.last_check.isoformat() if self.last_check else None,
                "check_count": self.check_count,
                "error_count": self.error_count,
                "watchlist": sorted(list(self.watchlist)),
                "current_signals": self.current_signals,
                "config": asdict(self.config)
            }
            
            state_file = self.state_dir / "fastapi_service_state.json"
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2, default=str)
                
        except Exception as e:
            self.logger.error(f"Failed to save state: {e}")
    
    async def _handle_trade_update(self, trade_info: Dict):
        """Handle real-time trade updates from Alpaca streaming"""
        self.logger.warning(f"🔔 TRADE UPDATE: {trade_info['event']} - {trade_info['symbol']}")
        
        # Send desktop notification for order fills
        if trade_info['event'] == 'order_filled':
            await self.desktop_notifications.send_order_fill_alert(
                symbol=trade_info['symbol'],
                side=trade_info['side'],
                quantity=int(trade_info['filled_qty']),
                fill_price=float(trade_info['filled_avg_price'])
            )
        
        # Broadcast to WebSocket clients
        await self._broadcast_update({
            "type": "trade_update",
            **trade_info
        })
        
        # Send alert for order fills
        if trade_info['event'] == 'order_filled':
            await self.alert_system.send_alert(
                f"📊 Order Filled: {trade_info['symbol']}",
                f"{trade_info['side'].upper()} {trade_info['filled_qty']} @ ${trade_info['filled_avg_price']}",
                priority="high"
            )
            
            # Force position update and automatic checking
            if self.position_tracker:
                await self.position_tracker.update_positions()
                
            # Automatically trigger position verification
            await self.check_positions_after_order({"symbol": trade_info['symbol']})
    
    async def _handle_profit_spike(self, spike_info: Dict):
        """Handle real-time profit spike detection"""
        self.logger.warning(f"🚨 PROFIT SPIKE DETECTED: {spike_info['symbol']} +{spike_info['profit_pct']:.2f}%")
        
        # Send desktop notification for profit spike
        await self.desktop_notifications.send_profit_spike_alert(
            symbol=spike_info['symbol'],
            profit_percent=spike_info['profit_pct'],
            current_price=spike_info['current_price'],
            profit_dollar=spike_info.get('profit_dollar', 0)
        )
        
        # Generate JSON profit alert
        profit_alert = {
            "id": f"profit_{spike_info['symbol']}_{int(time.time())}",
            "timestamp": spike_info['timestamp'],
            "event": "PROFIT_SPIKE",
            "symbol": spike_info['symbol'],
            "entry_price": spike_info['entry_price'],
            "current_price": spike_info['current_price'],
            "profit_pct": spike_info['profit_pct'],
            "action": "CONSIDER_EXIT"
        }
        
        # Save to JSON file
        alert_file = self.state_dir / "profit_alerts" / f"{profit_alert['id']}.json"
        alert_file.parent.mkdir(exist_ok=True)
        with open(alert_file, 'w') as f:
            json.dump(profit_alert, f, indent=2)
        
        # Broadcast to all channels
        await self._broadcast_update({
            "type": "profit_alert",
            **profit_alert
        })
        
        await self.alert_system.send_alert(
            f"💰 PROFIT SPIKE: {spike_info['symbol']}",
            f"+{spike_info['profit_pct']:.2f}% profit detected! Current: ${spike_info['current_price']}",
            priority="critical"
        )
    
    async def _handle_market_data(self, data: Dict):
        """Handle real-time market data updates"""
        # Forward to WebSocket clients
        await self._broadcast_update({
            "type": "market_data",
            **data
        })
    
    async def _load_state(self):
        """Load service state from disk"""
        try:
            state_file = self.state_dir / "fastapi_service_state.json"
            if state_file.exists():
                with open(state_file, 'r') as f:
                    state = json.load(f)
                
                self.watchlist = set(state.get('watchlist', []))
                self.current_signals = state.get('current_signals', [])
                self.check_count = state.get('check_count', 0)
                self.error_count = state.get('error_count', 0)
                
                self.logger.info(f"Loaded previous state: {len(self.watchlist)} symbols in watchlist")
                
        except Exception as e:
            self.logger.warning(f"Could not load previous state: {e}")


# Global service instance
monitoring_service = MonitoringServiceAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    # Startup
    await monitoring_service.startup()
    yield
    # Shutdown
    await monitoring_service.shutdown()


# Create FastAPI app
app = FastAPI(
    title="Hybrid Trading Monitoring Service",
    description="Production-ready monitoring service with real-time trading signals and position tracking",
    version="1.0.0",
    lifespan=lifespan
)


# Health and Status Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return await monitoring_service.get_health()


@app.get("/status")
async def get_status():
    """Get detailed service status"""
    status = await monitoring_service.get_status()
    return {
        "active": status.active,
        "start_time": status.start_time.isoformat() if status.start_time else None,
        "last_check": status.last_check.isoformat() if status.last_check else None,
        "watchlist_size": status.watchlist_size,
        "active_positions": status.active_positions,
        "signals_detected_today": status.signals_detected_today,
        "uptime_seconds": status.uptime_seconds,
        "check_count": status.check_count,
        "error_count": status.error_count
    }


@app.get("/hibernation")
async def get_hibernation_status():
    """Get current hibernation status and resource optimization info"""
    return await monitoring_service.get_hibernation_status()


# Watchlist Management
@app.get("/watchlist")
async def get_watchlist():
    """Get current watchlist"""
    return await monitoring_service.get_watchlist()


@app.post("/watchlist/add")
async def add_symbols(request: AddSymbolsRequest):
    """Add symbols to watchlist"""
    return await monitoring_service.add_symbols(request.symbols)


@app.post("/watchlist/remove")
async def remove_symbols(request: RemoveSymbolsRequest):
    """Remove symbols from watchlist"""
    return await monitoring_service.remove_symbols(request.symbols)


@app.post("/watchlist/sync")
async def sync_watchlist_with_scanner(request: ScanSyncRequest):
    """Sync watchlist with active scanner results"""
    scan_params = {
        "min_trades_per_minute": request.min_trades_per_minute,
        "min_percent_change": request.min_percent_change,
        "max_symbols": request.max_symbols,
        "force_update": request.force_update
    }
    return await monitoring_service.sync_with_scanner_results(scan_params)


@app.get("/watchlist/auto-scan")
async def get_auto_scan_status():
    """Get automatic scanning configuration and status"""
    return await monitoring_service.get_auto_scan_status()


@app.post("/watchlist/auto-scan")
async def configure_auto_scan(request: AutoScanConfigRequest):
    """Configure automatic scanning parameters"""
    config = {
        "enabled": request.enabled,
        "interval_seconds": request.interval_seconds,
        "min_trades_per_minute": request.min_trades_per_minute,
        "min_percent_change": request.min_percent_change,
        "max_symbols": request.max_symbols
    }
    return await monitoring_service.configure_auto_scan(config)


# Position Management
@app.get("/positions")
async def get_positions():
    """Get current positions"""
    return await monitoring_service.get_positions()


@app.post("/positions/check")
async def check_positions(request: OrderCheckRequest):
    """Check positions after order"""
    return await monitoring_service.check_positions_after_order(request.order_info)


# Order Management
@app.post("/orders")
async def place_order(request: OrderRequest):
    """Place a stock order using MCP tools"""
    try:
        monitoring_service.logger.info(f"📋 Order request: {request.side.upper()} {request.quantity} {request.symbol} @ ${request.limit_price}")
        
        # Use MCP tool directly
        from ..tools.place_order_tool import place_stock_order
        
        order_result = await place_stock_order(
            symbol=request.symbol,
            side=request.side,
            quantity=request.quantity,
            order_type=request.order_type,
            limit_price=request.limit_price,
            time_in_force=request.time_in_force
        )
        
        if order_result and 'order' in order_result:
            monitoring_service.logger.info(f"✅ Order placed successfully: {order_result['order'].get('id', 'unknown')}")
            return {
                "status": "success",
                "order": order_result['order']
            }
        else:
            monitoring_service.logger.error(f"❌ Order placement failed: {order_result}")
            raise HTTPException(
                status_code=400, 
                detail=f"Order placement failed: {order_result}"
            )
            
    except Exception as e:
        monitoring_service.logger.error(f"❌ Error placing order: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


# Signal Management
@app.get("/signals")
async def get_signals():
    """Get current trading signals"""
    return await monitoring_service.get_signals()


# Streaming Management
@app.get("/streaming/status")
async def get_streaming_status():
    """Get streaming service status"""
    if monitoring_service.streaming_service:
        return await monitoring_service.streaming_service.get_streaming_status()
    else:
        return {
            "is_running": False,
            "error": "Streaming service not initialized",
            "subscribed_symbols": [],
            "tracked_positions": [],
            "position_count": 0
        }


# Trade Confirmation Management
@app.post("/trades/request-confirmation")
async def request_trade_confirmation(request: TradeConfirmationRequest):
    """Request trade confirmation for a new trade"""
    trade_id = await monitoring_service.trade_confirmation.request_trade_confirmation(
        symbol=request.symbol,
        action=request.action,
        quantity=request.quantity,
        expected_price=request.expected_price
    )
    return {"trade_id": trade_id, "status": "confirmation_requested"}


@app.post("/trades/confirm-execution")
async def confirm_trade_execution(request: ConfirmExecutionRequest):
    """Confirm trade execution with actual details"""
    success = await monitoring_service.trade_confirmation.confirm_trade_execution(
        trade_id=request.trade_id,
        actual_price=request.actual_price,
        fill_timestamp=request.fill_timestamp,
        screenshot_path=request.screenshot_path
    )
    return {"success": success, "status": "confirmed" if success else "failed"}


@app.get("/trades/confirmations")
async def get_trade_confirmations():
    """Get pending trade confirmations"""
    return {
        "confirmations": monitoring_service.trade_confirmation.get_pending_confirmations(),
        "history": monitoring_service.trade_confirmation.get_confirmation_history()
    }


@app.get("/trades/confirmations/{trade_id}")
async def get_trade_confirmation(trade_id: str):
    """Get specific trade confirmation"""
    confirmation = monitoring_service.trade_confirmation.get_confirmation(trade_id)
    if confirmation:
        return confirmation
    else:
        raise HTTPException(status_code=404, detail="Trade confirmation not found")


# Desktop Notifications Management  
@app.get("/notifications/status")
async def get_notification_status():
    """Get desktop notification service status"""
    return monitoring_service.desktop_notifications.get_status()


@app.get("/notifications/history")
async def get_notification_history():
    """Get recent notification history"""
    return {
        "notifications": monitoring_service.desktop_notifications.get_notification_history()
    }


# WebSocket endpoint for real-time updates
@app.websocket("/stream")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    monitoring_service.websocket_connections.add(websocket)
    
    try:
        # Send initial status
        await websocket.send_text(json.dumps({
            "type": "connection",
            "status": "connected",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "watchlist_size": len(monitoring_service.watchlist),
            "active_positions": len(monitoring_service.position_tracker.positions) if monitoring_service.position_tracker else 0
        }))
        
        # Keep connection alive
        while True:
            try:
                # Wait for client messages (ping/pong)
                await websocket.receive_text()
            except WebSocketDisconnect:
                break
                
    except WebSocketDisconnect:
        pass
    finally:
        monitoring_service.websocket_connections.discard(websocket)


if __name__ == "__main__":
    uvicorn.run(
        "fastapi_service:app",
        host="0.0.0.0",
        port=8001,
        reload=False,
        log_level="info"
    )