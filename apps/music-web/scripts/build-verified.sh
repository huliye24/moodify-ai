#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ "${SITES_ENV_READY:-}" != "1" ]]; then
  exec "${script_dir}/sites-env.sh" -- "$0" "$@"
fi

command -v timeout || {
  echo "build-verified.sh requires GNU timeout." >&2
  exit 69
}

vinext="${SITES_PROJECT_ROOT}/node_modules/.bin/vinext"
if [[ ! -x "${vinext}" ]]; then
  echo "vinext is unavailable. Run npm run install:ci and wait for it to finish before building." >&2
  exit 69
fi

# Cloudflare workerd is a platform-specific optional dependency that npm ci
# may silently skip on flaky networks; vinext/miniflare hard-require it
# (MFY_RELEASE_CANDIDATE_INTEGRITY_001). Fail fast with the repair command.
workerd_dir="${SITES_PROJECT_ROOT}/node_modules/@cloudflare/workerd-windows-64"
if [[ ! -d "${workerd_dir}" ]]; then
  echo "build-verified.sh: missing @cloudflare/workerd-windows-64 (npm ci skipped an optional platform package)." >&2
  echo "Fix: cd apps/music-web && npm install --no-save @cloudflare/workerd-windows-64@<version from package-lock.json>" >&2
  exit 69
fi

echo "Running bounded vinext build..."
timeout \
  --signal=TERM \
  --kill-after="${SITES_BUILD_KILL_AFTER:-10s}" \
  "${SITES_BUILD_TIMEOUT:-3m}" \
  "${vinext}" build

"${script_dir}/prune-deploy-audio.sh"
"${script_dir}/validate-artifact.sh"
