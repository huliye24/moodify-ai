#!/usr/bin/env bash
set -euo pipefail

# Real audio belongs in R2 (or the configured media origin), never in the
# Worker's static asset bundle. Keep public/audio available for local preview,
# but remove the copied directory from the deployable artifact.
project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
deploy_audio="${project_root}/dist/client/audio"

if [[ -d "${deploy_audio}" ]]; then
  rm -rf -- "${deploy_audio}"
fi

if [[ -e "${deploy_audio}" ]]; then
  echo "Deploy artifact still contains audio: ${deploy_audio}" >&2
  exit 1
fi
