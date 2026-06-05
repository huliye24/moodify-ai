# MHP-848: MAP Report Schema Probe

**Status**: done
**Direction**: ECHAIN-MOODIFY-MAP-CHAIN-015 / NEM-MOODIFY-MAP-PROBE-045 / Probe Plan-6A: Schema Validation / V4
**Depends on**: MHP-846 (Interface Contract), MHP-847 (Alignment Smoke)
**Protocol**: AWJ Stack + E-Chain 54

## Context

MHP-846 produced `schemas/map_chain_report.schema.json`. Before the schema is promoted to a Build NEM contract, it must be validated against multiple v01 reports from different presets and edge cases.

## Goal

Validate the MAP report schema against at least 3 different v01 reports (different presets, different audio), and verify the schema correctly rejects known-bad reports.

## Scope

Allowed files:
- `schemas/map_chain_report.schema.json`
- `moodify-core-package/tests/baseline/test_audio/*.wav`
- `/tmp/moodify_map_probe_848/*`
- `reports/echain_moodify_map_chain_015/*`

Forbidden: no code changes to v01_pipeline.py or v01_types.py.

## Expected Output

`reports/echain_moodify_map_chain_015/mhp_848_map_report_schema_probe.md`

## Acceptance Criteria

- Schema validates against reports from at least 3 different presets.
- Schema correctly rejects invalid reports (missing required field, wrong workflow, invalid enum).
- Schema validates report from a file with issues/diagnosis.
- Probe report documents results and recommends ADOPT/HOLD/FIX.

## Proof Required

```bash
python3 -m json.tool schemas/map_chain_report.schema.json >/dev/null
for preset in clean_master warm_vocal wide_space; do
  PYTHONPATH=... python3 -m moodify.cli v01-process <wav> --preset $preset --output-dir /tmp/moodify_map_probe_848/$preset
done
python3 scripts/validate_map_schema.py  # or inline jsonschema validation
```
