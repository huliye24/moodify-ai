#!/usr/bin/env bash
set -euo pipefail

REMOTE_ROOT="${1:-$HOME/moodify-ear-remote}"
REPO_ROOT="$REMOTE_ROOT/repo"
UNIT_DIR="$HOME/.config/systemd/user"
ENV_DIR="$HOME/.config/moodify-ear"
UNIT_PATH="$UNIT_DIR/moodify-ear-batch.service"

mkdir -p "$UNIT_DIR" "$ENV_DIR" "$REMOTE_ROOT/logs"
chmod 700 "$ENV_DIR"
if [[ ! -f "$ENV_DIR/codex.env" ]]; then
  umask 077
  cat >"$ENV_DIR/codex.env" <<'EOF'
# Worker tuning only. Authentication is established separately with:
# codex login --device-auth
MAX_TASK_SECONDS=7200
IDLE_SECONDS=30
EOF
fi
chmod 600 "$ENV_DIR/codex.env"

cat >"$UNIT_PATH" <<EOF
[Unit]
Description=Moodify Ear v1 unattended Codex task worker
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=$REPO_ROOT
EnvironmentFile=-$ENV_DIR/codex.env
ExecStart=/usr/bin/env bash $REPO_ROOT/ops/ear_batch/remote/remote_worker.sh $REMOTE_ROOT
Restart=on-failure
RestartSec=20
TimeoutStopSec=45
UMask=0077
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable moodify-ear-batch.service
printf 'installed %s\n' "$UNIT_PATH"
printf 'start with: systemctl --user start moodify-ear-batch.service\n'
