# MHP-847: v01 Seven-Stage Alignment Smoke

**Status**: sealed
**Direction**: ECHAIN-MOODIFY-MAP-CHAIN-015 / NEM-MOODIFY-MAP-PROBE-045 / Probe Plan-6A: Mainline Smoke / V3
**Depends on**: MHP-846
**Protocol**: AWJ Stack + E-Chain 54

## Context

The v01 pipeline was previously closer to a five-stage delivery flow. It now needs to expose the MAP seven-stage vocabulary so the rest of the E-chain can attach to stable names.

## Goal

Verify this v01 stage sequence:

```text
S_scan -> A_analyze -> D_diagnose -> P_process -> V_validate -> R_report -> G_generate
```

## Current Implementation Evidence

Updated files:

- `moodify-core-package/src/moodify/v01_pipeline.py`
- `moodify-core-package/src/moodify/v01_types.py`
- `moodify-core-package/tests/test_v01_pipeline.py`

Current v01 report includes:

- `workflow`
- `scan`
- `feature_analysis`
- `diagnosis_report`
- `validation_result`
- `metrics_before`
- `metrics_after`
- `delivery`

Validation uses `mrs_proxy_v01` as a temporary, explicitly versioned proxy. It is not the final calibrated MRS.

## Acceptance Criteria

- `workflow` equals the seven MAP stage names.
- `validation_result` includes `mrs_before`, `mrs_after`, `mrs_delta`, `damage_loss`, `risk_flags`, and `passed`.
- CLI smoke produces WAV, JSON, PDF, before chart, and after chart.
- Existing v01 API smoke remains green.

## Proof Required

Commands:

```bash
PYTHONPATH=/home/ubuntu/moodify-mainline:/home/ubuntu/moodify-mainline/moodify-core-package/src pytest -q moodify-core-package/tests/test_v01_pipeline.py moodify-core-package/tests/test_api_v01.py
PYTHONPATH=/home/ubuntu/moodify-mainline:/home/ubuntu/moodify-mainline/moodify-core-package/src python3 -m moodify.cli v01-process moodify-core-package/tests/baseline/test_audio/vocal_folk.wav --preset auto --output-dir /tmp/moodify_v01_check
```

Artifacts:

- `/tmp/moodify_v01_check/*_report.json`
- `/tmp/moodify_v01_check/*_report.pdf`
- `/tmp/moodify_v01_check/*_before_spectrum.png`
- `/tmp/moodify_v01_check/*_after_spectrum.png`

## Judge Notes

This MHP is function-complete but not sealed. Seal requires recording command output and a report under:

`reports/echain_moodify_map_chain_015/mhp_847_v01_seven_stage_alignment_smoke.md`

