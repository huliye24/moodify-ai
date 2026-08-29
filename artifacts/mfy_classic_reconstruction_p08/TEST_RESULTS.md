# MFY-CR-P08 — TEST RESULTS

## Full suite (2026-08-17, codex/moodify-classic-reconstruction-001)

```
944 passed, 5 skipped, 7 warnings in 1202.71s (20:02)
```

P07 baseline was 839 passed / 5 skipped → P08 adds 105 passing tests.

## New tests (this package)

### tests/reconstruction_job/ (67)

| File | Count | Coverage |
|---|---|---|
| test_store.py | 18 | schema, CRUD, owner filter, idempotency UNIQUE, lease, recovery, cancel semantics, transitions, counts, progress labels, product view hygiene |
| test_selection.py | 9 | decision tree: auto win, hard-gate block, all-blocked→SOURCE_WINS, no-candidate→SOURCE_WINS, per-candidate HUMAN_REQUIRED skip vs stop, MEDIUM/HIGH/LOW objective gating |
| test_engine.py | 8 | end-to-end SOURCE_WINS/SUCCEEDED/FAILED, unsupported format, pipeline invoked once, tmp cleanup, single canonical case, HUMAN_REQUIRED stops without result, cancel boundary, transient requeue |
| test_idempotency.py | 4 | same-key replay, different-key isolation, post-success RETURN_EXISTING, rebuild header |
| test_api.py | 9 | capabilities, create, engineering params rejected, unsupported type, status/result projection, cancel, 404s, full worker flow incl. tokenized audio download |
| test_auth.py | 8 | owner-mode header required, own read, cross-owner 404 (job+cancel), token valid/cross-owner/expired/garbage, secret missing fail-closed, single-user default |
| test_retention.py | 7 | tmp immediate, substantive dirs kept, TTL expiry per class, source expiry, indefinite evidence, sweep across workspaces, active-job skip |
| test_worker.py | 3 | serial processing, restart recovery, resource precheck DEFER |
| conftest.py | — | deterministic synthetic fixtures (clean full-band + 9 kHz lowpass), store/config fixtures |

### tests/reconstruction/test_pipeline_params.py (5)

| Test | Verifies |
|---|---|
| defaults_preserve_p06_behavior | P06 golden behavior unchanged (record_id, candidates dir, blind kit) |
| case_id_propagates | case_id reaches diagnostics/interventions |
| record_id_override | record_id honored |
| skip_blind_kit | empty kit, no kit files |
| candidates_dir_override | candidates rendered into the given directory |

## Behavior changes to existing code (regression-protected)

- `moodify.reconstruction.pipeline.run_golden_pipeline` gained 5 optional
  kwargs (`record_id`, `case_id`, `skip_blind_kit`, `candidates_dir`,
  `include_low_confidence`) — defaults preserve P06 behavior
  (tests/reconstruction/ all green).
- `moodify.reconstruction.objective.plan_from_findings` gained
  `include_low_confidence` (production mode: LOW never authorises, ED-02
  NOISE_REDUCTION unsupported → SOURCE-only plans). Golden default unchanged.
- `moodify.api.main` registers the reconstruction router (existing endpoints
  untouched).

## Quality gates

- `ruff check src tests` → All checks passed.
- Full suite → 944 passed / 5 skipped.
- Deterministic fixtures generated at test time (numpy/scipy/soundfile); no
  binaries committed.
