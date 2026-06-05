# MAP-Chain Interface Contract v0.1

**Version**: 0.1.0
**E-Chain**: ECHAIN-MOODIFY-MAP-CHAIN-015
**Status**: Draft — Probe 6A
**Validator**: `schemas/map_chain_report.schema.json`

## 1. Purpose

This contract defines the canonical v0.1 MAP objects shared across the seven-stage pipeline:

```text
S_scan → A_analyze → D_diagnose → P_process → V_validate → R_report → G_generate
```

All objects are JSON-serializable. The contract distinguishes between the current v01 implementation (`mrs_proxy_v01`) and the target calibrated MRS.

---

## 2. MAP Layer Objects

### 2.1 InputAudio (S layer input)

The audio file entry point before any processing.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `input_path` | string | yes | Absolute or relative path to audio file |
| `extension` | string | yes | Lowercase file extension (`.wav`, `.mp3`, `.flac`) |
| `file_size_bytes` | integer | yes | File size in bytes |
| `format_hint` | string | no | Container format if detectable |

### 2.2 ScanResult (S layer output)

Post-scan assessment of the input audio file.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `input_path` | string | yes | Path to the scanned audio file |
| `exists` | boolean | yes | Whether the file exists on disk |
| `extension` | string | yes | Lowercase file extension |
| `file_size_bytes` | integer | yes | File size in bytes |
| `readable` | boolean | yes | Whether the file decodes successfully |
| `warnings` | string[] | yes | Human-readable scan warnings |

MAP v0.2 target fields (not yet implemented):

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `loudness_lufs` | number | no | Integrated LUFS (ITU-R BS.1770) |
| `transient_ratio` | number | no | Peak-to-transient energy ratio |
| `stereo_width` | number | no | Side-to-mid energy ratio |
| `spectral_centroid_hz` | number | no | Weighted mean frequency |
| `dc_offset` | number | no | DC bias in the signal |
| `clip_count` | integer | no | Number of samples at digital ceiling |

### 2.3 FeatureAnalysis (A layer output)

Audio feature measurements extracted from the file.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file_path` | string | yes | Path to the analyzed audio file |
| `duration_s` | number | yes | Duration in seconds |
| `sample_rate` | integer | yes | Sample rate in Hz |
| `channels` | integer | yes | Channel count (1 or 2) |
| `spectrum` | object | yes | Per-band RMS energy (dB) |
| `spectrum.sub_bass` | number | yes | 20–60 Hz |
| `spectrum.bass` | number | yes | 60–250 Hz |
| `spectrum.low_mid` | number | yes | 250–500 Hz |
| `spectrum.mid` | number | yes | 500–2000 Hz |
| `spectrum.presence` | number | yes | 2000–5000 Hz |
| `spectrum.air` | number | yes | 8000–16000 Hz |
| `dynamics` | object | yes | Dynamic range measurements |
| `dynamics.peak_db` | number | yes | Peak level in dBFS |
| `dynamics.crest_factor` | number | yes | Peak / RMS ratio |
| `dynamics.dynamic_range_db` | number | yes | Estimated dynamic range in dB |
| `stereo` | object | yes | Stereo image measurements |
| `stereo.correlation_lr` | number | yes | Left-right correlation (-1 to 1) |

MAP v0.2 target feature vector (not yet implemented):

```text
f = [bass_balance, warmth, clarity, presence, density, stereo_width, transient_energy, reality_index]
```

### 2.4 DiagnosisResult (D layer output)

Audio problem diagnosis with human-readable and machine-actionable fields.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `overall_health` | string | yes | `good`, `fair`, or `poor` |
| `issues` | string[] | yes | Human-readable issue descriptions |
| `strengths` | string[] | yes | Human-readable strength descriptions |
| `suggested_presets` | string[] | yes | Ordered list of recommended presets |
| `metrics` | FeatureAnalysis | yes | The feature analysis this diagnosis is based on |

MAP v0.2 target fields (not yet implemented):

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `problem_vector` | object[] | no | Array of `{problem_id, severity, confidence}` |
| `diagnosis_loss` | number | no | Scalar diagnosis quality metric (0–1) |

### 2.5 ProcessPlan (P layer input/output)

The preset and DSP configuration applied during processing.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `requested_preset` | string | yes | User-requested preset or `"auto"` |
| `preset` | string | yes | Resolved preset actually applied |
| `elapsed_s` | number | yes | Total pipeline elapsed seconds |
| `stage_timings` | object | yes | Per-stage elapsed seconds |

MAP v0.2 target fields (not yet implemented):

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `craft_operations` | string[] | no | Craft-22 operation IDs applied |
| `safe_limits` | object | no | Per-operation safety caps |

### 2.6 ValidationResult (V layer output)

Before/after quality validation.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `passed` | boolean | yes | Whether quality gate is satisfied |
| `warnings` | string[] | yes | Human-readable quality warnings |
| `deltas` | object | yes | Before/after metric deltas |
| `mrs_version` | string | yes | MRS version identifier |
| `mrs_before` | number | yes | MRS score before processing |
| `mrs_after` | number | yes | MRS score after processing |
| `mrs_delta` | number | yes | MRS score change (after - before) |
| `damage_loss` | number | yes | Aggregate damage metric (0–1, lower is better) |
| `risk_flags` | string[] | yes | Risk classification tags |

**MRS Version Policy**:

- `mrs_proxy_v01`: Temporary proxy (current). Not calibrated. Versioned explicitly so consumers can detect it.
- `mrs_calibrated_v02`: Target. Will be a calibrated MRS adapter wrapping MRS Open v0.3.1.

**Risk Flag Taxonomy** (current):

| Flag | Meaning |
|------|---------|
| `peak_risk` | Output peak within 0.1 dB of 0 dBFS |
| `over_dark` | Air-band energy reduced by > 6 dB |
| `dynamic_damage` | Dynamic range reduced by > 4 dB |
| `mrs_regression` | MRS proxy decreased after processing |
| `damage_loss_high` | Damage loss ≥ 0.25 |

### 2.7 ReportBundle (R layer output)

The structured report outputs from a pipeline run.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `workflow` | string[7] | yes | Ordered MAP stage names |
| `scan` | ScanResult | yes | Input scan result |
| `feature_analysis` | FeatureAnalysis | yes | Pre-processing feature analysis |
| `diagnosis_report` | DiagnosisResult | yes | Audio diagnosis |
| `validation_result` | ValidationResult | yes | Quality validation result |
| `quality_gate` | ValidationResult | yes | Synonym for validation_result (compat) |
| `metrics_before` | FeatureAnalysis | yes | Pre-processing metrics |
| `metrics_after` | FeatureAnalysis | yes | Post-processing metrics |
| `delivery` | object | yes | Delivery file paths (see 2.8) |

### 2.8 DeliveryPackage (G layer output)

The physical artifacts produced by one pipeline run.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `output_audio` | string | yes | Absolute path to processed WAV |
| `json_report` | string | yes | Absolute path to JSON report |
| `pdf_report` | string | yes | Absolute path to PDF report (empty string if not generated) |
| `spectrum_before` | string | yes | Absolute path to before spectrum PNG |
| `spectrum_after` | string | yes | Absolute path to after spectrum PNG |

MAP v0.2 target fields (not yet implemented):

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `manifest` | string | no | Path to delivery manifest file |
| `logs` | string | no | Path to processing log bundle |
| `environment` | object | no | `{python_version, package_versions, git_hash, platform}` |

---

## 3. JSON Schema

The canonical JSON Schema is at `schemas/map_chain_report.schema.json`.

Validation command:

```bash
python3 -m json.tool schemas/map_chain_report.schema.json >/dev/null
```

Validate a report:

```bash
pip install jsonschema
python3 -c "
import json
from jsonschema import validate
with open('schemas/map_chain_report.schema.json') as f: schema = json.load(f)
with open('outputs/some_report.json') as f: report = json.load(f)
validate(report, schema)
print('valid')
"
```

---

## 4. CLI/API Contract

### 4.1 CLI

```bash
python3 -m moodify.cli v01-process <input.wav> --preset <name|auto> --output-dir <dir>
```

Output:
- Exit code 0 on success, non-zero on failure
- JSON report printed to stdout (when `--json` flag added in future)
- WAV, JSON, PDF, PNG artifacts written to `--output-dir`

### 4.2 Python API

```python
from moodify.v01_pipeline import process_audio
result: ProcessResult = process_audio("input.wav", preset="auto", output_dir="outputs")
assert result.success
print(result.delivery.output_audio)
print(result.quality_gate.passed)
```

### 4.3 Backwards Compatibility

- `quality_gate` and `validation_result` fields are synonyms in v0.1. Both MUST be present.
- `mrs_version` field MUST be checked by consumers before interpreting MRS values.
- New MAP fields added in v0.2 MUST be optional in the schema.
- The seven-element `workflow` array MUST NOT be reordered.

---

## 5. Versioning Policy

| Version | MRS | Schema | Breaking? |
|---------|-----|--------|-----------|
| v0.1.0 (current) | mrs_proxy_v01 | map_chain_report.schema.json | — |
| v0.2.0 (target) | mrs_calibrated_v02 | map_chain_report.schema.json (extended) | No |

Breaking changes require:
- Schema version bump in `$id`
- `mrs_version` field update
- Gate 2 (Build NEM) review
- Backwards-compat window of at least one E-chain cycle
