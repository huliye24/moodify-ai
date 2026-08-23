"""Moodify Intelligence Engine — Shared AI auditory capability layer.

All Moodify products (QA, Master, Rating, Supply) build on this engine.
The engine provides pure analysis functions with no product-specific logic.

Modules:
    acoustic_analysis   — Acoustic measurement (LUFS, spectrum, stereo, dynamics)
    audio_features      — Feature extraction (waveform, spectral, rhythm, timbre)
    music_understanding — Musical semantics (structure, emotion, genre, instruments)
    scoring_engine      — Scoring (MRS, quality scores, uncertainty)
    recommendation_engine — Matching (similarity, scene, preference, ranking)

Migration Status: Phase B T0.5 — analysis facade live (delegates to the legacy
``moodify-core-package`` implementation), unified Intelligence Report schema
published (engine/report_schema). Full module migration continues in Phase B.
See docs/MOODIFY_ARCHITECTURE_V1.md and docs/MOODIFY_DEMO_PIPELINE.md.
"""

__version__ = "0.1.0"
__status__ = "PHASE_B_T0_5_FACADE_LIVE"
