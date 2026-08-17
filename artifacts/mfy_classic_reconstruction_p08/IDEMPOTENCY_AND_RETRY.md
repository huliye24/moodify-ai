# MFY-CR-P08 — IDEMPOTENCY AND RETRY

## Idempotency

Key space: `(owner_id, source_sha256, reconstruction_version, idempotency_key)`
enforced by a UNIQUE constraint on `reconstruction_jobs`. SQLite unique
indexes allow multiple NULLs, so requests without a key never collide.

| Case | Behavior |
|---|---|
| Same key, duplicate request | 200 + `X-Moodify-Idempotency: RETURN_EXISTING` (same job returned) |
| Same owner+sha+version, existing success, no key | 200 RETURN_EXISTING (no duplicate compute) |
| `X-Moodify-Rebuild: true` | new job created; old evidence never overwritten |
| Different reconstruction version | new job/revision; old evidence preserved |
| No key, no prior | new job |

The upload is staged, hashed, and only then compared — the SHA-256 gate makes
duplicates detectable across retries even when the multipart request was
re-sent.

## Retry policy

Failures carry `retry_policy`:

| Policy | Auto retry | Examples |
|---|---|---|
| TRANSIENT | yes, bounded (≤3 attempts via lease counter) | temporary network, worker restart, transient storage |
| PERMANENT | never | invalid audio, unsupported codec, empty/silent source, identity-adjacent input errors |
| HUMAN_REQUIRED | never (stops) | MEDIUM objective, identity guard review |
| EXTERNAL_BILLABLE | never | reserved; any future billed external stem/API call must be registered before submission so a retry can never double-charge |

Retry mechanics: worker leases a QUEUED job (`attempts+1`), engine runs it;
on TRANSIENT failure `retry_or_fail` requeues until attempts >= 3, then
FAILED. MemoryError and resource-budget violations are PERMANENT (FAIL_SAFE)
— no OOM retry loops.

## Failure semantics

Every failure is a `FailureInfo`:
`failure_code, stage, retryable, user_action, internal_detail,
public_message_key`. Users receive only the message key + user action; the
internal detail is retained in the job record and evidence for operators.
Never stack traces to clients.
