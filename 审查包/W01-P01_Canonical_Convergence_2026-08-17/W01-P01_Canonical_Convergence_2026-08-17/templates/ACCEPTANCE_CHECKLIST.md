# W01-P01 Acceptance Checklist

## Inputs

- [ ] P00 complete
- [ ] P00 human-reviewed
- [ ] P00 Evidence Index available

## Authority

- [ ] README and AGENTS agree
- [ ] one external product identity
- [ ] Moodify Music / Player is external product
- [ ] PLAY is first-stage primary user action
- [ ] Ear / Auditory Intelligence is internal
- [ ] no new parallel Canon created
- [ ] authority order is explicit

## Historical assets

- [ ] valuable old engineering assets preserved
- [ ] high-risk legacy docs are marked/reclassified
- [ ] historical docs cannot override current Canon

## PR #21

- [ ] compatibility report created
- [ ] PR not auto-merged
- [ ] engineering assets separated from old product prose

## Scope integrity

- [ ] no runtime behavior change
- [ ] no cloud deployment
- [ ] no DB mutation
- [ ] no OSS mutation
- [ ] no audio asset mutation
- [ ] no state-machine refactor

## Guardrails

- [ ] Canon drift guard implemented
- [ ] guard does not ban legitimate internal use of Ear terminology
- [ ] changelog complete
- [ ] unresolved items marked HUMAN_DECISION_REQUIRED

## Verification

- [ ] `git diff --check` passes
- [ ] relevant tests pass
- [ ] final report complete
- [ ] stop after P01
