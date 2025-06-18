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


class AddSymbolsRequest(BaseModel):
    symbols: List[str] = Field(..., description="List of stock symbols to add")


class RemoveSymbolsRequest(BaseModel):
    symbols: List[str] = Field(..., description="List of stock symbols to remove")


class OrderCheckRequest(BaseModel):
    order_info: Optional[Dict] = Field(None, description="Order information for tracking")


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
        
        # Components
        self.position_tracker: Optional[PositionTracker] = None
        self.signal_detector: Optional[SignalDetector] = None
        self.alert_system: Optional[AlertSystem] = None
        self.streaming_service: Optional[AlpacaStreamingService] = None
        self.desktop_notifications: Optional[DesktopNotificationService] = None
        self.trade_confirmation: Optional[TradeConfirmationService] = None
        
        # Monitoring state
        self.watchlist: Set[str] = set()
        self.current_signals: List[Dict] = []
        self.signal_history: List[Dict] = []
        self.monitoring_task: Optional[asyncio.Task] = None
        
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
        
        return {
            "status": "success",
            "removed": removed,
            "watchlist_size": len(self.watchlist),
            "current_watchlist": sorted(list(self.watchlist))
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


# Position Management
@app.get("/positions")
async def get_positions():
    """Get current positions"""
    return await monitoring_service.get_positions()


@app.post("/positions/check")
async def check_positions(request: OrderCheckRequest):
    """Check positions after order"""
    return await monitoring_service.check_positions_after_order(request.order_info)


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
        "pending": monitoring_service.trade_confirmation.get_pending_confirmations(),
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