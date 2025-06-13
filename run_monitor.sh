#!/bin/bash

# Check if required environment variables are set
if [ -z "$APCA_API_KEY_ID" ] || [ -z "$APCA_API_SECRET_KEY" ]; then
    echo "Error: Alpaca API credentials not set in environment"
    echo "Please set APCA_API_KEY_ID and APCA_API_SECRET_KEY"
    exit 1
fi

# Function to handle script termination
cleanup() {
    echo "Stopping stock monitor..."
    exit 0
}

# Function to run the analysis
run_analysis() {
    ./stock_analyzer --list ~/autotrade/combined.lis
    return $?
}

# Set up trap for clean exit
trap cleanup SIGINT SIGTERM

# Execute immediately on startup
run_analysis

# Main loop
while true; do
    sleep 60
    run_analysis
done
