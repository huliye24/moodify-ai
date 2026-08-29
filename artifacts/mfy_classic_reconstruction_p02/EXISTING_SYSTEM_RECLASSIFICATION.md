# MFY-CR-P02 — Existing System Reclassification

How existing systems are classified in the new phase (recorded formally in
`docs/CLASSIC_RECONSTRUCTION_CONSTITUTION.md` Article III / IX and
`docs/STEREO_FIRST_POLICY.md` §6).

| Existing System | New Role | Status |
|---|---|---|
| Auditory Core (`moodify.auditory`) | Internal intelligence (Ear) | CANONICAL — unchanged code |
| WSE | Measurement / acoustic understanding | CANONICAL — internal |
| MSE | Musical structure / identity context | CANONICAL — internal (research) |
| PPE | Reproducible reconstruction process | CANONICAL — internal |
| Data Factory (`moodify.data_factory`) | Reconstruction learning factory | CANONICAL — internal |
| Pedalboard Chain | Intervention mechanism | CANONICAL — internal mechanism, subject to decision model |
| LALAL (`moodify.stems`) | Optional external stem service | SUPPORTED_EXTERNAL — stereo-first policy governs invocation |
| Audiolla | Optional reconstruction toolset | SUPPORTED_EXTERNAL — evidence on LA host |
| Android (`apps/music-android`, `apps/android`) | Listening Environment client | CANONICAL — public surface; UI untouched in P02 |
| Node / Worker (`moodify.node`, `ops/data_node`) | Reconstruction execution infrastructure | CANONICAL — unchanged |
| Human Review | Artistic authority / calibration | CANONICAL — unchanged; machines never hold final artistic authority |

## Boundary guarantees

- No existing system was deleted, renamed or re-scoped in P02.
- The reclassification above is documentation only; no code changes.
- External services (LALAL/Audiolla) never define the product identity and
  never bypass the decision model.
