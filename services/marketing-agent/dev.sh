#!/usr/bin/env bash
set -euo pipefail

# Development helper for marketing-agent (Rasa)
# Creates/activates a virtual environment, installs deps, trains model if needed, then runs Rasa servers.

PYTHON_BIN=${PYTHON_BIN:-python3}
VE_DIR=.venv
PORT=${PORT:-8002}
ACTIONS_PORT=${ACTIONS_PORT:-5055}

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "[ERROR] Python executable '$PYTHON_BIN' not found. Set PYTHON_BIN=python3.10 if using pyenv or system install." >&2
PYTHON_BIN=${PYTHON_BIN:-python3}
PY_VERSION=$($PYTHON_BIN -c 'import sys; print("%d.%d"%sys.version_info[:2])') || true
REQUIRED_MAX_MINOR=10
REQUIRED_MIN_MAJOR=3
REQUIRED_MAX_MAJOR=3
if [[ "$PY_VERSION" =~ ^3\.11 || "$PY_VERSION" =~ ^3\.12 || "$PY_VERSION" =~ ^3\.13 ]]; then
  echo "[dev.sh] Detected Python $PY_VERSION. Rasa 3.6.20 requires Python >=3.8,<3.11."
  if command -v python3.10 >/dev/null 2>&1; then
    echo "[dev.sh] Using python3.10 to create virtual environment."
    PY_CMD=python3.10
  else
    echo "[dev.sh] python3.10 not found. Please install Python 3.10 (e.g., via pyenv or apt) and rerun."
    echo "[dev.sh] Example (Ubuntu): sudo apt-get update && sudo apt-get install -y python3.10 python3.10-venv"
    exit 1
  fi
else
  PY_CMD=$PYTHON_BIN
fi

fi

PY_VERSION=$($PYTHON_BIN -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')
echo "Using Python $PY_VERSION ($PYTHON_BIN)"

if [ ! -d "$VE_DIR" ]; then
  echo "Creating virtual environment ($VE_DIR)..."
  $PYTHON_BIN -m venv "$VE_DIR"
fi

# shellcheck disable=SC1091
  "$PY_CMD" -m venv "$VE_DIR"

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing dependencies..."
pip install -r requirements.txt

  "$PY_CMD" -m pip install --upgrade pip
  "$PY_CMD" -m pip install -r requirements.txt
  touch "$VE_DIR/.deps-installed"
else
  echo "Existing model found, skipping training. Force retrain with: rasa train"
fi

echo "Starting Rasa HTTP server (port $PORT) and action server (port $ACTIONS_PORT)..."
# Run both; if you want logs separated open two terminals instead.
rasa run --enable-api --port "$PORT" --cors "*" &
RASA_PID=$!
rasa run actions --port "$ACTIONS_PORT" --cors "*" --debug &
ACTIONS_PID=$!

echo "Servers started. REST endpoint: http://localhost:$PORT/webhooks/rest/webhook"
echo "Stop with Ctrl+C"

trap 'echo "Stopping..."; kill $RASA_PID $ACTIONS_PID 2>/dev/null; wait $RASA_PID $ACTIONS_PID 2>/dev/null || true' INT TERM
wait