# MHP-071: Genre-Specific Threshold Configuration

**Status**: completed
**Direction**: NEM-MOODIFY-MRS-002 / Build-6 / E1 (Execution)
**Depends on**: MHP-070 (NEM-MOODIFY-STUDIO-OS-001 complete)
**Protocol**: NEM-18 = Build-6 + Validate-6 + Harden-6

## Context

`decide_candidate_gate()` in `operator_console.py:255` uses global hardcoded thresholds:
- `required_mrs_delta = 0.0` — any improvement passes
- `transient_threshold = 1.0` — arbitrary
- `loudness_penalty_threshold = 1.0` — arbitrary

These thresholds apply identically to all genres. A piano track with `mrs_delta = 0.1` is treated the same as an electronic track with the same delta. This is musically wrong — different genres have different acceptable ranges for MRS change, transient response, and loudness variation.

## Goal

Create a YAML-based genre threshold configuration that `decide_candidate_gate()` reads at runtime. Support per-genre overrides with sensible defaults.

### Config format (`configs/mrs_thresholds.yaml`)
```yaml
defaults:
  required_mrs_delta: 0.0
  transient_threshold: 1.0
  loudness_penalty_threshold: 1.0
  over_dark_policy: binary  # "binary" | "graduated"

genres:
  electronic:
    required_mrs_delta: 2.0
    transient_threshold: 0.8
  piano:
    required_mrs_delta: 1.0
    transient_threshold: 1.2
  vocal:
    required_mrs_delta: 1.5
    loudness_penalty_threshold: 0.7
  rock:
    required_mrs_delta: 2.5
    transient_threshold: 0.6
  ambient:
    required_mrs_delta: 3.0
    loudness_penalty_threshold: 0.5
```

## Acceptance Criteria
- `configs/mrs_thresholds.yaml` exists with 5 genre sections
- `decide_candidate_gate()` accepts optional `genre` parameter and reads thresholds from config
- Unit test: electronic genre gets `required_mrs_delta = 2.0`, piano gets `1.0`
- Default thresholds unchanged when no genre is specified
- Existing 129 tests still pass
