# Current Repository Capabilities

This inventory describes verified current-worktree evidence. It does not promote
material proposals, branch-only systems, or historical documentation.

## Verification

The current v0.1 marker suite completed with **20 passed, 5 skipped, 575
deselected, and 5 warnings**. The five warnings concern Matplotlib tight-layout
behavior. A broader suite attempt exceeded the 120-second command boundary and
is not presented as passing evidence.

| Capability | Status | Evidence boundary |
|---|---|---|
| Audio ingest | CANONICAL | `audio_io.py`; v0.1 tests |
| Wave/spectral analysis | CANONICAL | `v01_analyzer.py`; analyzer tests |
| Diagnosis | CANONICAL | `v01_diagnostics.py`; diagnostics tests |
| Controlled intervention / DSP | CANONICAL | `v01_pipeline.py`, pedalboard chain; pipeline tests |
| Before/after verification | EXPERIMENTAL | No single canonical comparison contract |
| Treatment records | EXPERIMENTAL | Records and aggregation utilities |
| Human feedback | EXPERIMENTAL | Feedback fields/workflows, not canonical learning |
| Production-case state machine | LEGACY | Preserved `workflow_engine.py` |
| MSE structural analysis | ABSENT | No canonical subsystem |
| Cloud runtime | UNRESOLVED | Wider systems are not current authority |
| App integration | UNRESOLVED | Historical/branch context is insufficient |

The batch controller under `ops/ear_batch` is an operations aid and deliberately
does not alter any of these authority classifications.
