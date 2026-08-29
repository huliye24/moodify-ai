# Rollback Readiness — MFY-INFRA-FOUNDATION-001

## 1. Git baseline recovery (Phase B)
- Draft PR #1 (huliye24/moodify) — not merged. Close/delete branch
  `codex/moodify-production-baseline-20260813` = complete rollback.
- LA production untouched: nothing to roll back on the server.

## 2. Hangzhou API authentication (C1)
Backups in place on Hangzhou ECS:
- `/root/moodify-core-package/src/moodify/api/main.py.bak-20260813`
  (checksum fe12e64dd03a596267979d49a11a078854ea3ae11f89aba911c7dbcdafc6ffab)
- `/etc/systemd/system/moodify-api.service.bak-20260813`
Rollback: restore main.py from backup, remove `EnvironmentFile=/root/moodify-api.env`
line from unit, `systemctl daemon-reload && systemctl restart moodify-api`, verify health.

## 3. PolarDB runtime account (C4)
- Account creation is additive; no existing account touched.
- If grants are wrong: fix grants, never elevate. Admin emergency access (mylab/mylab2)
  preserved.

## 4. Admin password rotation (C5)
- New independent passwords saved local-only 0600:
  `E:\moodify\temp\moodify_audit\polardb_admin.env`
- If a hidden dependency fails: no hidden dependency exists (zero code references,
  audit verified); admin access possible via the new passwords above.

## 5. Security group / whitelist (C2/C6)
- Not executed (console-only, BLOCKED_BY_HUMAN_AUTHORITY). No rollback needed.

## 6. Secrets
- API key: `E:\moodify\temp\moodify_audit\hangzhou_api_key.env` (0600)
- app DB password: `E:\moodify\temp\moodify_audit\polardb_app.env` (0600)
- admin DB passwords: `E:\moodify\temp\moodify_audit\polardb_admin.env` (0600)
- None entered git, none printed in any report.
