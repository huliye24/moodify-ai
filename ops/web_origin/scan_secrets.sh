#!/usr/bin/env bash
# Secrets scanner — MFY_PRODUCTION_OPERATIONS_OBSERVABILITY_001.
# Fails when a real secret (private key, token, live credential) is found in
# tracked files. False positives on example/placeholder values are expected;
# every hit must be reviewed before merge.
set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

PATTERNS=(
  'PRIVATE KEY-----'
  'AKIA[0-9A-Z]{16}'
  'ghp_[A-Za-z0-9]{36}'
  'sk-[A-Za-z0-9]{20,}'
  'xox[baprs]-[A-Za-z0-9-]{10,}'
  'MOODIFY_BFF_SESSION_SECRET=[^<$]'
  'MOODIFY_INTERNAL_API_KEY=[^<$]'
  'MOODIFY_HANGZHOU_KEY=[^<$]'
  'MOODIFY_DB_PASSWORD=[^<$]'
  'BEGIN (RSA|EC|OPENSSH) PRIVATE KEY'
)

EXCLUDE=(
  ':!补丁包'
  ':!artifacts'
  ':!moodify-core-package/benchmarks'
  ':!ops/web_origin/site/rongjingmusic/app-workspace.js'
)

violations=0
for pattern in "${PATTERNS[@]}"; do
  while IFS= read -r hit; do
    [ -z "$hit" ] && continue
    echo "SECRET-SCAN: ${pattern} -> ${hit}"
    violations=$((violations + 1))
  done < <(git grep -I -n -E "$pattern" HEAD -- "${EXCLUDE[@]}" 2>/dev/null || true)
done

# .env with real-looking values must not be tracked
while IFS= read -r f; do
  [ -z "$f" ] && continue
  if git ls-files --error-unmatch "$f" >/dev/null 2>&1; then
    echo "SECRET-SCAN: tracked env file: $f"
    violations=$((violations + 1))
  fi
done < <(git ls-files '*.env' '.env' 2>/dev/null || true)

if [ "$violations" -gt 0 ]; then
  echo "SECRET-SCAN: $violations potential secret(s) in tracked files (review each hit)"
  exit 1
fi
echo "SECRET-SCAN: clean"
