# Evidence Contract Map

| Concept | PR #15 candidates | Strength | Problem | Decision |
|---|---|---|---|---|
| ProductionCase | `app.production_control.ProductionCase`, `domain.ProjectWorkflow`, bridge `ProductionCase`, runtime jobs | state invariants in app; strict lineage in bridge | duplicate identities and lifecycle meanings | Use production-control lifecycle plus extracted bridge identity fields |
| MeasurementRecord | bridge schema, `protocol.py`, capability-registry knowledge, auditory metric dictionaries | bridge has method/version/units; auditory has status/warnings/profile | four incompatible shapes | Extract a smaller typed record with explicit method and provenance |
| EvidenceArtifact | auditory manifests, bridge `EvidencePacket`, app `evidence.py`, runtime craft/data assets | hashes and case linkage exist | path leakage, mixed artifact/bundle meanings | Canonical immutable artifact reference plus separate bundle index |
| Rule | bridge `MoodifyRule`, capability policy proposals, runtime craft rules | version/state/provenance ideas | production state claimed without one acceptance authority | Canonical rule lifecycle tied to evidence and human acceptance |
| Human feedback | learning `HumanListeningEvaluation`, bridge HumanObservation/Approval | explicit human authority | feedback, approval, and label can be conflated | Preserve separate record types and actor/context |

`moodify-bridge/schemas.py` is the best schema source but is too broad and path-centric to cherry-pick unchanged. Extract concepts into a small dependency-light contract package.
