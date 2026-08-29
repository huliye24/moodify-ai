# W01-P08 Handoff — 3 → 10 Song Pilot

P08 receives one validated Golden Case.

It must not assume all songs behave the same.

## Inputs

- Golden Source identity
- successful run identity
- pipeline version
- blocker history
- compute cost/time
- failure history
- listening verdict
- playback evidence
- regression baseline
- open non-blocking issues

## P08 question

> Does the same architecture remain correct when expanded from 1 song to 3, then 10?

## P08 sequence

```text
1 Golden Song
   ↓
3-song smoke pilot
   ↓ gate
10-song pilot
```

Do not jump directly to 10 if the 3-song gate fails.
