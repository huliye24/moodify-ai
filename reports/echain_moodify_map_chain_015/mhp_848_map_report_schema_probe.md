# MHP-848: MAP Report Schema Probe — Validation Report

**Generated**: 2026-06-05
**Status**: done
**E-Chain**: ECHAIN-MOODIFY-MAP-CHAIN-015 / NEM-MOODIFY-MAP-PROBE-045 / Probe Plan-6A

## Validation Summary

### Positive Tests (Schema accepts valid reports)

| # | Test | Report | Result |
|---|------|--------|--------|
| 1 | clean_master preset | `vocal_folk_clean_master_report.json` | valid |
| 2 | warm_vocal preset (with quality warning) | `vocal_folk_warm_vocal_report.json` | valid |
| 3 | wide_space preset | `vocal_folk_wide_space_report.json` | valid |

All 3 preset variants pass schema validation. The warm_vocal report has `passed: false` and one quality warning but still validates — correct behavior.

### Negative Tests (Schema rejects invalid reports)

| # | Test | Mutated Field | Result |
|---|------|--------------|--------|
| 2 | Missing required field | removed `workflow` | rejected: required property |
| 3 | Wrong workflow array | 5-stage instead of 7 | rejected: too short |
| 4 | Bad health enum | `overall_health = "terrible"` | rejected: not in enum |
| 5 | Invalid risk flag | `risk_flags = ["not_a_real_flag"]` | rejected: not in enum |
| 6 | Invalid channels | `channels = 6` | rejected: exceeds maximum |

All 5 negative tests correctly reject invalid reports.

### Edge Case Test

| # | Test | Detail | Result |
|---|------|--------|--------|
| 7 | Report with quality warnings | warm_vocal: dynamic range warning, passed=false | valid |

Reports with quality issues still validate — schema validates structure, not quality.

## Recommendation

**ADOPT** — The schema correctly validates v01 reports from all 3 presets and correctly rejects 5 classes of invalid input. It is ready for Build NEM contract promotion.

## Command Evidence

```text
$ for preset in clean_master warm_vocal wide_space; do
    PYTHONPATH=... python3 -m moodify.cli v01-process vocal_folk.wav --preset $preset ...
  done
  clean_master: exit 0, quality pass
  warm_vocal:  exit 0, quality review (1 warning)
  wide_space:  exit 0, quality pass

$ python3 -c "from jsonschema import validate; ..."
  7/7 tests pass (3 positive, 5 negative, 1 edge case)
```
