"""Feature extraction facade (waveform, spectral, rhythm, timbre).

Phase T0.5: raw spectral/dynamics features are measured by
``engine.acoustic_analysis`` (delegating to the legacy core package).
This package re-exports the flat feature view for consumers and will
absorb migrated feature extractors in Phase B (T2+).
"""

from engine.acoustic_analysis.analyzer import AcousticProfile

__all__ = ["AcousticProfile"]
