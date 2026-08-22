# Current Audio Capability Map

| Capability | Current Implementation | Runtime Verified | Canon Class | Input | Output | Version Identity | Failure Behavior | Decision |
|---|---|---:|---|---|---|---|---|---|

Allowed decisions:

- USE
- WRAP_WITH_ADAPTER
- KEEP_INTERNAL
- EXPERIMENTAL_ONLY
- LEGACY
- REPLACE_LATER
- HUMAN_DECISION_REQUIRED

## Required review areas

- current v0.1 pipeline
- FFmpeg
- stem/separation
- analysis
- Ear/judgment
- intervention/DSP
- profile/preset
- render
- verification
- external APIs
- PR #21 compute worker
