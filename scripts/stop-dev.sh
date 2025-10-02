#!/bin/bash

echo "Stopping development services..."

# Kill uvicorn processes running on specific ports
echo "Stopping counter-agent (port 8000)..."
pkill -f "uvicorn.*--port 8000" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✓ counter-agent stopped"
else
    echo "⚠ counter-agent was not running"
fi

echo "Stopping waha-integrator (port 8001)..."
pkill -f "uvicorn.*--port 8001" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✓ waha-integrator stopped"
else
    echo "⚠ waha-integrator was not running"
fi

# Alternative: Kill all uvicorn processes (less specific)
# pkill -f "uvicorn app.main:app"

# Check if any uvicorn processes are still running
remaining=$(pgrep -f "uvicorn" | wc -l)
if [ $remaining -gt 0 ]; then
    echo ""
    echo "⚠ Warning: $remaining uvicorn process(es) still running:"
    ps aux | grep uvicorn | grep -v grep
    echo ""
    echo "To force kill all uvicorn processes, run:"
    echo "  pkill -9 -f uvicorn"
else
    echo ""
    echo "✅ All development services stopped successfully"
fi

# Optional: Check if ports are freed
echo ""
echo "Checking ports..."
if lsof -i:8000 > /dev/null 2>&1; then
    echo "⚠ Port 8000 is still in use"
    lsof -i:8000
else
    echo "✓ Port 8000 is free"
fi

if lsof -i:8001 > /dev/null 2>&1; then
    echo "⚠ Port 8001 is still in use"
    lsof -i:8001
else
    echo "✓ Port 8001 is free"
fi