# MHP-833: Operator Dashboard Learning View

**Status**: done
**Direction**: ECHAIN-MOODIFY-DATA-LOOP-014 / NEM-MOODIFY-DATA-LOOP-SYSTEM-044 / System Plan-6B: Product Integration / P1 (Execution)
**Depends on**: MHP-832
**Protocol**: E-Chain 54 = Probe NEM-18 + Build NEM-18 + System NEM-18

## Goal

Surface data loop insights in the operator dashboard as learning cards.

## Implementation

`moodify_runtime/product_integration.py::build_learning_dashboard()` converts a NightMetricRecord + RecommendationBundle into a `LearningDashboard` with 6 cards:
1. Runtime Success Rate (metric)
2. Fatal Error Alert (alert — only when present)
3. Score Direction Agreement (metric)
4. Preset Penalty Flag Rate (metric)
5. Top Recommendation Action (action — highest severity non-operator rec)
6. Learning Trend (trend — populated after 3+ nights)

## Acceptance Criteria

- Dashboard view works from data loop output. ✅
- Cards have severity levels (info/warn/critical). ✅
- Each card links to actionable MHP when relevant. ✅
- Empty/null data handled gracefully. ✅
