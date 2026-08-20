#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${REPO_ROOT:-/opt/moodify}"
OPS_SRC="${OPS_SRC:-$REPO_ROOT/ops/data_node}"
UNIT_SRC="${UNIT_SRC:-$REPO_ROOT/ops/data_node/systemd}"
MOODIFY_USER="${MOODIFY_USER:-moodify}"
MOODIFY_GROUP="${MOODIFY_GROUP:-moodify}"

echo "[1/7] Verify existing worker"
command -v systemctl >/dev/null
test -x "$REPO_ROOT/.venv/bin/moodify-node"
test -d "$OPS_SRC"

echo "[2/7] Create durable directories"
install -d -o "$MOODIFY_USER" -g "$MOODIFY_GROUP" \
  /var/lib/moodify/staging \
  /var/lib/moodify/inbox \
  /var/lib/moodify/sources \
  /var/lib/moodify/data_factory \
  /var/lib/moodify/ops \
  /var/lib/moodify/reports
install -d -o root -g root /var/backups/moodify

echo "[3/7] Conservative swap policy"
cat >/etc/sysctl.d/99-moodify-low-resource.conf <<'EOF'
vm.swappiness=10
EOF
sysctl --system >/dev/null || true

echo "[4/7] Install systemd units"
install -m 0644 "$UNIT_SRC/moodify-inbox-ingest.service" /etc/systemd/system/
install -m 0644 "$UNIT_SRC/moodify-inbox-ingest.timer" /etc/systemd/system/
install -m 0644 "$UNIT_SRC/moodify-resource-probe.service" /etc/systemd/system/
install -m 0644 "$UNIT_SRC/moodify-resource-probe.timer" /etc/systemd/system/
install -m 0644 "$UNIT_SRC/moodify-daily-report.service" /etc/systemd/system/
install -m 0644 "$UNIT_SRC/moodify-daily-report.timer" /etc/systemd/system/
install -m 0644 "$UNIT_SRC/moodify-metadata-backup.service" /etc/systemd/system/
install -m 0644 "$UNIT_SRC/moodify-metadata-backup.timer" /etc/systemd/system/

install -d /etc/systemd/system/moodify-data-worker.service.d
install -m 0644 "$UNIT_SRC/moodify-data-worker.service.d/10-24x7.conf" \
  /etc/systemd/system/moodify-data-worker.service.d/10-24x7.conf

echo "[5/7] Reload and enable"
systemctl daemon-reload
systemctl enable --now moodify-data-worker.service
systemctl enable --now moodify-inbox-ingest.timer
systemctl enable --now moodify-resource-probe.timer
systemctl enable --now moodify-daily-report.timer
systemctl enable --now moodify-metadata-backup.timer

echo "[6/7] Smoke oneshot services"
systemctl start moodify-resource-probe.service
systemctl start moodify-inbox-ingest.service
systemctl start moodify-daily-report.service
systemctl start moodify-metadata-backup.service

echo "[7/7] Status"
systemctl --no-pager --full status moodify-data-worker.service || true
systemctl list-timers --all | grep moodify || true
free -h
df -h /var/lib/moodify

echo "MFY-24X7-DATA-PIPELINE-001 install complete."
