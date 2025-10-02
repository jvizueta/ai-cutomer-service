#!/bin/bash
echo "Starting counter-agent development environment..."

# Start counter-agent service in its virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment for counter-agent..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000