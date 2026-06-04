# MRS Calibration Guide — Moodify Studio OS

**Version**: v0.2.0
**Date**: 2026-06-04
**Protocol**: NEM-18 / NEM-MOODIFY-MRS-002 / Build-6 / S1

---

## 1. What MRS Measures

MRS (Moodify Reality Score) quantifies how "real" or "natural" processed audio sounds compared to the original. It answers: *Did the DSP processing improve the audio, or make it worse?*

### The Four Sub-Scores

| Sub-score | Weight (default) | What it measures | Good range |
|-----------|------------------|------------------|------------|
| **peak** | 0.25 | How close peak amplitude is to 0.98 (just below clipping) | 0.85–0.98 |
| **rms** | 0.25 | Overall loudness, centered around 0.12 RMS | 0.08–0.16 |
| **crest** | 0.35 | Dynamic range (peak/RMS ratio), target ~8.0 | 5.0–12.0 |
| **dc_offset** | 0.15 | DC bias penalty — lower is better | < 0.005 |

### MRS Variants

| Variant | Engine | Use case |
|---------|--------|----------|
| **pseudo_mrs** | `metrics.py:pseudo_mrs()` | Fast, no dependencies. Good for quick scans. |
| **calibrated pseudo-MRS** | `scripts/calibrate_pseudo_mrs.py` | Grid-search-optimized weights. Best for production gates. |
| **MRS Open v0.3.1** | `metrics.py:compute_mrs_open_v031()` | External standard. Requires moodify-core-package. D_ref = 0.274350. |

---

## 2. Genre Thresholds

Thresholds are stored in `configs/mrs_thresholds.yaml`. Each genre has its own gate criteria.

### Current Thresholds (v0.2.0)

| Genre | MRS Δ | Transient | Loudness | Over-dark Policy |
|-------|-------|-----------|----------|------------------|
| electronic | 2.0 | 0.8 | 1.0 | graduated |
| piano | 1.0 | 1.2 | 1.0 | graduated |
| vocal | 1.5 | 1.0 | 0.7 | graduated |
| rock | 2.5 | 0.6 | 1.0 | graduated |
| ambient | 3.0 | 1.0 | 0.5 | graduated |
| *default* | 0.0 | 1.0 | 1.0 | binary |

### How Thresholds Work

```python
from moodify_runtime.operator_console import decide_candidate_gate

# Piano: needs MRS delta ≥ 1.0 to pass
result = decide_candidate_gate("C1", "J1", runtime_success=True,
                               mrs_score_delta=1.5, genre="piano")
# → {"decision": "approve", "reasons": ["all_gates_passed"]}

# Same delta with electronic threshold (≥ 2.0)
result = decide_candidate_gate("C1", "J1", runtime_success=True,
                               mrs_score_delta=1.5, genre="electronic")
# → {"decision": "reprocess", "reasons": ["mrs_delta_below_threshold"]}
```

### Adding a New Genre

1. Add a section to `configs/mrs_thresholds.yaml`:
```yaml
genres:
  jazz:
    required_mrs_delta: 1.8
    transient_threshold: 1.0
    loudness_penalty_threshold: 0.8
    over_dark_policy: graduated
    note: "Jazz dynamics are natural; don't over-compress."
```
2. Update `GENRE_TOLERANCE` in `moodify_runtime/over_dark.py` with per-band tolerances.
3. Run `scripts/calibrate_pseudo_mrs.py` with jazz samples to find optimal weights.
4. Add jazz samples to the calibration dataset.
5. Run a calibration audit to verify gate accuracy.

---

## 3. Over-Dark Detection

The graduated over-dark detector (`moodify_runtime/over_dark.py`) replaces the old binary flag with 3 levels.

### How It Works

1. Read before/after WAV files
2. Compute energy in 3 frequency bands: sub_bass (20-60Hz), low_mid (100-300Hz), mid (300-2000Hz)
3. Compute delta ratio per band: `(after - before) / before`
4. Cross-reference with genre tolerance thresholds
5. Classify: `none` | `mild` | `severe`

### Level Interpretation

| Level | Meaning | Gate Impact | Operator Action |
|-------|---------|-------------|-----------------|
| **none** | No significant darkness increase | Pass (no effect) | No action needed |
| **mild** | 1-2 bands show 10-30% energy increase | Reprocess | Review candidate; may still be acceptable |
| **severe** | Any band >30% increase OR all 3 bands >10% | **Reject** | Candidate is damaged; check preset parameters |

### Usage

```python
from moodify_runtime.over_dark import detect_over_dark

result = detect_over_dark("original.wav", "processed.wav", genre="vocal")
print(result.level)            # "none" | "mild" | "severe"
print(result.score)            # 0.0–1.0
print(result.affected_bands)   # e.g. ["low_mid"]
print(result.band_scores)      # {"sub_bass": 0.05, "low_mid": 0.18, "mid": 0.02}
print(result.recommendation)   # "pass" | "review" | "reject"
print(result.triggered)        # bool — backward compat
```

---

## 4. Calibration Workflow

### Step 1: Build a Calibration Dataset

```bash
# Assemble 50+ WAV samples across 5+ genres
# Process each through the appropriate preset
# Label at least 30 pairs with human preference

data/calibration/mrs_002/
├── source/{genre}/     # original WAVs
├── processed/{id}/     # DSP output
├── registry.jsonl      # sample metadata
└── labels.jsonl        # human decisions
```

### Step 2: Submit Human Reviews

```python
from moodify_runtime.mrs_calibration import submit_calibration_review

submit_calibration_review(cfg,
    set_id="CALSET_XXX",
    candidate_id="CAND_YYY",
    human_decision="better",   # "better" | "worse" | "no_change" | "unsure"
    gate_decision="approve",   # what the automated gate said
    notes="Clearer highs, bass still controlled",
)
```

### Step 3: Run Gate Audit

```python
from moodify_runtime.mrs_calibration import run_gate_audit

audit = run_gate_audit(cfg, set_id="CALSET_XXX")
# → {accuracy: 0.92, false_positives: 2, false_negatives: 1, ...}
```

Target: accuracy ≥ 85% overall, ≥ 70% per genre.

### Step 4: Propose Threshold Changes

```python
from moodify_runtime.mrs_calibration import propose_threshold

propose_threshold(cfg,
    parameter="required_mrs_delta",
    current_value=2.0,
    proposed_value=1.5,
    justification="Gate accuracy for electronic improved from 78% to 89% at delta=1.5",
)
```

### Step 5: Recalibrate Weights

```bash
python3 scripts/calibrate_pseudo_mrs.py \
    --before-dir data/calibration/mrs_002/source/ \
    --after-dir data/calibration/mrs_002/processed/ \
    --data data/calibration/mrs_002/labels.jsonl
```

Review the top-5 weight combinations. Update `configs/mrs_weights.yaml` if the best calibrated weights differ significantly from current defaults.

---

## 5. Interpreting Audit Reports

### GateAudit Output

```yaml
total_reviews: 50
false_positives: 3    # Gate rejected, human says "better"
false_negatives: 2    # Gate approved, human says "worse"
accuracy: 0.90        # 90% agreement
```

### Troubleshooting

| Symptom | Likely Cause | Action |
|---------|-------------|--------|
| High FP rate | Threshold too strict | Lower `required_mrs_delta` for that genre |
| High FN rate | Threshold too loose | Raise `required_mrs_delta` |
| over_dark disagrees with humans | Band tolerance wrong | Adjust `GENRE_TOLERANCE` in `over_dark.py` |
| Pseudo-MRS disagrees with MRS Open | Weights overfit | Recalibrate with larger dataset |

---

## 6. D_ref Maintenance

### What is D_ref?

D_ref is the reference distance used by MRS Open v0.3.1 to normalize reality scores. It represents the expected distance between "real" and "generated" audio in the MRS feature space.

Current value: **0.274350** (default, from `configs/mrs_open_v03.yaml`)

### When to Recalibrate

- After adding 50+ new calibration samples
- If MRS Open correlation with human labels drops below 0.5
- When switching to a new version of MRS Open

### How to Recalibrate

```python
from workers.mrs_open_benchmark_v03 import calibrate_dref

new_dref = calibrate_dref(reference_audio_dir="data/calibration/mrs_002/source/")
# Update configs/mrs_open_v03.yaml:
#   calibration:
#     d_ref: <new_value>
```

---

> A well-calibrated gate is an engineering asset. An uncalibrated gate is just an opinion.
