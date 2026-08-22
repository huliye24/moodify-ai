# W10 Handoff

```text
W09_STATUS = PASS
W10_GATE = PASS
CANON_CHANGE = NO
VISUAL_REDESIGN = NO
```

Network/API client location: `src/services/api/client.ts` (`BffClient`), configured by `src/services/config/index.ts`. Existing catalogue/Track DTOs and remote playback methods exist, but no complete local-source-to-cloud-production capability has been verified by W09.

W10 may audit and implement a truthful Local Source → cloud request/preparation → Cloud-prepared Track → PLAY seam using existing Track/Playback/Queue/Recovery and native lifecycle. Public UI may expose only concise preparing/ready/play states. It must not expose Ear, stem, judge, intervene, evidence or an internal job graph, and must not claim unverified production/AI capability.
