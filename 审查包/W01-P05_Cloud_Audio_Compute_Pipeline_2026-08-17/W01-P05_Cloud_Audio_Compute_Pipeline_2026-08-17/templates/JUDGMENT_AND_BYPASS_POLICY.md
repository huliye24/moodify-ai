# Judgment & BYPASS Policy

## Judgment Output

- judgment_id
- subject
- observations
- detected conditions
- confidence
- uncertainty
- evidence_refs
- recommended_action

Allowed recommended_action:

- INTERVENE
- BYPASS
- HUMAN_REVIEW

## BYPASS

BYPASS is not failure.

Valid reasons include:

- insufficient evidence for intervention
- intervention expected benefit too uncertain
- source already satisfies target
- verification shows no supported gain
- human authority requests preservation

## BYPASS Record

- reason_code
- narrative
- evidence_refs
- decision_actor
- affected stages
- final audio lineage

## Principle

When intervention is unsupported, preserve the original signal.
