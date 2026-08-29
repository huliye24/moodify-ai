#!/usr/bin/env bash
set -euo pipefail

STAMP="${STAMP:-$(date -u +%Y%m%dT%H%M%SZ)}"
CONFIG_SOURCE="${CONFIG_SOURCE:-$(cd "$(dirname "$0")" && pwd)/nginx/moodify-sites.conf}"

fetch_site() {
  local domain="$1"
  local release="/var/www/$domain/releases/$STAMP"
  install -d "$release"
  curl --retry 5 --retry-delay 2 -fsSL "https://$domain/" -o "$release/index.html"
  while IFS= read -r asset; do
    [[ -n "$asset" ]] || continue
    install -d "$release/$(dirname "$asset")"
    curl --retry 5 --retry-delay 2 -fsSL "https://$domain/$asset" -o "$release/$asset"
  done < <(grep -Eo '(src|href)="\./[^"]+"' "$release/index.html" | cut -d'"' -f2 | sed 's#^\./##' | sort -u)
  find "$release" -type f -exec chmod 0644 {} +
  ln -sfn "$release" "/var/www/$domain/current"
}

fetch_site rongjingmusic.com
fetch_site rongjingwenchuan.com
install -m 0644 "$CONFIG_SOURCE" /etc/nginx/sites-available/moodify-sites
rm -f /etc/nginx/sites-enabled/default
ln -sfn /etc/nginx/sites-available/moodify-sites /etc/nginx/sites-enabled/moodify-sites
nginx -t
systemctl enable nginx
systemctl reload nginx
printf 'deployed release=%s\n' "$STAMP"
