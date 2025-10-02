#!/bin/bash
echo "Starting waha-integrator development environment..."

# Start waha-integrator service in its virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment for waha-integrator..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001