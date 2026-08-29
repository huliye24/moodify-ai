#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: moodify-basic-pitch INPUT_AUDIO OUTPUT_DIRECTORY" >&2
  exit 64
fi

input_audio="$1"
output_directory="$2"
runtime="/opt/moodify/capabilities/basic-pitch/venv/bin/basic-pitch"

if [[ ! -f "$input_audio" ]]; then
  echo "input audio does not exist: $input_audio" >&2
  exit 66
fi

install -d -m 0750 "$output_directory"
exec "$runtime" --save-note-events "$output_directory" "$input_audio"
