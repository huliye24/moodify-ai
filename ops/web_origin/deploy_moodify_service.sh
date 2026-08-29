#!/usr/bin/env bash
set -euo pipefail

archive=${1:?usage: deploy_moodify_service.sh RELEASE_ARCHIVE}
test -f "$archive"
release=$(date -u +%Y%m%dT%H%M%SZ)
release_dir="/opt/moodify/releases/$release"

missing=()
command -v ffmpeg >/dev/null || missing+=(ffmpeg)
python3 -c 'import venv, ensurepip' >/dev/null 2>&1 || missing+=(python3-venv)
if ((${#missing[@]})); then
  apt-get update
  apt-get install -y "${missing[@]}"
fi
id moodify >/dev/null 2>&1 || useradd --system --home /var/lib/moodify --shell /usr/sbin/nologin moodify
install -d -o moodify -g moodify /var/lib/moodify/state /var/lib/moodify/data_factory
install -d /opt/moodify/releases /etc/moodify
mkdir -p "$release_dir"
tar -xzf "$archive" -C "$release_dir"

if [[ ! -x /opt/moodify/venv/bin/python ]] || ! /opt/moodify/venv/bin/python -m pip --version >/dev/null 2>&1; then
  rm -rf /opt/moodify/venv
  python3 -m venv /opt/moodify/venv
fi
/opt/moodify/venv/bin/pip install --upgrade pip
/opt/moodify/venv/bin/pip install "$release_dir/moodify-core-package"
ln -sfn "$release_dir" /opt/moodify/current

install -m 0644 "$release_dir/ops/web_origin/node.env.example" /etc/moodify/node.env
install -m 0644 "$release_dir/ops/web_origin/systemd/moodify-api.service" /etc/systemd/system/moodify-api.service
install -m 0644 "$release_dir/ops/web_origin/systemd/moodify-worker.service" /etc/systemd/system/moodify-worker.service
install -m 0644 "$release_dir/ops/web_origin/nginx/moodify-api-limits.conf" /etc/nginx/conf.d/moodify-api-limits.conf
install -m 0644 "$release_dir/ops/web_origin/nginx/moodify-sites.conf" /etc/nginx/sites-available/moodify-sites
install -m 0644 "$release_dir/ops/web_origin/site/rongjingmusic/app-workspace.js" /var/www/rongjingmusic.com/current/app-workspace.js

nginx -t
systemctl daemon-reload
systemctl enable moodify-api moodify-worker
systemctl restart moodify-api moodify-worker
systemctl reload nginx
systemctl is-active moodify-api moodify-worker nginx cloudflared-moodify
