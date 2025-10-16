#!/usr/bin/env bash
set -euo pipefail

if [ ! -d "models" ]; then
  echo "[entrypoint] Training initial model..."
  rasa train
fi

# Run Rasa server and action server
rasa run --enable-api --port ${PORT:-8002} --cors "*" &
RASA_PID=$!
rasa run actions --port ${ACTIONS_PORT:-5055} --cors "*" --debug &
ACTIONS_PID=$!

trap 'echo "[entrypoint] Shutting down"; kill $RASA_PID $ACTIONS_PID; wait $RASA_PID $ACTIONS_PID' SIGINT SIGTERM

wait $RASA_PID $ACTIONS_PID
