# P04 Objective Model (reconstruction-objective-v0.1)

## ReconstructionObjective

| Field | Meaning |
|---|---|
| objective_id | deterministic hash(source_hash, finding_id) |
| kind | RO-00 BYPASS / RO-01 BANDWIDTH_BALANCE / RO-02 NOISE_REDUCTION / RO-03 DYNAMIC_RECOVERY / RO-04 STEREO_STABILIZATION / RO-05 SPECTRAL_DECONGESTION / RO-06 TRANSFER_REPAIR |
| production_case_id | canonical ProductionCase (single authority) |
| source_hash | immutable source identity |
| diagnostic_finding_refs | P03 findings that justify this objective |
| target_conditions | category, max_plan_intensity, unsupported |
| preserve_conditions | no_new_clipping, no_duration_change |
| parameter_budget | InterventionBudget |
| confidence | LOW / MEDIUM / HIGH |
| requires_human_review | MEDIUM confidence or flagged finding |
| unsupported_reason | honest capability downgrade |

## Objective kinds (v0.1, honest)

- RO-01 named **BANDWIDTH_BALANCE** — the v0.1 engine performs balance work,
  it does NOT restore missing content (never claims BANDWIDTH_RECOVERY)
- RO-02 noise reduction = **INTERVENTION_NOT_SUPPORTED_V0_1** — no reliable
  denoise in the v0.1 engine; EQ is not a substitute for denoise

## Confidence gating (diagnosis != authorisation)

| Confidence | Planning scope |
|---|---|
| HIGH | A(0.3) / B(0.5) / C(0.7) |
| MEDIUM | A(0.1) / B(0.2) only, C=BYPASS, human review REQUIRED |
| LOW | BYPASS (no aggressive processing) |

Only POSSIBLE_TECHNICAL_LIMITATION findings grant planning authority;
LIKELY_ARTISTIC_CHARACTER / INSUFFICIENT_EVIDENCE / NOT_APPLICABLE never do.

## A/B/C semantics

- A = Minimal Intervention (if light touch is enough, stop)
- B = Balanced Reconstruction (max audible gain, conservative identity)
- C = Upper Safe Boundary (pressure test; NEVER default product output)
