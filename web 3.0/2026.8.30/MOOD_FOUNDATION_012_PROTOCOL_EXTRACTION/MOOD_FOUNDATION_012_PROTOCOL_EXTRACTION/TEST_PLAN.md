# TEST PLAN

## Required invariants

### Foundation independence
Remove / unset future MOOD token config and verify:
- app foundation still loads/builds
- wallet still connects
- identity path still works
- contribution service still works

### Launch gate
For state `foundation`:
- no production DEX CTA
- no claim action
- no official future CA exposure

For invalid state:
- fail closed

### Contribution
Verify:
- task list
- submission
- review transitions
- resubmission
- reputation event creation
- pending reward recording
- zero blockchain write side effects

### Identity
Verify:
- address normalization
- nonce uniqueness / expiry if present
- human-readable signature message
- invalid signature rejection
- replay protection if implemented

### Regression
Do not break existing Moodify product routes unrelated to MOOD foundation.

## Evidence

Record exact commands + exit codes in:

```text
docs/mood/extraction/012_FINAL_REPORT.md
```
