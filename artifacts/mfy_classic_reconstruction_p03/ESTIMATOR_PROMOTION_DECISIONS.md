# MFY-CR-P03 — Estimator Promotion Decisions

Gate applied: synthetic validation → perturbation → repeatability → false
positive review → boundary test → decision (01_TASK.md §7). The global
registry (`measurement_registry_v1.yaml`) is UNCHANGED — `judgment_eligible`
stays `false` for both estimators (verified by test). Promotion here means the
new *diagnostic* eligibility layer (`ERA_DIAGNOSTIC_POLICY_V1`).

| Metric | Repeatable | Monotonic | FP risk | Diagnostic use | Final |
|---|---|---|---|---|---|
| estimated_hf_cutoff | yes (seeded) | coarse on tonal content | dark-mix FP guarded | ED-01 primary | ELIGIBLE_FOR_DIAGNOSTIC |
| estimated_noise_floor | yes | yes | dense-mix miss (accepted) | ED-02 primary | ELIGIBLE_FOR_DIAGNOSTIC |
| stereo_correlation | yes | yes | mono-as-defect FP guarded | ED-04 primary | ELIGIBLE_FOR_DIAGNOSTIC |
| phase_risk_ratio | yes | yes | wide-production FP | ED-04 corroborating | ELIGIBLE_FOR_DIAGNOSTIC |
| clipping_sample_ratio | yes (physical) | yes | distortion-as-art guarded | ED-03 primary | ELIGIBLE_FOR_DIAGNOSTIC |
| spectral_flatness | yes | n/a | arrangement-density FP | ED-05 context | ELIGIBLE_FOR_DIAGNOSTIC |
| crest_factor_db | yes (derived) | yes | genre-aesthetic FP | ED-03 context | ELIGIBLE_FOR_DIAGNOSTIC |
| plr_db | derived exact | yes | same as crest | report context | KEEP_DESCRIPTIVE_ONLY |

## Notes

- `ELIGIBLE_FOR_DIAGNOSTIC` != global `judgment_eligible=true`. The two layers
  are deliberately separate; nothing in the global judgment path changed.
- No metric received `ELIGIBLE_FOR_GUARDRAIL` or `REJECT_OR_REWORK` in v0.1.
- Policy enforcement is code-level: `DETECTOR_INPUTS ⊆ eligible` asserted by
  `test_policy_enforcement`; the global registry is asserted untouched by
  `test_judgment_eligibility_untouched`.
