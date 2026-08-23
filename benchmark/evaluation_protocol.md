# Evaluation Protocol

This document defines standardized methodologies for evaluating audio quality in the Moodify Audio Benchmark framework.

## Overview

Evaluation protocols ensure consistent, reproducible, and comparable results across different models, pipelines, and research groups.

## Protocol Categories

### 1. Technical Evaluation

#### Objective Metrics

| Metric | Description | Target Range | Tool |
|--------|-------------|--------------|------|
| LUFS | Integrated loudness | -14 to -16 LUFS | ffmpeg, pyloudnorm |
| True Peak | Peak level | < -1 dBTP | ffmpeg, libebur128 |
| Dynamic Range | Loudness range | 8-14 LU | EBU R128 |
| THD+N | Total harmonic distortion | < 0.1% | Audio analyzer |
| SNR | Signal-to-noise ratio | > 60 dB | Custom analysis |

#### Spectral Analysis

- **Frequency Response**: ±3 dB from 20 Hz to 20 kHz
- **Spectral Balance**: Energy distribution across octaves
- **Stereo Correlation**: Phase coherence between channels
- **Spectral Flatness**: Tonal vs. noise-like characteristics

### 2. Perceptual Evaluation

#### MUSHRA-style Testing

```
Procedure:
1. Present reference (hidden) and multiple test samples
2. Rate each on 0-100 scale (0 = bad, 100 = excellent)
3. Include hidden reference and anchor
4. Minimum 10 listeners per test
```

#### ABX Testing

```
Procedure:
1. Present sample A and sample B
2. Present sample X (randomly A or B)
3. Listener identifies whether X matches A or B
4. Statistical significance: p < 0.05
```

#### Preference Ranking

```
Procedure:
1. Present 3-5 samples simultaneously
2. Rank by preference (1 = most preferred)
3. Record confidence level (1-5)
4. Collect qualitative feedback
```

### 3. Comparative Evaluation

#### Pairwise Comparison

- Direct A vs. B comparison
- Forced choice preference
- Statistical analysis using Bradley-Terry model

#### Tournament Style

- Elimination bracket for large model sets
- Elo rating system for ranking
- Confidence intervals for rankings

## Evaluation Dimensions

### Technical Quality Score (TQS)

Computed from objective metrics:

```python
def compute_tqs(metrics):
    """
    Technical Quality Score (0-100)
    """
    loudness_score = score_loudness(metrics['lufs'])
    peak_score = score_peak(metrics['true_peak'])
    dynamic_score = score_dynamic_range(metrics['lra'])
    spectral_score = score_spectral_balance(metrics['spectral'])
    
    return weighted_average([
        (loudness_score, 0.25),
        (peak_score, 0.25),
        (dynamic_score, 0.25),
        (spectral_score, 0.25)
    ])
```

### Perceptual Quality Score (PQS)

Derived from human ratings:

```python
def compute_pqs(ratings):
    """
    Perceptual Quality Score (0-100)
    """
    mean_rating = statistics.mean(ratings)
    confidence = compute_confidence_interval(ratings)
    
    return {
        'score': mean_rating * 20,  # Scale 1-5 to 0-100
        'confidence': confidence,
        'n': len(ratings)
    }
```

### Overall Benchmark Score

```python
def compute_overall(tqs, pqs, weights=None):
    """
    Combined benchmark score
    """
    if weights is None:
        weights = {'technical': 0.4, 'perceptual': 0.6}
    
    return (
        tqs * weights['technical'] +
        pqs['score'] * weights['perceptual']
    )
```

## Test Dataset Requirements

### Minimum Dataset Size

| Evaluation Type | Minimum Samples | Recommended |
|-----------------|-----------------|-------------|
| Technical only | 10 | 100 |
| Perceptual | 20 | 200 |
| Model comparison | 50 | 500 |
| Publication quality | 100 | 1000 |

### Genre Distribution

For general-purpose benchmarks:

- Pop/Rock: 25%
- Classical: 20%
- Electronic: 20%
- Jazz: 15%
- Folk/World: 10%
- Other: 10%

### Audio Characteristics

- Duration: 10-60 seconds per sample
- Sample rate: 44.1 kHz or 48 kHz
- Bit depth: 16 or 24 bit
- Channels: Stereo (2.0)

## Statistical Methods

### Significance Testing

- **Paired t-test**: For before/after comparisons
- **ANOVA**: For multiple model comparisons
- **Mann-Whitney U**: For non-parametric data
- **Cohen's d**: Effect size calculation

### Confidence Intervals

- 95% CI for all mean estimates
- Bootstrap resampling for complex metrics
- Bayesian credible intervals (optional)

### Inter-rater Reliability

- Cohen's kappa for categorical ratings
- ICC (Intraclass Correlation) for continuous ratings
- Minimum acceptable: κ > 0.6 or ICC > 0.75

## Reporting Standards

### Required Information

1. Dataset description and source
2. Evaluation protocol version
3. Number of samples and listeners
4. Statistical methods used
5. Confounding factors and controls
6. Reproducibility information

### Result Format

```json
{
  "evaluation_id": "string",
  "protocol_version": "1.0.0",
  "dataset_id": "string",
  "model_id": "string",
  "timestamp": "ISO-8601",
  "scores": {
    "technical": {},
    "perceptual": {},
    "overall": {}
  },
  "statistics": {
    "confidence_intervals": {},
    "p_values": {},
    "effect_sizes": {}
  },
  "metadata": {}
}
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2026-08-23 | Initial protocol definition |

## References

- ITU-R BS.1770 (Loudness)
- EBU R128 (Loudness normalization)
- ITU-R BS.1534 (MUSHRA)
- ITU-R BS.1116 (ABC/HR)
