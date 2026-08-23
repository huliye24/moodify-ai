#!/usr/bin/env bash
# W01-P00 read-only Linux node scan.
# Designed to avoid modifying the host. Review before execution.
# DO NOT run with sudo unless your operator policy explicitly allows read-only sudo.

set -u

section() {
  printf '\n\n===== %s =====\n' "$1"
}

safe_cmd() {
  printf '\n$ %s\n' "$*"
  "$@" 2>&1 || true
}

section "TIMESTAMP"
safe_cmd date -Is

section "HOST"
safe_cmd hostname
safe_cmd uname -a
if command -v hostnamectl >/dev/null 2>&1; then safe_cmd hostnamectl; fi
if [ -r /etc/os-release ]; then cat /etc/os-release; fi

section "UPTIME"
safe_cmd uptime

section "CPU"
if command -v lscpu >/dev/null 2>&1; then safe_cmd lscpu; fi
safe_cmd getconf _NPROCESSORS_ONLN

section "MEMORY"
if command -v free >/dev/null 2>&1; then safe_cmd free -h; fi
if [ -r /proc/meminfo ]; then grep -E 'MemTotal|MemAvailable|SwapTotal|SwapFree' /proc/meminfo || true; fi

section "FILESYSTEM"
safe_cmd df -hT
safe_cmd df -ih

section "NETWORK LISTENERS"
if command -v ss >/dev/null 2>&1; then safe_cmd ss -lntup; fi

section "PROCESSES"
safe_cmd ps -eo pid,ppid,user,lstart,etime,comm,args --sort=comm

section "SYSTEMD RUNNING SERVICES"
if command -v systemctl >/dev/null 2>&1; then
  safe_cmd systemctl list-units --type=service --state=running --no-pager
  safe_cmd systemctl list-timers --all --no-pager
fi

section "CRON LOCATIONS"
# Listing only. No crontab modification.
for f in /etc/crontab /etc/cron.d; do
  if [ -r "$f" ] || [ -d "$f" ]; then ls -la "$f" 2>/dev/null || true; fi
done
if command -v crontab >/dev/null 2>&1; then safe_cmd crontab -l; fi

section "RUNTIMES"
for cmd in python3 python pip3 pip ffmpeg ffprobe git docker podman node npm; do
  if command -v "$cmd" >/dev/null 2>&1; then
    case "$cmd" in
      ffmpeg|ffprobe) "$cmd" -version 2>&1 | head -n 3 ;;
      docker) docker --version 2>&1; docker ps --no-trunc 2>&1 || true; docker images 2>&1 || true ;;
      podman) podman --version 2>&1; podman ps --no-trunc 2>&1 || true; podman images 2>&1 || true ;;
      *) "$cmd" --version 2>&1 || true ;;
    esac
  fi
done

section "LIKELY MOODIFY PATHS"
# Find directory names only; avoid reading secrets or huge files.
for root in /opt /srv /var/www /home /root; do
  if [ -d "$root" ]; then
    find "$root" -maxdepth 4 -type d \( -iname '*moodify*' -o -iname '*audio*factory*' \) -print 2>/dev/null | head -n 200
  fi
done

section "GIT IDENTITIES IN LIKELY MOODIFY REPOS"
while IFS= read -r gitdir; do
  repo="${gitdir%/.git}"
  printf '\n--- %s ---\n' "$repo"
  git -C "$repo" status --short --branch 2>&1 || true
  git -C "$repo" rev-parse HEAD 2>&1 || true
  git -C "$repo" remote -v 2>&1 | sed -E 's#(https?://)[^/@:]+:[^/@]+@#\1***:***@#g' || true
done < <(for root in /opt /srv /var/www /home /root; do
  [ -d "$root" ] && find "$root" -maxdepth 5 -type d -name .git -print 2>/dev/null
done | head -n 200)

section "ENVIRONMENT VARIABLE NAMES ONLY"
# Never print values.
env | cut -d= -f1 | sort | grep -Ei 'MOODIFY|DATABASE|MYSQL|POSTGRES|POLAR|OSS|ALI|LALAL|AUDIOLLA|REDIS|CELERY|S3|BUCKET|API|TOKEN|KEY|SECRET' || true

section "END"
printf 'W01-P00 read-only node scan finished.\n'
