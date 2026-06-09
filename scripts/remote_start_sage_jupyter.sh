#!/usr/bin/env bash
set -euo pipefail

# remote_start_sage_jupyter.sh
# Usage: remote_start_sage_jupyter.sh [port] [logfile] [tmux_session] [--reverse user@host[:local_port]]
#
# Starts a Sage/Jupyter Notebook on the remote host (bound to 127.0.0.1), writes logs to
# the given logfile and prints the access token. Optionally establishes a reverse SSH
# tunnel back to a reachable host if `--reverse` is given.

PORT="${1:-8888}"
LOG="${2:-$HOME/jupyter.log}"
TMUX_SESSION="${3:-jupyter}"

REVERSE_TARGET=""
if [ "${4:-}" = "--reverse" ]; then
  REVERSE_TARGET="${5:-}"
fi

start_jupyter() {
  if command -v tmux >/dev/null 2>&1; then
    if tmux ls 2>/dev/null | grep -q "^${TMUX_SESSION}:"; then
      echo "tmux session ${TMUX_SESSION} already running."
    else
      tmux new-session -d -s "${TMUX_SESSION}" "exec sage -python -m notebook --no-browser --port=${PORT} --ip=127.0.0.1 > \"${LOG}\" 2>&1"
      echo "Started Jupyter in tmux session ${TMUX_SESSION} (port ${PORT})."
    fi
  else
    nohup sage -python -m notebook --no-browser --port=${PORT} --ip=127.0.0.1 > "${LOG}" 2>&1 &
    echo $! > "$HOME/.jupyter_pid"
    echo "Started Jupyter with nohup (pid $(cat "$HOME/.jupyter_pid"))."
  fi
}

extract_token() {
  if [ ! -f "${LOG}" ]; then
    return 1
  fi
  grep -Po "http://(?:127\\.0\\.0\\.1|localhost):${PORT}/\\?token=\\K[^[:space:]]+" "${LOG}" 2>/dev/null | head -n1 || true
}

start_jupyter

echo "Waiting for Jupyter token in ${LOG}..."
TOKEN=""
for i in $(seq 1 30); do
  TOKEN=$(extract_token)
  if [ -n "${TOKEN}" ]; then
    break
  fi
  sleep 0.5
done

if [ -n "${TOKEN}" ]; then
  echo "Jupyter token: ${TOKEN}"
else
  echo "Token not found. Check ${LOG} (last 50 lines):"
  tail -n 50 "${LOG}"
fi

if [ -n "${REVERSE_TARGET}" ]; then
  # REVERSE_TARGET format: user@host[:local_port]
  if echo "${REVERSE_TARGET}" | grep -q ":"; then
    USER_HOST="${REVERSE_TARGET%:*}"
    LOCAL_PORT="${REVERSE_TARGET##*:}"
  else
    USER_HOST="${REVERSE_TARGET}"
    LOCAL_PORT="${PORT}"
  fi
  echo "Attempting reverse tunnel to ${USER_HOST} (local port ${LOCAL_PORT})..."
  ssh -f -N -o ServerAliveInterval=60 -o ServerAliveCountMax=3 -R "${LOCAL_PORT}:localhost:${PORT}" "${USER_HOST}" && echo "Reverse tunnel established." || echo "Reverse tunnel failed (check SSH access from this host to ${USER_HOST})."
fi

echo
echo "Logs: ${LOG}"
echo "If you prefer a local forward instead, run on your local machine:"
echo "  ssh -f -N -L ${PORT}:localhost:${PORT} youruser@$(hostname -s)"
echo "Then open http://localhost:${PORT}/?token=<the-token-above> in your browser."
