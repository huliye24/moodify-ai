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
    band_spec: str = "7"        # which band definition was used (AEP-ACU-004)
    rms_total: float = 0.0
    rms_sub: float = 0.0        # 20–60 Hz
    rms_bass: float = 0.0       # 60–250 Hz
    rms_low_mid: float = 0.0    # 250–500 Hz
    rms_mid: float = 0.0        # 500–2000 Hz
    rms_presence: float = 0.0   # 2000–5000 Hz
    rms_brilliance: float = 0.0 # 5000–8000 Hz (AEP-ACU-004)
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
                "brilliance": round(self.rms_brilliance, 1),
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
class ScanResult:
    """Input audio scan result before musical diagnosis.

    v0.2 (MHP-864): Added 6 acoustic surface fields.
    All new fields are Optional/zero-default for backwards compatibility.
    """

    # -- v0.1 file-level fields --
    input_path: str = ""
    exists: bool = False
    extension: str = ""
    file_size_bytes: int = 0
    readable: bool = False
    warnings: list[str] = field(default_factory=list)

    # -- v0.2 acoustic surface fields (MHP-851 / MHP-864) --
    loudness_lufs: float | None = None          # Integrated LUFS (ITU-R BS.1770 approx)
    transient_ratio: float | None = None         # Peak-to-moving-RMS ratio
    stereo_width: float | None = None            # Side-to-mid energy ratio (0–1)
    spectral_centroid_hz: float | None = None    # Weighted mean frequency (Hz)
    dc_offset: float | None = None               # Signal mean / full-scale
    clip_count: int = 0                          # Samples at digital ceiling (±1.0)

    def to_dict(self) -> dict:
        result: dict = {
            "input_path": self.input_path,
            "exists": self.exists,
            "extension": self.extension,
            "file_size_bytes": self.file_size_bytes,
            "readable": self.readable,
            "warnings": self.warnings,
        }
        # Include acoustic fields only when populated
        if self.loudness_lufs is not None:
            result["loudness_lufs"] = round(self.loudness_lufs, 1)
        if self.transient_ratio is not None:
            result["transient_ratio"] = round(self.transient_ratio, 2)
        if self.stereo_width is not None:
            result["stereo_width"] = round(self.stereo_width, 3)
        if self.spectral_centroid_hz is not None:
            result["spectral_centroid_hz"] = round(self.spectral_centroid_hz, 0)
        if self.dc_offset is not None:
            result["dc_offset"] = round(self.dc_offset, 6)
        if self.clip_count > 0:
            result["clip_count"] = self.clip_count
        return result


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
class QualityGate:
    """Before/after safety checks for a processed file."""

    passed: bool = True
    warnings: list[str] = field(default_factory=list)
    deltas: dict = field(default_factory=dict)
    mrs_version: str = "mrs_proxy_v01"
    mrs_before: float = 0.0
    mrs_after: float = 0.0
    mrs_delta: float = 0.0
    damage_loss: float = 0.0
    risk_flags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "warnings": self.warnings,
            "deltas": self.deltas,
            "mrs_version": self.mrs_version,
            "mrs_before": round(self.mrs_before, 2),
            "mrs_after": round(self.mrs_after, 2),
            "mrs_delta": round(self.mrs_delta, 2),
            "damage_loss": round(self.damage_loss, 3),
            "risk_flags": self.risk_flags,
        }


@dataclass
class DeliveryBundle:
    """Files produced by one pipeline run.

    v0.2 (MHP-875/876): Added manifest, metadata, environment, validation report,
    MAP_CHAIN_VERSION, and processing log paths.
    """

    # -- v0.1 fields --
    output_audio: str = ""
    json_report: str = ""
    pdf_report: str = ""
    spectrum_before: str = ""
    spectrum_after: str = ""

    # -- v0.2 MAP delivery (MHP-875/876) --
    manifest: str = ""               # manifest.json artifact inventory
    metadata: str = ""               # metadata.json reproducibility metadata
    environment: str = ""            # environment.txt dependency listing
    validation_report: str = ""      # validation_report.json standalone
    version_file: str = ""           # MAP_CHAIN_VERSION file

    def to_dict(self) -> dict:
        result: dict = {
            "output_audio": self.output_audio,
            "json_report": self.json_report,
            "pdf_report": self.pdf_report,
            "spectrum_before": self.spectrum_before,
            "spectrum_after": self.spectrum_after,
        }
        # Include v0.2 fields only when populated
        if self.manifest:
            result["manifest"] = self.manifest
        if self.metadata:
            result["metadata"] = self.metadata
        if self.environment:
            result["environment"] = self.environment
        if self.validation_report:
            result["validation_report"] = self.validation_report
        if self.version_file:
            result["version_file"] = self.version_file
        return result


@dataclass
class ProcessResult:
    """Result of a v0.1.0 pipeline run."""

    input_path: str = ""
    output_path: str = ""
    preset: str = ""
    requested_preset: str = ""
    report_path: str = ""
    scan: ScanResult = field(default_factory=ScanResult)
    metrics_before: AudioMetrics = field(default_factory=AudioMetrics)
    metrics_after: AudioMetrics = field(default_factory=AudioMetrics)
    diagnosis: DiagnosisReport = field(default_factory=DiagnosisReport)
    quality_gate: QualityGate = field(default_factory=QualityGate)
    delivery: DeliveryBundle = field(default_factory=DeliveryBundle)
    stage_timings: dict = field(default_factory=dict)
    success: bool = False
    error: str = ""


# ═══════════════════════════════════════════════════════════════════════════
# MAP v0.2 Data Model (MHP-863)
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class FeatureVector:
    """MAP 8-D feature vector derived from AudioMetrics.

    MHP-852 / MHP-863: All dimensions clamped to [0, 1].
    Used for genre-weighted distance comparisons.
    """

    bass_balance: float = 0.0     # b: sub/bass energy balance
    warmth: float = 0.0           # w: low-mid body
    clarity: float = 0.0          # c: mid-range intelligibility
    presence_energy: float = 0.0  # p: vocal presence
    density: float = 0.0          # d: waveform fullness (inverse crest)
    stereo_width: float = 0.0     # s: 0=mono, 1=wide
    transient_energy: float = 0.0 # t: attack/punch
    reality_index: float = 0.0    # r: naturalness of dynamics

    def to_list(self) -> list[float]:
        return [
            self.bass_balance,
            self.warmth,
            self.clarity,
            self.presence_energy,
            self.density,
            self.stereo_width,
            self.transient_energy,
            self.reality_index,
        ]

    def to_dict(self) -> dict:
        return {
            "bass_balance": round(self.bass_balance, 4),
            "warmth": round(self.warmth, 4),
            "clarity": round(self.clarity, 4),
            "presence_energy": round(self.presence_energy, 4),
            "density": round(self.density, 4),
            "stereo_width": round(self.stereo_width, 4),
            "transient_energy": round(self.transient_energy, 4),
            "reality_index": round(self.reality_index, 4),
        }


# -- Genre weight vectors (MHP-852) --
GENRE_WEIGHTS: dict[str, list[float]] = {
    "vocal":       [0.7, 1.0, 1.0, 1.0, 0.6, 0.5, 0.5, 0.8],
    "piano":       [0.8, 0.8, 0.9, 0.6, 0.5, 0.3, 0.9, 1.0],
    "electronic":  [1.0, 0.6, 0.7, 0.8, 0.9, 0.9, 0.7, 0.4],
    "orchestral":  [0.8, 0.8, 0.7, 0.5, 0.4, 0.7, 0.6, 1.0],
    "default":     [0.8, 0.8, 0.8, 0.8, 0.7, 0.6, 0.7, 0.8],
}


@dataclass
class ProblemEntry:
    """A single diagnosed problem with severity and confidence.

    MHP-853 / MHP-863: Structured problem representation for
    machine-actionable diagnosis.
    """

    problem_id: str = ""       # e.g. "over_compressed", "bass_forward"
    category: str = ""         # "spectral" | "dynamics" | "stereo" | "overall"
    severity: str = "low"      # "low" | "medium" | "high"
    confidence: float = 0.0    # 0.0–1.0, from threshold distance
    weight: float = 0.0        # MAP weight for diagnosis_loss
    description: str = ""      # human-readable

    def to_dict(self) -> dict:
        return {
            "problem_id": self.problem_id,
            "category": self.category,
            "severity": self.severity,
            "confidence": round(self.confidence, 3),
            "weight": round(self.weight, 2),
            "description": self.description,
        }


@dataclass
class ProblemVector:
    """Collection of diagnosed problems with aggregate loss.

    MHP-853 / MHP-863: Feeds MAP D→P→V linkage.
    diagnosis_loss = min(1.0, sum(p.weight * p.confidence) / 10.0).
    """

    problems: list[ProblemEntry] = field(default_factory=list)
    diagnosis_loss: float = 0.0

    def to_dict(self) -> dict:
        return {
            "problem_count": len(self.problems),
            "diagnosis_loss": round(self.diagnosis_loss, 3),
            "problems": [p.to_dict() for p in self.problems],
        }

    @property
    def high_severity_count(self) -> int:
        return sum(1 for p in self.problems if p.severity == "high")

    @property
    def medium_severity_count(self) -> int:
        return sum(1 for p in self.problems if p.severity == "medium")
