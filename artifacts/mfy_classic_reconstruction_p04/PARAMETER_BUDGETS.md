# P04 Parameter Budgets (InterventionBudget v0.1)

| Budget | Ceiling | Note |
|---|---|---|
| eq_gain_db_max | 3.0 | per-objective EQ cap |
| loudness_delta_db_max | 0.5 | A/B level stability |
| parameter_distance_max | 1.0 | overall distance budget (anti-accumulation) |
| stereo_width_delta_max | 0.2 | no destructive widening |

Per-kind caps: bandwidth EQ <= 2.5dB, spectral EQ <= 2.0dB, dynamics loudness
<= 0.4dB, stereo width <= 0.15dB, transfer EQ <= 1.0dB.
Thresholds validated by hard-gate tests (not document-invented).
