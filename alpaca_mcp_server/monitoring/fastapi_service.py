"""Refactored FastAPI-based Hybrid Trading Service

Production-ready monitoring service with clean modular architecture,
REST API, WebSocket streaming, and persistent background monitoring.
"""

import asyncio
import json
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import uvicorn

from .api.routes import api_router, get_monitoring_service
from .api.websockets import websocket_endpoint, websocket_manager
from .api.services import MonitoringServiceAPI


# Global state file path
STATE_FILE = Path(__file__).parent.parent.parent / "monitoring_data" / "fastapi_service_state.json"


def load_state():
    """Load service state from disk"""
    try:
        if STATE_FILE.exists():
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
                logging.info(f"Loaded service state: {len(state.get('watchlist', []))} symbols in watchlist")
                return state
    except Exception as e:
        logging.warning(f"Could not load service state: {e}")
    
    return {
        "watchlist": [],
        "auto_scan_enabled": False,
        "auto_trader_enabled": False,
        "last_saved": None
    }


def save_state(state_data: dict):
    """Save service state to disk"""
    try:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        state_data["last_saved"] = datetime.now().isoformat()
        
        with open(STATE_FILE, 'w') as f:
            json.dump(state_data, f, indent=2)
            
        logging.info(f"Saved service state: {len(state_data.get('watchlist', []))} symbols")
        
    except Exception as e:
        logging.error(f"Could not save service state: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    logging.info("Starting FastAPI Hybrid Trading Monitoring Service...")
    
    # Load persistent state
    state = load_state()
    service = get_monitoring_service()
    service.watchlist = set(state.get("watchlist", []))
    service.auto_scan_enabled = state.get("auto_scan_enabled", False)
    
    # Auto-trader is disabled by default per CLAUDE.md requirements
    if service.auto_trader:
        service.auto_trader.enabled = False
    
    logging.info(f"Service initialized with {len(service.watchlist)} symbols in watchlist")
    logging.info("Auto-trading is DISABLED by default - user must enable manually")
    
    yield
    
    # Shutdown
    logging.info("Shutting down FastAPI service...")
    
    # Save current state
    service = get_monitoring_service()
    current_state = {
        "watchlist": list(service.watchlist),
        "auto_scan_enabled": service.auto_scan_enabled,
        "auto_trader_enabled": getattr(service.auto_trader, 'enabled', False) if service.auto_trader else False
    }
    save_state(current_state)
    
    # Stop monitoring if active
    if service.active:
        await service.stop_monitoring()
    
    logging.info("FastAPI service shutdown complete")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    app = FastAPI(
        title="Alpaca Trading Monitoring Service",
        description="FastAPI-based monitoring service for automated trading",
        version="2.0.0",
        lifespan=lifespan
    )
    
    # Include API routes
    app.include_router(api_router)
    
    # WebSocket endpoint
    @app.websocket("/ws")
    async def websocket_route(websocket: WebSocket):
        await websocket_endpoint(websocket)
    
    # Dashboard endpoint
    @app.get("/dashboard", response_class=HTMLResponse)
    async def dashboard():
        """Simple monitoring dashboard"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Trading Monitor Dashboard</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background-color: #1a1a1a; color: #fff; }
                .container { max-width: 1200px; margin: 0 auto; }
                .status-box { background-color: #2d2d2d; padding: 20px; margin: 10px 0; border-radius: 8px; }
                .symbol { display: inline-block; margin: 5px; padding: 8px 12px; 
                         background-color: #007acc; color: white; border-radius: 4px; }
                .fresh-signal { background-color: #28a745; }
                .stale-signal { background-color: #ffc107; color: black; }
                .error { background-color: #dc3545; }
                button { background-color: #007acc; color: white; border: none; 
                        padding: 10px 15px; margin: 5px; border-radius: 4px; cursor: pointer; }
                button:hover { background-color: #005c99; }
                #log { background-color: #000; color: #0f0; padding: 10px; 
                      font-family: monospace; height: 200px; overflow-y: scroll; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Trading Monitor Dashboard</h1>
                
                <div class="status-box">
                    <h2>Service Status</h2>
                    <div id="service-status">Loading...</div>
                    <button onclick="startService()">Start Monitoring</button>
                    <button onclick="stopService()">Stop Monitoring</button>
                    <button onclick="refreshStatus()">Refresh</button>
                </div>
                
                <div class="status-box">
                    <h2>Watchlist</h2>
                    <div id="watchlist">Loading...</div>
                </div>
                
                <div class="status-box">
                    <h2>Positions</h2>
                    <div id="positions">Loading...</div>
                </div>
                
                <div class="status-box">
                    <h2>Signals</h2>
                    <div id="signals">Loading...</div>
                </div>
                
                <div class="status-box">
                    <h2>Real-time Log</h2>
                    <div id="log"></div>
                </div>
            </div>
            
            <script>
                let ws = null;
                let isConnected = false;
                
                function connectWebSocket() {
                    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                    const wsUrl = `${protocol}//${window.location.host}/ws`;
                    
                    ws = new WebSocket(wsUrl);
                    
                    ws.onopen = function(event) {
                        isConnected = true;
                        addLog('WebSocket connected');
                    };
                    
                    ws.onmessage = function(event) {
                        const data = JSON.parse(event.data);
                        handleWebSocketMessage(data);
                    };
                    
                    ws.onclose = function(event) {
                        isConnected = false;
                        addLog('WebSocket disconnected');
                        setTimeout(connectWebSocket, 5000);
                    };
                    
                    ws.onerror = function(error) {
                        addLog(`WebSocket error: ${error}`);
                    };
                }
                
                function handleWebSocketMessage(data) {
                    addLog(`${data.type}: ${JSON.stringify(data.data || {})}`);
                    
                    if (data.type === 'status_update') {
                        updateServiceStatus(data.data);
                    } else if (data.type === 'position_update') {
                        updatePositions(data.data);
                    } else if (data.type === 'signal_update') {
                        updateSignals(data.data);
                    }
                }
                
                function addLog(message) {
                    const log = document.getElementById('log');
                    const timestamp = new Date().toLocaleTimeString();
                    log.innerHTML += `[${timestamp}] ${message}<br>`;
                    log.scrollTop = log.scrollHeight;
                }
                
                async function refreshStatus() {
                    try {
                        const response = await fetch('/status');
                        const data = await response.json();
                        updateServiceStatus(data);
                        updateWatchlist(data.watchlist);
                        updatePositions(data.positions);
                        updateSignals(data.signals);
                    } catch (error) {
                        addLog(`Error refreshing status: ${error}`);
                    }
                }
                
                function updateServiceStatus(data) {
                    const status = document.getElementById('service-status');
                    const activeText = data.active ? 'ACTIVE' : 'INACTIVE';
                    const uptimeText = data.uptime_seconds ? 
                        `Uptime: ${Math.floor(data.uptime_seconds / 60)}m ${Math.floor(data.uptime_seconds % 60)}s` : '';
                    
                    status.innerHTML = `
                        <strong>Status:</strong> ${activeText}<br>
                        <strong>Check Count:</strong> ${data.check_count || 0}<br>
                        <strong>Error Count:</strong> ${data.error_count || 0}<br>
                        ${uptimeText}
                    `;
                }
                
                function updateWatchlist(data) {
                    const watchlist = document.getElementById('watchlist');
                    if (data && data.symbols) {
                        let html = `<strong>Size:</strong> ${data.size || 0}<br><br>`;
                        data.symbols.forEach(symbol => {
                            const signalClass = symbol.bars_ago <= 11 ? 'fresh-signal' : 'stale-signal';
                            html += `<span class="symbol ${signalClass}">${symbol.symbol} (${symbol.signal_type})</span>`;
                        });
                        watchlist.innerHTML = html;
                    } else {
                        watchlist.innerHTML = 'No watchlist data';
                    }
                }
                
                function updatePositions(data) {
                    const positions = document.getElementById('positions');
                    if (data && data.positions) {
                        let html = `<strong>Count:</strong> ${data.count || 0}<br>`;
                        html += `<strong>Total P&L:</strong> $${(data.total_unrealized_pnl || 0).toFixed(2)}<br><br>`;
                        data.positions.forEach(pos => {
                            const pnl = parseFloat(pos.unrealized_pnl || 0);
                            const pnlClass = pnl >= 0 ? 'fresh-signal' : 'error';
                            html += `<span class="symbol ${pnlClass}">${pos.symbol}: $${pnl.toFixed(2)}</span>`;
                        });
                        positions.innerHTML = html;
                    } else {
                        positions.innerHTML = 'No positions';
                    }
                }
                
                function updateSignals(data) {
                    const signals = document.getElementById('signals');
                    if (data && data.active_signals) {
                        let html = `<strong>Count:</strong> ${data.signal_count || 0}<br><br>`;
                        Object.entries(data.active_signals).forEach(([symbol, signal]) => {
                            html += `<span class="symbol fresh-signal">${symbol}: ${signal.type}</span>`;
                        });
                        signals.innerHTML = html;
                    } else {
                        signals.innerHTML = 'No active signals';
                    }
                }
                
                async function startService() {
                    try {
                        const response = await fetch('/start', { method: 'POST' });
                        const data = await response.json();
                        addLog(`Start service: ${data.message}`);
                        refreshStatus();
                    } catch (error) {
                        addLog(`Error starting service: ${error}`);
                    }
                }
                
                async function stopService() {
                    try {
                        const response = await fetch('/stop', { method: 'POST' });
                        const data = await response.json();
                        addLog(`Stop service: ${data.message}`);
                        refreshStatus();
                    } catch (error) {
                        addLog(`Error stopping service: ${error}`);
                    }
                }
                
                // Initialize
                connectWebSocket();
                refreshStatus();
                setInterval(refreshStatus, 10000); // Refresh every 10 seconds
            </script>
        </body>
        </html>
        """
    
    return app


def run_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Run the FastAPI server"""
    app = create_app()
    uvicorn.run(app, host=host, port=port, reload=reload)


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the server
    run_server(reload=True)