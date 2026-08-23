# Unified Pipeline Architecture

```text
JobContext
   │
   ▼
ACQUIRE
   ▼
VALIDATE
   ▼
STEM? ────── optional
   ▼
ANALYZE
   ▼
JUDGE
   ├──── HUMAN_REVIEW_REQUIRED
   ├──── BYPASS
   ▼
INTERVENE?
   ▼
PROFILE
   ▼
RENDER
   ▼
VERIFY
   ├──── FAIL
   ├──── HUMAN_REVIEW_REQUIRED
   ▼
REGISTER
   ▼
CompletionCandidate
```

## Authority Boundary

Pipeline may:

- report stage
- register objects
- create evidence
- submit failure
- submit completion candidate

Pipeline may not:

- write READY directly
- reset retry budget
- create new Job identity
- replace Track/source identity
