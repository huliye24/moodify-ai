#!/usr/bin/env bash
set -euo pipefail

# The LA production service runs the Vinext output under Node rather than a
# Cloudflare Worker. This flag activates the fail-closed binding adapter so
# Cloudflare-only virtual imports never enter the self-hosted server bundle.
export MOODIFY_SELF_HOSTED=1
exec "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/build-verified.sh" "$@"
