# MFY-CR-P08 — RETENTION POLICY

Six storage classes, independent TTLs (seconds; `0` = delete immediately,
`null` = retain indefinitely). TTLs are engineering defaults and do NOT by
themselves constitute legal compliance — a legal review is required before
any compliance claim.

## Defaults (RetentionPolicy)

| Class | Workspace dir | TTL | Direction |
|---|---|---|---|
| TMP | tmp/ | 0 (immediate) | shortest; also cleaned in engine `finally` |
| STEMS | stems/ | 0 (v0.1 never produces stems) | short-lived by policy |
| CANDIDATES | candidates/ | 7 days | removable after decision |
| SOURCE | input/ | 30 days | minimized (private direction) |
| RESULT | result/ | 90 days | kept until P10 redesigns encryption |
| EVIDENCE | case/ (evidence.json, canonical JSON) | forever | long-term non-audio audit records |

## Enforcement

- `retention.sweep_workspaces(root, policy, active_job_ids)` runs on worker
  startup and hourly; workspaces of currently leased jobs are SKIPPED (a
  sweep can never delete scratch of work in progress).
- `cleanup_tmp` removes tmp/ immediately (engine also does this in `finally`).
- Enforcement is by directory mtime (workspace-dir granularity), per class.

## Privacy guarantees independent of TTL

- `training_permission=false` default: evidence may be retained but NEVER
  enters training corpora automatically.
- No public catalog, no search of others' songs, no public pages, no
  recommendation based on private uploads.
- Source retention is intentionally short; result/evidence separation follows
  the private-audio direction (P10 will move to user-key-encrypted objects).
