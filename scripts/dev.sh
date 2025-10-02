#!/bin/bash
echo "Starting counter-agent development environment..."

# Start counter-agent service in its virtual environment
cd ../services/counter-agent
if [ ! -d "venv" ]; then
    echo "Creating virtual environment for counter-agent..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &

# Start waha-integrator service in its virtual environment
cd ../services/waha-integrator
if [ ! -d "venv" ]; then
    echo "Creating virtual environment for waha-integrator..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001 &

echo "Services running:"
echo "- counter-agent: http://localhost:8000"
echo "- WAHA Integrator: http://localhost:8001"
echo ""
echo "To stop services, run: pkill -f uvicorn"