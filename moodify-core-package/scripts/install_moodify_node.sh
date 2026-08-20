#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="${1:-/opt/moodify}"
SERVICE_USER="${MOODIFY_SERVICE_USER:-moodify}"
STATE_DIR="${MOODIFY_NODE_STATE_DIR:-/var/lib/moodify}"

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run as root (sudo)." >&2
  exit 2
fi

if command -v apt-get >/dev/null 2>&1; then
  apt-get update
  apt-get install -y python3 python3-venv python3-pip ffmpeg git
elif command -v dnf >/dev/null 2>&1; then
  dnf install -y python3 python3-pip ffmpeg git || true
elif command -v yum >/dev/null 2>&1; then
  yum install -y python3 python3-pip ffmpeg git || true
else
  echo "Unsupported package manager. Install Python 3, pip, git and ffmpeg manually." >&2
  exit 3
fi

command -v ffmpeg >/dev/null || { echo "ffmpeg is required" >&2; exit 4; }
command -v ffprobe >/dev/null || { echo "ffprobe is required" >&2; exit 4; }

python3 - <<'PYVER'
import sys
if sys.version_info < (3, 10):
    raise SystemExit(f"Moodify requires Python >=3.10; found {sys.version.split()[0]}")
print("Python", sys.version.split()[0])
PYVER

if ! id "${SERVICE_USER}" >/dev/null 2>&1; then
  useradd --system --create-home --shell /usr/sbin/nologin "${SERVICE_USER}"
fi

mkdir -p "${STATE_DIR}/inbox" "${STATE_DIR}/data_factory"
chown -R "${SERVICE_USER}:${SERVICE_USER}" "${STATE_DIR}"

if [[ ! -d "${REPO_DIR}/.git" ]]; then
  echo "Repository must already be cloned at ${REPO_DIR}; installer will not guess credentials or overwrite it." >&2
  exit 5
fi

python3 -m venv "${REPO_DIR}/.venv"
"${REPO_DIR}/.venv/bin/pip" install --upgrade pip
"${REPO_DIR}/.venv/bin/pip" install -e "${REPO_DIR}/moodify-core-package[node]"
chown -R "${SERVICE_USER}:${SERVICE_USER}" "${REPO_DIR}/.venv"

echo "Base node dependencies installed. Install systemd unit separately after reviewing paths."
