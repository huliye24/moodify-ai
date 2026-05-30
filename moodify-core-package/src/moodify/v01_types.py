"""v01_types.py — Moodify v0.1.0 lightweight data structures.

Single source of truth for the v0.1.0 mainline.
Does NOT depend on data_types.py (which carries v1.5+ weight).
"""

from dataclasses import dataclass, field


@dataclass
class AudioMetrics:
    """Basic audio measurements from a single file."""

    file_path: str = ""
    duration_s: float = 0.0
    sample_rate: int = 44100
    channels: int = 2

    # Spectrum (dB)
    rms_total: float = 0.0
    rms_sub: float = 0.0        # 20–60 Hz
    rms_bass: float = 0.0       # 60–250 Hz
    rms_low_mid: float = 0.0    # 250–500 Hz
    rms_mid: float = 0.0        # 500–2000 Hz
    rms_presence: float = 0.0   # 2000–5000 Hz
    rms_air: float = 0.0        # 8000–16000 Hz

    # Dynamics
    peak_db: float = 0.0
    crest_factor: float = 0.0   # peak / rms ratio
    dynamic_range_db: float = 0.0

    # Stereo
    correlation_lr: float = 0.0

    def to_dict(self) -> dict:
        return {
            "file_path": self.file_path,
            "duration_s": round(self.duration_s, 1),
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "spectrum": {
                "sub_bass": round(self.rms_sub, 1),
                "bass": round(self.rms_bass, 1),
                "low_mid": round(self.rms_low_mid, 1),
                "mid": round(self.rms_mid, 1),
                "presence": round(self.rms_presence, 1),
                "air": round(self.rms_air, 1),
            },
            "dynamics": {
                "peak_db": round(self.peak_db, 1),
                "crest_factor": round(self.crest_factor, 2),
                "dynamic_range_db": round(self.dynamic_range_db, 1),
            },
            "stereo": {
                "correlation_lr": round(self.correlation_lr, 3),
            },
        }


@dataclass
class DiagnosisReport:
    """Human-readable audio diagnosis."""

    metrics: AudioMetrics = field(default_factory=AudioMetrics)
    overall_health: str = "fair"       # good / fair / poor
    issues: list[str] = field(default_factory=list)
    strengths: list[str] = field(default_factory=list)
    suggested_presets: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "overall_health": self.overall_health,
            "issues": self.issues,
            "strengths": self.strengths,
            "suggested_presets": self.suggested_presets,
            "metrics": self.metrics.to_dict(),
        }


@dataclass
class ProcessResult:
    """Result of a v0.1.0 pipeline run."""

    input_path: str = ""
    output_path: str = ""
    preset: str = ""
    metrics_before: AudioMetrics = field(default_factory=AudioMetrics)
    diagnosis: DiagnosisReport = field(default_factory=DiagnosisReport)
    success: bool = False
    error: str = ""
