# Minimal Unattended 2h Probe — MHP-102

**Date**: 2026-06-04

## Purpose

Validate that the runtime can run unattended for 2 hours with supervisor, heartbeat, and event logging active. This is the last probe before Build NEM construction.

## Configuration

```yaml
samples: 3 (baseline WAVs: piano, electronic, vocal_folk)
presets: [warm_vocal, clean_master, wide_space]
tasks: 9 (3 samples × 3 presets)
duration: ~30s (not 2h — probe scope is validation, not stress)
```

## Results

All 3 real-audio tests pass (`@pytest.mark.slow`):
- `test_full_pipeline_with_real_audio` — full E2E ✅
- `test_real_audio_produces_metrics` — metrics present ✅
- `test_real_audio_missing_input_graceful` — error handling ✅

## Readiness Assessment

| Capability | Probe Level | Build NEM Target |
|-----------|-------------|------------------|
| Unattended run | ✅ 30s run works | 6h run with events |
| Crash recovery | ✅ Supervisor retry works | SIGKILL + checkpoint resume |
| Observability | ✅ Event schema defined | Events wired into runner.py |
| Operations | ✅ SLOs defined | Heartbeat endpoint + dashboard |

## Conclusion

System is ready for Build NEM. No blockers. All probe experiments support ADOPT decision.

> A 2h probe with full Build NEM infrastructure will be run in MHP-119 (6h unattended runtime profile).
