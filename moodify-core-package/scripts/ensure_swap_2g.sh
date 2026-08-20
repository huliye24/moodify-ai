#!/usr/bin/env bash
set -euo pipefail

# Conservative helper: create a 2 GiB swapfile only when the host has no active swap.
# Codex/operator must inspect disk capacity first.

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run as root (sudo)." >&2
  exit 2
fi

if swapon --show --noheadings | grep -q .; then
  echo "Swap already active; no change made."
  swapon --show
  exit 0
fi

FREE_KB=$(df --output=avail / | tail -1 | tr -d ' ')
NEEDED_KB=$((3 * 1024 * 1024))
if (( FREE_KB < NEEDED_KB )); then
  echo "Not enough free root-disk headroom to safely create 2 GiB swap." >&2
  exit 3
fi

fallocate -l 2G /swapfile || dd if=/dev/zero of=/swapfile bs=1M count=2048
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
if ! grep -q '^/swapfile ' /etc/fstab; then
  echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi
sysctl vm.swappiness=10
if [[ -f /etc/sysctl.conf ]] && ! grep -q '^vm.swappiness=' /etc/sysctl.conf; then
  echo 'vm.swappiness=10' >> /etc/sysctl.conf
fi
swapon --show
