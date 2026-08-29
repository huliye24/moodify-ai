# MFY-CR-P08 — Codex Final Response

# 1. Result

```text
STATUS = P08_COMPLETE_WITH_BLOCKERS
BRANCH = codex/moodify-classic-reconstruction-001
HEAD   = 62fee077 (code) — this artifacts commit (evidence)
```

Blockers: real authorized corpus + human listening/hardware validation remain
PENDING (user instruction), same as P07. All software gates are green.

# 2. Job Model

```text
JOB_OBJECT = moodify.reconstruction_job.contract.ReconstructionJob (product layer)
PRODUCTION_CASE_RELATION = job.production_case_id -> canonical ProductionCase
                            in workspace case/production_case.json (+ evidence.json)
RESULT_OBJECT = ReconstructionResult (references audio by path; no audio in DB)
```

Confirmed: no second authority. Product state is a projection; the canonical
case/evidence are the single production truth.

# 3. End-to-End

```text
SUBMIT           = POST /api/v1/reconstruction/jobs (multipart, owner-bound)   -> QUEUED
VALIDATE         = probe + validate_source_audio + sha256 -> PERMANENT failures (UNSUPPORTED_FORMAT/DECODE_FAILED/INVALID_INPUT)
DIAGNOSE         = P03 run_era_diagnostic (production_case_id bound)            -> ANALYZING
PLAN             = P04 plan_from_findings (include_low_confidence=False)        -> PLANNING
RECONSTRUCT      = execute_intervention renders A/B/C                           -> RECONSTRUCTING
IDENTITY_GUARD   = P05 guard_candidate + rank_candidates                        -> VERIFYING
FINALIZE         = select_result -> SUCCEEDED / SOURCE_WINS / HUMAN_REQUIRED
RESULT_FETCH     = GET result + short-lived owner tokenized audio
```

# 4. Job States

Full mapping in STATE_PROJECTION.md. Actual statuses exercised end-to-end:
QUEUED, VALIDATING, ANALYZING, PLANNING, RECONSTRUCTING, VERIFYING,
SUCCEEDED, SOURCE_WINS, HUMAN_REQUIRED (engine), FAILED, CANCELLED.

# 5. API

```text
CREATE       = POST /jobs -> 202 CREATED / 200 RETURN_EXISTING; engineering params rejected (400)
STATUS       = GET /jobs/{id} -> product projection only
RESULT       = GET /jobs/{id}/result -> metadata + tokenized audio_url; HUMAN_REQUIRED -> 200 {status}
CANCEL       = POST /jobs/{id}/cancel -> 202 / 409 terminal
CAPABILITIES = GET /capabilities -> formats/max size/mode/stems=false/version/auth_mode
IDEMPOTENCY  = (owner, sha256, version, key) UNIQUE; RETURN_EXISTING; REBUILD header; per-version revision
```

# 6. Privacy / Authorization

```text
OWNER_ONLY        = yes — owner-filtered store reads; cross-owner 404 (existence not leaked)
PUBLIC_AUDIO_URL  = eliminated — only tokenized owner-only short-lived audio access (15 min HMAC, fail-closed)
TRAINING_DEFAULT  = false (field + API rejects true)
PUBLIC_DEMO_DEFAULT = false
SHARING           = no share/publish/public-link/catalog features exist
AUTH_MODE         = single_user default; explicit NOT_MULTIUSER_PRODUCTION_READY (owner mode available)
```

# 7. Retention

```text
SOURCE     = 30 d (minimized; input/original{suffix})
TMP        = immediate (engine finally + policy TTL 0; sweeps skip active jobs)
STEMS      = 0 (v0.1 never produces stems)
CANDIDATES = 7 d after decision
RESULT     = 90 d (until P10 encryption redesign)
EVIDENCE   = indefinite (canonical non-audio records)
```

TTLs are engineering defaults; no compliance claim (legal review required).

# 8. External Services

```text
LALAL    = not integrated (Option A: STEM_RECOMMENDED only; adapter boundary documented)
AUDIOLLA = not integrated
AUTO_STEM = false (capabilities)
BILLED_RETRY_PROTECTION = structural — no billed call exists in v0.1; EXTERNAL_BILLABLE
                           retry policy reserved and never auto-retried
```

# 9. Infrastructure

```text
PRODUCT_NODE     = worker is deployable on the LA product node (env-configured; no IPs/secrets in code);
                   local single-node verified; deployment unit out of scope
CONCURRENCY      = 1 (serial worker; no parallel capacity evidence yet)
PROCESSING_TIME  = synthetic 2 s fixture end-to-end ~8 s wall; real 219 s track was minutes (P06 evidence)
PEAK_MEMORY      = tracemalloc-based (Windows); RSS accounting deferred to POSIX deploy
RESOURCE_GUARD   = wall 1800 s / candidates ≤4 / stems 0; MemoryError PERMANENT; worker precheck DEFER
```

# 10. Tests

```text
job            = store 18 + engine 8 (create/query/cancel/success/source wins/human required/failure)
api            = 9 (create/status/result/cancel/capabilities + error codes)
auth           = 8 (owner / cross-owner 404 / token expiry/forgery/ownership / fail-closed / single-user)
idempotency    = 4 (duplicate key / post-success / rebuild / distinct keys)
retention      = 7 (tmp / stems / candidates / source / result / evidence / active skip)
worker         = 3 (serial / restart recovery / precheck DEFER)
pipeline       = 5 (P06 parameterization regression) + engine integration (P03→P05 invoked once,
                   no duplicate ProductionCase, result references canonical evidence)
p03_p07_regression = full suite 944 passed / 5 skipped (20:02)
android_build  = N/A (cloud package; no Android change)
ruff           = All checks passed
diff_check     = 10 new module files + 3 modified (api/main, pipeline, objective) + CLI/pyproject
```

# 11. Unresolved

Only P09-affecting items (details in UNRESOLVED.md):

1. Real authorized 10-track corpus + human listening/hardware validation — PENDING (user instruction).
2. LA product-node deployment/systemd wiring — follow-up ops package.
3. Multiuser auth is NOT production-ready: default single_user; BFF session
   integration + real identity are P09 scope.
4. AAC/M4A edge cases not exhaustively tested; peak-memory RSS needs POSIX deploy.
5. MEDIUM findings will route real-music jobs to HUMAN_REQUIRED; operator CLI
   review is the v0.1 admin path (consumer review UI is P09/P11 scope).
6. P07 factory corpus/learning records not auto-fed by P08 (kept separate; P09 may bridge).

# 12. Recommendation

```text
READY_FOR_P09_LISTENING_ENVIRONMENT_V0_1
```

CAN_A_CLIENT_SUBMIT_ONE_TRACK?             YES (multipart API, owner-bound)
CAN_THE_CLOUD_RECONSTRUCT_IT_END_TO_END?   YES (P03→P05 via golden pipeline, verified)
IS_THE_JOB_IDEMPOTENT?                     YES (UNIQUE key space, RETURN_EXISTING/REBUILD)
CAN_SOURCE_WIN?                            YES (SOURCE_WINS first-class product result)
CAN_HUMAN_REQUIRED_STOP_AUTOMATION?        YES (stopping state, no auto-approval; operator CLI only)
ARE_RESULTS_OWNER_ONLY?                    YES (owner-filtered; cross-owner 404)
ARE_PUBLIC_URLS_ELIMINATED_OR_GATED?       GATED (tokenized short-lived audio; none public)
ARE_TEMP_FILES_CLEANED?                    YES (tmp immediate + engine finally + sweep)
CAN_ANDROID_CONSUME_THE_API_WITHOUT_KNOWING_INTERNALS? YES (product projection only)
IS_THE_SYSTEM_READY_FOR_LISTENING_ENVIRONMENT_V0_1?    YES — with the listed blockers (corpus/human/hardware evidence)
```
