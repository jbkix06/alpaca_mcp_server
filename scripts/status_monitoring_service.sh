#!/bin/bash
# Check FastAPI Monitoring Service Status
# Comprehensive status check for the trading signal monitoring service

set -e

# Configuration
SERVICE_PORT="8001"
PID_FILE="monitoring_service.pid"
LOG_DIR="logs"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}📊 FastAPI Monitoring Service Status${NC}"
echo "=================================================="

# Check PID file
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    echo -e "${BLUE}PID File:${NC} Found ($PID)"
    
    # Check if process is running
    if ps -p "$PID" > /dev/null 2>&1; then
        echo -e "${GREEN}Process Status:${NC} Running ✅"
        
        # Get process info
        echo -e "${BLUE}Process Info:${NC}"
        ps -p "$PID" -o pid,ppid,cmd,etime,pcpu,pmem --no-headers | while read line; do
            echo "  $line"
        done
    else
        echo -e "${RED}Process Status:${NC} Not running ❌ (stale PID file)"
    fi
else
    echo -e "${YELLOW}PID File:${NC} Not found"
    
    # Check for any uvicorn processes
    UVICORN_PIDS=$(pgrep -f "uvicorn.*fastapi_service" 2>/dev/null || true)
    if [ -n "$UVICORN_PIDS" ]; then
        echo -e "${YELLOW}Process Status:${NC} Found orphaned processes:"
        for pid in $UVICORN_PIDS; do
            ps -p "$pid" -o pid,ppid,cmd,etime --no-headers
        done
    else
        echo -e "${RED}Process Status:${NC} Not running ❌"
    fi
fi

echo ""

# Check port status
echo -e "${BLUE}Port Status:${NC}"
if lsof -Pi :$SERVICE_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${GREEN}Port $SERVICE_PORT:${NC} In use ✅"
    lsof -Pi :$SERVICE_PORT -sTCP:LISTEN | head -2
else
    echo -e "${RED}Port $SERVICE_PORT:${NC} Not in use ❌"
fi

echo ""

# Test HTTP endpoints
echo -e "${BLUE}Service Endpoints:${NC}"
BASE_URL="http://localhost:$SERVICE_PORT"

# Test health endpoint
echo -n "Health Check: "
if curl -s -f "$BASE_URL/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Responding${NC}"
    
    # Get health data
    echo -e "${CYAN}Health Details:${NC}"
    curl -s "$BASE_URL/health" | python -m json.tool 2>/dev/null | sed 's/^/  /'
else
    echo -e "${RED}❌ Not responding${NC}"
fi

echo ""

# Test status endpoint
echo -n "Status Check: "
if curl -s -f "$BASE_URL/status" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Responding${NC}"
    
    # Get status data
    echo -e "${CYAN}Status Details:${NC}"
    curl -s "$BASE_URL/status" | python -m json.tool 2>/dev/null | sed 's/^/  /'
else
    echo -e "${RED}❌ Not responding${NC}"
fi

echo ""

# Test watchlist endpoint
echo -n "Watchlist Check: "
if curl -s -f "$BASE_URL/watchlist" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Responding${NC}"
    
    # Get watchlist data
    echo -e "${CYAN}Watchlist Details:${NC}"
    curl -s "$BASE_URL/watchlist" | python -m json.tool 2>/dev/null | sed 's/^/  /'
else
    echo -e "${RED}❌ Not responding${NC}"
fi

echo ""

# Check recent logs
echo -e "${BLUE}Recent Logs:${NC}"
if [ -f "$LOG_DIR/monitoring_service.log" ]; then
    echo -e "${CYAN}Last 10 log entries:${NC}"
    tail -10 "$LOG_DIR/monitoring_service.log" | sed 's/^/  /'
else
    echo -e "${YELLOW}No log file found${NC}"
fi

echo ""

# Service URLs
echo -e "${BLUE}Service URLs:${NC}"
if curl -s -f "$BASE_URL/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Service is accessible at:${NC}"
    echo "  • Health: $BASE_URL/health"
    echo "  • Status: $BASE_URL/status"
    echo "  • Watchlist: $BASE_URL/watchlist"
    echo "  • Positions: $BASE_URL/positions"
    echo "  • Signals: $BASE_URL/signals"
    echo "  • API Docs: $BASE_URL/docs"
    echo "  • WebSocket: ws://localhost:$SERVICE_PORT/stream"
else
    echo -e "${RED}❌ Service is not accessible${NC}"
fi

echo ""

# Quick actions
echo -e "${BLUE}Quick Actions:${NC}"
echo "  • Start service: ./scripts/start_monitoring_service.sh"
echo "  • Stop service: ./scripts/stop_monitoring_service.sh"
echo "  • View logs: tail -f $LOG_DIR/monitoring_service.log"
echo "  • Test health: curl $BASE_URL/health"

# Overall status summary
echo ""
if curl -s -f "$BASE_URL/health" > /dev/null 2>&1; then
    echo -e "${GREEN}🎉 Overall Status: Service is running and healthy!${NC}"
else
    echo -e "${RED}⚠️  Overall Status: Service is not responding${NC}"
    if [ -f "$PID_FILE" ]; then
        echo "Try restarting the service with ./scripts/stop_monitoring_service.sh && ./scripts/start_monitoring_service.sh"
    else
        echo "Start the service with ./scripts/start_monitoring_service.sh"
    fi
fi