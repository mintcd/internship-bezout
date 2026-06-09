#!/usr/bin/env bash
set -euo pipefail

# local_start_and_forward.sh
# Usage: local_start_and_forward.sh [user@]host [remote_port] [local_port]
# If only a host is provided, the script will try to detect the username from
# your SSH config (`ssh -G host`) and fall back to the embedded default.

# Embedded default username (update this if your account differs)
DEFAULT_USER="chau"

# Accept either `user@host` or just `host`
ARG1="${1:-}"
if [ -z "${ARG1}" ]; then
  echo "Usage: $0 [user@]host [remote_port] [local_port]"
  exit 2
fi

if [[ "${ARG1}" == *@* ]]; then
  REMOTE="${ARG1}"
else
  HOST="${ARG1}"
  DETECTED_USER=$(ssh -G "${HOST}" 2>/dev/null | awk '/^user /{print $2; exit}') || DETECTED_USER=""
  if [ -n "${DETECTED_USER}" ]; then
    USERNAME="${DETECTED_USER}"
  else
    USERNAME="${DEFAULT_USER}"
  fi
  REMOTE="${USERNAME}@${HOST}"
fi

REMOTE_PORT="${2:-8888}"
LOCAL_PORT="${3:-${REMOTE_PORT}}"
REMOTE_SCRIPT_LOCAL_DIR="$(cd "$(dirname "$0")" && pwd)"
REMOTE_SCRIPT_NAME="remote_start_sage_jupyter.sh"
REMOTE_SCRIPT_REMOTE_PATH="~/bin/${REMOTE_SCRIPT_NAME}"
REMOTE_LOG="~/jupyter.log"
TMUX_SESSION="jupyter"

echo "Ensuring remote helper is installed on ${REMOTE}..."
if ! ssh "${REMOTE}" "test -x ${REMOTE_SCRIPT_REMOTE_PATH}" >/dev/null 2>&1; then
  mkdir -p "${REMOTE_SCRIPT_LOCAL_DIR}"
  scp "${REMOTE_SCRIPT_LOCAL_DIR}/${REMOTE_SCRIPT_NAME}" "${REMOTE}:${REMOTE_SCRIPT_REMOTE_PATH%/*}/"
  ssh "${REMOTE}" "chmod +x ${REMOTE_SCRIPT_REMOTE_PATH}"
  echo "Copied helper to ${REMOTE}:${REMOTE_SCRIPT_REMOTE_PATH}"
else
  echo "Remote helper already present."
fi

echo "Starting Jupyter on ${REMOTE} (port ${REMOTE_PORT})..."
ssh "${REMOTE}" "${REMOTE_SCRIPT_REMOTE_PATH} ${REMOTE_PORT} ${REMOTE_LOG} ${TMUX_SESSION}" || true

echo "Establishing local SSH tunnel ${LOCAL_PORT} -> ${REMOTE}:localhost:${REMOTE_PORT} (background)..."
ssh -f -N -L ${LOCAL_PORT}:localhost:${REMOTE_PORT} "${REMOTE}" || { echo "Failed to create SSH tunnel"; exit 2; }

echo "Fetching token from remote log..."
TOKEN=$(ssh "${REMOTE}" "grep -Po 'http://(?:127\\.0\\.0\\.1|localhost):${REMOTE_PORT}/\\?token=\\K[^[:space:]]+' ${REMOTE_LOG} 2>/dev/null | head -n1 || true") || true

if [ -n "${TOKEN}" ]; then
  echo "Open in your local browser: http://localhost:${LOCAL_PORT}/?token=${TOKEN}"
else
  echo "Token not yet available. Check remote log: ${REMOTE}:${REMOTE_LOG}"
fi
