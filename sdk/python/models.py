"""
Moodify SDK Data Models

Pydantic models for API request/response data.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Union


@dataclass
class AudioMetadata:
    """Audio file metadata."""
    duration: float  # seconds
    sample_rate: int  # Hz
    channels: int
    bit_depth: Optional[int] = None
    format: Optional[str] = None
    size_bytes: Optional[int] = None


@dataclass
class SpectralFeatures:
    """Spectral audio features."""
    centroid: Optional[float] = None  # Hz
    rolloff: Optional[float] = None  # Hz
    bandwidth: Optional[float] = None
    flatness: Optional[float] = None
    contrast: Optional[List[float]] = None


@dataclass
class TemporalFeatures:
    """Temporal audio features."""
    zero_crossing_rate: Optional[float] = None
    rms_energy: Optional[float] = None
    tempo: Optional[float] = None  # BPM


@dataclass
class AudioFeatures:
    """Complete audio feature set."""
    spectral: SpectralFeatures = field(default_factory=SpectralFeatures)
    temporal: TemporalFeatures = field(default_factory=TemporalFeatures)
    loudness: Optional[Dict[str, float]] = None  # LUFS values
    custom: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AudioAnalysisResult:
    """
    Result from audio analysis.

    Attributes:
        id: Unique analysis ID
        audio_path: Path to analyzed audio
        duration: Audio duration in seconds
        sample_rate: Sample rate in Hz
        features: Extracted audio features
        metadata: Additional metadata
        created_at: Analysis timestamp
    """
    id: str
    audio_path: str
    duration: float
    sample_rate: int
    features: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

    @property
    def spectral_centroid(self) -> Optional[float]:
        """Get spectral centroid if available."""
        return self.features.get("spectral", {}).get("centroid")

    @property
    def loudness_lufs(self) -> Optional[float]:
        """Get integrated loudness if available."""
        return self.features.get("loudness", {}).get("integrated")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "audio_path": self.audio_path,
            "duration": self.duration,
            "sample_rate": self.sample_rate,
            "features": self.features,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


@dataclass
class MRSResult:
    """
    Moodify Reconstruction Score result.

    Attributes:
        id: Unique evaluation ID
        audio_path: Path to evaluated audio
        overall: Overall MRS score (0-100)
        fidelity: Fidelity score (0-100)
        balance: Balance score (0-100)
        clarity: Clarity score (0-100)
        version: MRS algorithm version
        details: Additional scoring details
        created_at: Evaluation timestamp
    """
    id: str
    audio_path: str
    overall: float
    fidelity: float
    balance: float
    clarity: float
    version: str = "0.1.0"
    details: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

    @property
    def is_high_quality(self) -> bool:
        """Check if audio is high quality (score >= 80)."""
        return self.overall >= 80.0

    @property
    def is_acceptable(self) -> bool:
        """Check if audio is acceptable (score >= 60)."""
        return self.overall >= 60.0

    def get_recommendations(self) -> List[str]:
        """Get improvement recommendations based on scores."""
        recommendations = []

        if self.fidelity < 60:
            recommendations.append("Consider improving audio fidelity")
        if self.balance < 60:
            recommendations.append("Check frequency balance")
        if self.clarity < 60:
            recommendations.append("Review clarity and definition")

        return recommendations

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "audio_path": self.audio_path,
            "overall": self.overall,
            "fidelity": self.fidelity,
            "balance": self.balance,
            "clarity": self.clarity,
            "version": self.version,
            "details": self.details,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


@dataclass
class ProcessingResult:
    """
    Audio processing result.

    Attributes:
        id: Unique processing ID
        input_path: Path to input audio
        output_path: Path to processed audio
        operation: Processing operation performed
        status: Processing status ("pending", "processing", "completed", "failed")
        progress: Processing progress (0-100)
        metadata: Processing metadata
        error: Error message if failed
        created_at: Processing timestamp
        completed_at: Completion timestamp
    """
    id: str
    input_path: str
    output_path: str
    operation: str
    status: str = "pending"
    progress: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

    @property
    def is_completed(self) -> bool:
        """Check if processing is complete."""
        return self.status == "completed"

    @property
    def is_failed(self) -> bool:
        """Check if processing failed."""
        return self.status == "failed"

    @property
    def duration_seconds(self) -> Optional[float]:
        """Get processing duration if completed."""
        if self.completed_at and self.created_at:
            return (self.completed_at - self.created_at).total_seconds()
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "input_path": self.input_path,
            "output_path": self.output_path,
            "operation": self.operation,
            "status": self.status,
            "progress": self.progress,
            "metadata": self.metadata,
            "error": self.error,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


@dataclass
class BatchResult:
    """Result from batch operation."""
    id: str
    total_files: int
    processed_files: int
    failed_files: int
    results: List[Union[AudioAnalysisResult, MRSResult, ProcessingResult]]
    status: str
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_files == 0:
            return 0.0
        return (self.processed_files / self.total_files) * 100


@dataclass
class APIResponse:
    """Generic API response wrapper."""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    status_code: int = 200
    request_id: Optional[str] = None

    @classmethod
    def from_error(cls, error: str, status_code: int = 500) -> APIResponse:
        """Create error response."""
        return cls(success=False, error=error, status_code=status_code)

    @classmethod
    def from_data(cls, data: Any, status_code: int = 200) -> APIResponse:
        """Create success response."""
        return cls(success=True, data=data, status_code=status_code)
