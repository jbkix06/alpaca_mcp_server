#!/bin/bash
# Start FastAPI Monitoring Service
# Production-ready trading signal monitoring with REST API

set -e

# Configuration
SERVICE_HOST="0.0.0.0"
SERVICE_PORT="8001"
SERVICE_MODULE="alpaca_mcp_server.monitoring.fastapi_service:app"
LOG_DIR="logs"
PID_FILE="monitoring_service.pid"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting FastAPI Monitoring Service${NC}"
echo "=================================================="

# Create logs directory
mkdir -p "$LOG_DIR"

# Check if service is already running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Service already running with PID $PID${NC}"
        echo "Use ./scripts/stop_monitoring_service.sh to stop it first"
        exit 1
    else
        echo -e "${YELLOW}⚠️  Stale PID file found, removing...${NC}"
        rm -f "$PID_FILE"
    fi
fi

# Check dependencies
echo -e "${BLUE}📋 Checking dependencies...${NC}"
python -c "import fastapi, uvicorn" 2>/dev/null || {
    echo -e "${RED}❌ Missing dependencies. Installing...${NC}"
    uv add fastapi uvicorn websockets
}

# Check if port is available
if lsof -Pi :$SERVICE_PORT -sTCP:LISTEN -t >/dev/null; then
    echo -e "${RED}❌ Port $SERVICE_PORT is already in use${NC}"
    echo "Please check what's running on port $SERVICE_PORT:"
    lsof -Pi :$SERVICE_PORT -sTCP:LISTEN
    exit 1
fi

echo -e "${GREEN}✅ Port $SERVICE_PORT is available${NC}"

# Start the service
echo -e "${BLUE}🎯 Starting service on http://$SERVICE_HOST:$SERVICE_PORT${NC}"
echo "Module: $SERVICE_MODULE"
echo "Logs: $LOG_DIR/monitoring_service.log"

# Start uvicorn in background
nohup python -m uvicorn "$SERVICE_MODULE" \
    --host "$SERVICE_HOST" \
    --port "$SERVICE_PORT" \
    --reload \
    --log-level info \
    --access-log \
    > "$LOG_DIR/monitoring_service.log" 2>&1 &

# Save PID
echo $! > "$PID_FILE"
PID=$(cat "$PID_FILE")

# Wait a moment for startup
sleep 3

# Check if service started successfully
if ps -p "$PID" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Service started successfully!${NC}"
    echo "PID: $PID"
    echo ""
    echo -e "${BLUE}📊 Service Information:${NC}"
    echo "  • Health Check: http://localhost:$SERVICE_PORT/health"
    echo "  • Status: http://localhost:$SERVICE_PORT/status"
    echo "  • Watchlist: http://localhost:$SERVICE_PORT/watchlist"
    echo "  • Positions: http://localhost:$SERVICE_PORT/positions"
    echo "  • Signals: http://localhost:$SERVICE_PORT/signals"
    echo "  • API Docs: http://localhost:$SERVICE_PORT/docs"
    echo "  • WebSocket: ws://localhost:$SERVICE_PORT/stream"
    echo ""
    echo -e "${BLUE}📝 Quick Commands:${NC}"
    echo "  • Check health: curl http://localhost:$SERVICE_PORT/health"
    echo "  • View logs: tail -f $LOG_DIR/monitoring_service.log"
    echo "  • Stop service: ./scripts/stop_monitoring_service.sh"
    echo ""
    
    # Test health endpoint
    echo -e "${BLUE}🔍 Testing health endpoint...${NC}"
    sleep 2
    if curl -s "http://localhost:$SERVICE_PORT/health" > /dev/null; then
        echo -e "${GREEN}✅ Health check passed${NC}"
        
        # Show initial status
        echo -e "${BLUE}📈 Initial Status:${NC}"
        curl -s "http://localhost:$SERVICE_PORT/health" | python -m json.tool 2>/dev/null || echo "Status check failed"
    else
        echo -e "${YELLOW}⚠️  Health check failed, but service may still be starting...${NC}"
    fi
    
else
    echo -e "${RED}❌ Failed to start service${NC}"
    echo "Check logs: cat $LOG_DIR/monitoring_service.log"
    rm -f "$PID_FILE"
    exit 1
fi

echo ""
echo -e "${GREEN}🎉 FastAPI Monitoring Service is now running!${NC}"
echo "Monitor the logs with: tail -f $LOG_DIR/monitoring_service.log"