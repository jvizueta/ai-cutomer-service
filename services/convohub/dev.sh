#!/usr/bin/env bash
set -euo pipefail

# Dev helper script for ConvoHub
# - Creates venv if missing
# - Installs requirements if needed
# - Loads .env
# - Runs uvicorn with reload

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${PROJECT_ROOT}/.venv"
REQ_FILE="${PROJECT_ROOT}/requirements.txt"
ENV_FILE="${PROJECT_ROOT}/.env"
APP_PATH="convohub.waha_adapter.main:app"
HOST="0.0.0.0"
PORT="8080"

if [[ ! -f "${REQ_FILE}" ]]; then
  echo "[ERROR] requirements.txt not found at ${REQ_FILE}" >&2
  exit 1
fi

if [[ ! -d "${VENV_DIR}" ]]; then
  echo "[INFO] Creating virtual environment at ${VENV_DIR}";
  python -m venv "${VENV_DIR}";
fi

source "${VENV_DIR}/bin/activate"

# Upgrade pip minimally
python -m pip install --upgrade pip >/dev/null

# Install deps only if something changed (simple hash compare)
CURRENT_HASH_FILE="${VENV_DIR}/.req.hash"
NEW_HASH="$(sha256sum "${REQ_FILE}" | awk '{print $1}')"
NEED_INSTALL=1
if [[ -f "${CURRENT_HASH_FILE}" ]]; then
  OLD_HASH="$(cat "${CURRENT_HASH_FILE}")"
  if [[ "${OLD_HASH}" == "${NEW_HASH}" ]]; then
    NEED_INSTALL=0
  fi
fi
if [[ ${NEED_INSTALL} -eq 1 ]]; then
  echo "[INFO] Installing Python dependencies";
  pip install -r "${REQ_FILE}";
  echo "${NEW_HASH}" > "${CURRENT_HASH_FILE}";
else
  echo "[INFO] Dependencies unchanged; skipping install";
fi

if [[ -f "${ENV_FILE}" ]]; then
  echo "[INFO] Loading environment from ${ENV_FILE}";
  # Export variables while ignoring comments
  export $(grep -v '^#' "${ENV_FILE}" | xargs -d '\n')
else
  echo "[WARN] .env file not found; proceeding without extra env vars";
fi

# Run uvicorn with reload
echo "[INFO] Starting ConvoHub dev server at http://${HOST}:${PORT}";
exec uvicorn "${APP_PATH}" --host "${HOST}" --port "${PORT}" --reload
