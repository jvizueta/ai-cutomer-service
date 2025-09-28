#!/bin/bash
echo "Starting Lyra development environment..."

# Start lyra service
cd services/lyra && uvicorn app.main:app --reload --port 8000 &

# Start waha-integrator service  
cd services/waha-integrator && uvicorn app.main:app --reload --port 8001 &

echo "Services running:"
echo "- Lyra: http://localhost:8000"
echo "- WAHA Integrator: http://localhost:8001"