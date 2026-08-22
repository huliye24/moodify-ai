# W01-P07 Handoff — Golden Song 001

P06 freezes the delivery contract.

P07 must not redesign:

- playback authorization
- delivery URL identity
- Android player architecture
- compute pipeline
- Job state machine
- object identity

unless a blocking defect is proven.

## P07 Input

- one authorized source audio
- known Track identity path
- working upload/data plane
- working control plane
- working compute pipeline
- READY semantics
- working delivery
- Android PLAY
- evidence templates

## P07 Question

> Can one real, familiar song travel through the entire Moodify system and produce a playback experience that is technically correct, audibly reviewable and fully traceable?

P07 rule:

**Only fix blockers for Golden Song 001. No feature expansion.**
