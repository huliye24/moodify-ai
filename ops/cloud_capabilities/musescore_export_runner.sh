#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: moodify-musescore-export INPUT_SCORE OUTPUT_FILE" >&2
  exit 64
fi

input_score="$1"
output_file="$2"
state_root="/var/lib/moodify/capabilities/musescore"

if [[ ! -f "$input_score" ]]; then
  echo "input score does not exist: $input_score" >&2
  exit 66
fi

install -d -m 0750 "$(dirname "$output_file")" \
  "$state_root/config" "$state_root/cache" "$state_root/data" "$state_root/runtime"
chmod 0700 "$state_root/runtime"

export HOME="/var/lib/moodify"
export XDG_CONFIG_HOME="$state_root/config"
export XDG_CACHE_HOME="$state_root/cache"
export XDG_DATA_HOME="$state_root/data"
export XDG_RUNTIME_DIR="$state_root/runtime"
export QT_QPA_PLATFORM="offscreen"

exec timeout 300s musescore3 -f -m -s -o "$output_file" "$input_score"
