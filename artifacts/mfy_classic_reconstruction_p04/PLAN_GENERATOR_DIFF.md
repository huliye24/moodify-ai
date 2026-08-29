# P04 Plan Generator Diff

Reuses Data Factory InterventionPlan structure + plan generator discipline.
New: objective-aware candidate generation (reconstruction_objective/candidates.py)
maps objective kind -> bounded param budget -> semantic A/B/C intensity
(A minimal / B balanced / C upper-safe-boundary). No preset-based main logic;
legacy presets remain intervention primitives only (PRESET != OBJECTIVE !=
DECISION != FINAL VERSION).
