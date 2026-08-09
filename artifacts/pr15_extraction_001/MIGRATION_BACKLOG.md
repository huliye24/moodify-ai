# PR #15 Selective Migration Backlog

| Order | Task ID | Goal | Source Assets | Target | Tests | Dependencies | Estimated PR Size | Rollback |
|---:|---|---|---|---|---|---|---|---|
| 1 | MFY-MIG-001 | Define four minimum contracts | bridge schemas, auditory manifests, production control | `moodify.contracts` | strict serialization, unknown-field rejection, hash/lineage invariants | none | S: <15 files | remove new package; no runtime consumer yet |
| 2 | MFY-MIG-002 | Extract source identity and WSE MeasurementRecord adapter | auditory decode/models/metrics/profiles | `moodify.auditory.source/representation` | synthetic WAV, method/profile version, deterministic hashes, no-ffmpeg pure subset plus ffmpeg integration | MIG-001 | M: <25 files | keep v0.1 analyzer active |
| 3 | MFY-MIG-003 | Extract before/after verification | auditory comparison/manifests/judgment | `moodify.auditory.verification` | pairing invariants, normalization, hash tamper, human escalation | MIG-001/002 | M | keep branch-only verifier |
| 4 | MFY-MIG-004 | Adopt one ProductionCase state machine | app production control, v2 approval tests | `moodify.production` | every legal/illegal transition, plan-hash approval, retry/reapproval, concurrency/version | MIG-001 | M | feature flag; v0.1 remains adapter |
| 5 | MFY-MIG-005 | Bind v0.1 DSP as intervention adapter | v01 pipeline/processing plus PR15 engine envelope | `moodify.auditory.intervention` | existing 109 tests plus envelope/rollback tests | MIG-002/004 | S/M | disable adapter registration |
| 6 | MFY-MIG-006 | Extract MSE score model | score engine pure model/MIDI/serialization | `moodify.structural` | MIDI fixtures, deterministic JSON, MusicXML roundtrip; optional MuseScore job | MIG-001 | M | package remains experimental and optional |
| 7 | MFY-MIG-007 | Establish learning/human-label store | learning rights/models and treatment records | `moodify.learning` | fail-closed rights, review gates, pairwise labels, provenance | MIG-001/003 | M | export-only mode; no production rules |
| 8 | MFY-MIG-008 | Define canonical public API | PR15 mobile API contracts and minimum Android needs | `moodify.api.v1` | OpenAPI snapshot, auth, upload, case, approval, evidence, errors | MIG-001/004 | M | retain old endpoints behind compatibility adapter |
| 9 | MFY-MIG-009 | Port Android connection/upload/case flow | Android repositories/models/tests | `apps/android` | JVM contract tests, mock server, physical-device smoke | MIG-008 | M | retain current demo build branch |
| 10 | MFY-MIG-010 | Consolidate runtime execution infrastructure | queue/scheduler/supervisor/failure concepts | `moodify.runtime` | lease, retry, crash recovery, idempotency, no product-state mutation | MIG-004/008 | M/L | deploy parallel shadow worker; old runtime remains off-main |
| 11 | MFY-MIG-011 | Archive extracted PR15 history and cleanup duplicates | generated artifacts, night packages, superseded systems | archive manifest / cleanup | reference/hash integrity and no-live-import scan | MIG-001–010 | S per cleanup PR | restore from PR #15 immutable branch/tag |

Every row is one reviewable PR. No task merges PR #15 wholesale.
