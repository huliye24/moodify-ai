# MFY-CR-P08 — END-TO-END TEST

## Procedure

1. Generate deterministic synthetic fixtures (test-time only, nothing
   committed as binary):
   - `clean_fullband_wav`: full-band stereo, silence gaps, quiet noise bed
     (mirrors P03 `clean_stereo` recipe) -> no PTL findings -> SOURCE_WINS.
   - `lowpass_wav`: 9 kHz lowpass of the same signal (P03-validated strong
     ED-01) -> candidates A/B/C -> identity PASS on A/B -> SUCCEEDED.
2. API flow (TestClient): `POST /api/v1/reconstruction/jobs` (multipart) ->
   poll `GET /jobs/{id}` -> worker `run_once` -> `GET /jobs/{id}/result` ->
   `GET /jobs/{id}/result/audio?token=`.
3. CLI flow (operator): `moodify-reconstruction submit demo.wav
   --idempotency-key demo-1` -> `worker --once` -> `jobs` -> `status` ->
   `result`.

## Observed CLI run (2026-08-17)

```
submit  -> {"idempotency":"CREATED", job QUEUED, source_sha256 470729ec...}
worker  -> exit 0
status  -> SUCCEEDED
result  -> selected_candidate=B, identity_status=PASS,
           audio_object_ref=.../candidates/B.wav
re-submit with same idempotency key -> {"idempotency":"RETURN_EXISTING",
           same job_id}  (no duplicate job)
```

## Verified behaviors

- Source validation: unsupported suffix -> 415 (API) / UNSUPPORTED_FORMAT
  (engine, PERMANENT); empty -> 422 / INVALID_INPUT; decode failure ->
  DECODE_FAILED (PERMANENT).
- Selection: SUCCEEDED (auto candidate), SOURCE_WINS (no safe candidate),
  HUMAN_REQUIRED (MEDIUM objective or identity review) — all covered by
  `test_selection.py` decision tree and engine integration tests.
- Idempotency: duplicate key, post-success duplicate, rebuild header,
  different-key isolation (`test_idempotency.py`).
- Auth: owner-only reads, cross-owner 404, token expiry/forgery/ownership,
  secret-missing fail-closed (`test_auth.py`).
- Retention: tmp immediate, candidates TTL, evidence preserved, active-job
  sweep skip (`test_retention.py`).
- Worker: serial processing, restart recovery, resource precheck DEFER
  (`test_worker.py`).
- Pipeline: P03->P05 invoked exactly once per job, single canonical
  ProductionCase, result references canonical evidence, tmp cleaned
  (`test_engine.py`).
