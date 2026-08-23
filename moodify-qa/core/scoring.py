"""QA Scoring model - Moodify QA Score v0.1.

Scoring dimensions:
- Technical Quality: Loudness, Dynamics, Clipping, Noise, Stereo
- Musical Quality: Balance, Frequency Distribution, Energy Curve

Output: QA Score 0-100 with issues and recommendations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class IssueSeverity(str, Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


@dataclass
class QAIssue:
    """Detected quality issue."""

    category: str
    severity: IssueSeverity
    message: str
    metric: str
    value: float | None = None
    threshold: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "category": self.category,
            "severity": self.severity.value,
            "message": self.message,
            "metric": self.metric,
            "value": self.value,
            "threshold": self.threshold,
        }


@dataclass
class QARecommendation:
    """Recommendation for issue remediation."""

    issue_category: str
    priority: int
    action: str
    details: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "issue_category": self.issue_category,
            "priority": self.priority,
            "action": self.action,
            "details": self.details,
        }


@dataclass
class QAScoreBreakdown:
    """Detailed score breakdown by category."""

    technical_score: float = 0.0
    musical_score: float = 0.0

    # Technical sub-scores
    loudness_score: float = 0.0
    dynamics_score: float = 0.0
    clipping_score: float = 0.0
    noise_score: float = 0.0
    stereo_score: float = 0.0

    # Musical sub-scores
    balance_score: float = 0.0
    frequency_score: float = 0.0
    energy_score: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "technical": {
                "overall": self.technical_score,
                "loudness": self.loudness_score,
                "dynamics": self.dynamics_score,
                "clipping": self.clipping_score,
                "noise": self.noise_score,
                "stereo": self.stereo_score,
            },
            "musical": {
                "overall": self.musical_score,
                "balance": self.balance_score,
                "frequency": self.frequency_score,
                "energy": self.energy_score,
            },
        }


@dataclass
class QAScoringResult:
    """Complete QA scoring result."""

    track: str
    qa_score: float
    technical_score: float
    musical_score: float
    issues: list[QAIssue] = field(default_factory=list)
    recommendations: list[QARecommendation] = field(default_factory=list)
    breakdown: QAScoreBreakdown = field(default_factory=QAScoreBreakdown)

    def to_dict(self) -> dict[str, Any]:
        return {
            "track": self.track,
            "qa_score": round(self.qa_score, 1),
            "technical_score": round(self.technical_score, 1),
            "musical_score": round(self.musical_score, 1),
            "issues": [i.to_dict() for i in self.issues],
            "recommendations": [r.to_dict() for r in self.recommendations],
            "breakdown": self.breakdown.to_dict(),
        }


class QAScorer:
    """Moodify QA Score calculator v0.1.

    Scoring weights:
    - Technical Quality: 60%
      - Loudness: 15%
      - Dynamics: 15%
      - Clipping: 15%
      - Noise: 10%
      - Stereo: 5%
    - Musical Quality: 40%
      - Balance: 15%
      - Frequency Distribution: 15%
      - Energy Curve: 10%
    """

    # Target values (industry standards)
    TARGET_LUFS = -14.0  # Streaming target
    TARGET_LUFS_TOLERANCE = 2.0
    TARGET_TRUE_PEAK = -1.0
    TARGET_DYNAMIC_RANGE_MIN = 8.0  # dB
    TARGET_CREST_FACTOR_MIN = 6.0  # dB
    TARGET_LRA_MIN = 4.0  # LU
    TARGET_LRA_MAX = 12.0  # LU

    def __init__(self):
        self.issues: list[QAIssue] = []
        self.recommendations: list[QARecommendation] = []

    def score(self, analysis_result) -> QAScoringResult:
        """Calculate QA score from analysis result."""
        from moodify_qa.core.analyzer import AudioAnalysisResult

        if not isinstance(analysis_result, AudioAnalysisResult):
            raise TypeError("Expected AudioAnalysisResult")

        self.issues = []
        self.recommendations = []

        # Calculate sub-scores
        breakdown = QAScoreBreakdown()

        # Technical scores
        breakdown.loudness_score = self._score_loudness(analysis_result)
        breakdown.dynamics_score = self._score_dynamics(analysis_result)
        breakdown.clipping_score = self._score_clipping(analysis_result)
        breakdown.noise_score = self._score_noise(analysis_result)
        breakdown.stereo_score = self._score_stereo(analysis_result)

        # Musical scores
        breakdown.balance_score = self._score_balance(analysis_result)
        breakdown.frequency_score = self._score_frequency(analysis_result)
        breakdown.energy_score = self._score_energy(analysis_result)

        # Weighted totals
        breakdown.technical_score = (
            breakdown.loudness_score * 0.25 +
            breakdown.dynamics_score * 0.25 +
            breakdown.clipping_score * 0.25 +
            breakdown.noise_score * 0.15 +
            breakdown.stereo_score * 0.10
        )

        breakdown.musical_score = (
            breakdown.balance_score * 0.40 +
            breakdown.frequency_score * 0.35 +
            breakdown.energy_score * 0.25
        )

        # Overall QA Score (0-100)
        qa_score = breakdown.technical_score * 0.6 + breakdown.musical_score * 0.4

        # Sort recommendations by priority
        self.recommendations.sort(key=lambda r: r.priority)

        return QAScoringResult(
            track=analysis_result.filename,
            qa_score=qa_score,
            technical_score=breakdown.technical_score,
            musical_score=breakdown.musical_score,
            issues=self.issues,
            recommendations=self.recommendations,
            breakdown=breakdown,
        )

    def _score_loudness(self, result) -> float:
        """Score loudness quality (0-100)."""
        lufs = result.loudness.integrated_lufs

        # Distance from target
        distance = abs(lufs - self.TARGET_LUFS)

        if distance <= self.TARGET_LUFS_TOLERANCE:
            score = 100.0
        elif distance <= 5.0:
            score = 80.0
        elif distance <= 10.0:
            score = 60.0
        else:
            score = 40.0

        # Issue detection
        if lufs > -9.0:
            self.issues.append(QAIssue(
                category="loudness",
                severity=IssueSeverity.WARNING,
                message=f"Audio is very loud ({lufs:.1f} LUFS). May cause listener fatigue.",
                metric="integrated_lufs",
                value=lufs,
                threshold=-9.0,
            ))
            self.recommendations.append(QARecommendation(
                issue_category="loudness",
                priority=2,
                action="Reduce overall loudness",
                details=f"Current: {lufs:.1f} LUFS. Target: {self.TARGET_LUFS} LUFS. Consider reducing gain by {lufs - self.TARGET_LUFS:.1f} dB.",
            ))
        elif lufs < -20.0:
            self.issues.append(QAIssue(
                category="loudness",
                severity=IssueSeverity.INFO,
                message=f"Audio is quiet ({lufs:.1f} LUFS). May be too soft for some platforms.",
                metric="integrated_lufs",
                value=lufs,
                threshold=-20.0,
            ))

        return score

    def _score_dynamics(self, result) -> float:
        """Score dynamic range quality (0-100)."""
        dr = result.dynamics.dynamic_range_db
        lra = result.loudness.loudness_range_lu or 0
        crest = result.dynamics.crest_factor_db

        # Combined dynamic quality
        scores = []

        # Dynamic range score
        if dr >= 12:
            scores.append(100.0)
        elif dr >= 8:
            scores.append(80.0)
        elif dr >= 6:
            scores.append(60.0)
        else:
            scores.append(40.0)
            self.issues.append(QAIssue(
                category="dynamics",
                severity=IssueSeverity.WARNING,
                message=f"Low dynamic range ({dr:.1f} dB). Audio may sound compressed.",
                metric="dynamic_range_db",
                value=dr,
                threshold=self.TARGET_DYNAMIC_RANGE_MIN,
            ))
            self.recommendations.append(QARecommendation(
                issue_category="dynamics",
                priority=1,
                action="Increase dynamic range",
                details=f"Current: {dr:.1f} dB. Target: >{self.TARGET_DYNAMIC_RANGE_MIN} dB. Reduce compression or use parallel processing.",
            ))

        # LRA score
        if lra >= 6:
            scores.append(100.0)
        elif lra >= 4:
            scores.append(80.0)
        else:
            scores.append(50.0)

        # Crest factor score
        if crest >= 10:
            scores.append(100.0)
        elif crest >= 6:
            scores.append(80.0)
        else:
            scores.append(50.0)

        return sum(scores) / len(scores)

    def _score_clipping(self, result) -> float:
        """Score clipping quality (0-100)."""
        clip_ratio = result.integrity.clipping_ratio
        tp = result.peaks.true_peak_dbfs

        if clip_ratio > 0:
            score = max(0, 100 - (clip_ratio * 10000))
            self.issues.append(QAIssue(
                category="clipping",
                severity=IssueSeverity.CRITICAL,
                message=f"Clipping detected ({result.integrity.clipping_sample_count} samples, {clip_ratio:.6%}).",
                metric="clipping_ratio",
                value=clip_ratio,
                threshold=0.0,
            ))
            self.recommendations.append(QARecommendation(
                issue_category="clipping",
                priority=1,
                action="Remove clipping artifacts",
                details=f"{result.integrity.clipping_sample_count} samples clipped. Use soft clipping or reduce input gain.",
            ))
        elif tp > -0.5:
            score = 70.0
            self.issues.append(QAIssue(
                category="clipping",
                severity=IssueSeverity.WARNING,
                message=f"True peak very high ({tp:.1f} dBFS). Risk of inter-sample clipping.",
                metric="true_peak_dbfs",
                value=tp,
                threshold=-1.0,
            ))
        elif tp > -1.0:
            score = 85.0
        else:
            score = 100.0

        return score

    def _score_noise(self, result) -> float:
        """Score noise floor quality (0-100)."""
        noise_floor = result.integrity.noise_floor_dbfs

        if noise_floor > -50:
            score = 50.0
            self.issues.append(QAIssue(
                category="noise",
                severity=IssueSeverity.WARNING,
                message=f"High noise floor ({noise_floor:.1f} dBFS). Significant background noise.",
                metric="noise_floor_dbfs",
                value=noise_floor,
                threshold=-50.0,
            ))
            self.recommendations.append(QARecommendation(
                issue_category="noise",
                priority=3,
                action="Reduce noise floor",
                details=f"Current: {noise_floor:.1f} dBFS. Consider noise reduction or better recording environment.",
            ))
        elif noise_floor > -60:
            score = 75.0
        elif noise_floor > -70:
            score = 90.0
        else:
            score = 100.0

        return score

    def _score_stereo(self, result) -> float:
        """Score stereo quality (0-100)."""
        if not result.stereo.available:
            return 100.0  # Mono is valid

        corr = result.stereo.correlation
        phase_risk = result.stereo.phase_risk_ratio

        score = 100.0

        # Correlation issues
        if corr < 0:
            score -= 30
            self.issues.append(QAIssue(
                category="stereo",
                severity=IssueSeverity.CRITICAL,
                message=f"Negative correlation ({corr:.2f}). Phase issues likely.",
                metric="stereo_correlation",
                value=corr,
                threshold=0.0,
            ))
            self.recommendations.append(QARecommendation(
                issue_category="stereo",
                priority=1,
                action="Fix phase issues",
                details="Negative correlation detected. Check for phase cancellation or polarity inversion.",
            ))
        elif corr < 0.5:
            score -= 15
            self.issues.append(QAIssue(
                category="stereo",
                severity=IssueSeverity.WARNING,
                message=f"Low correlation ({corr:.2f}). Weak stereo image.",
                metric="stereo_correlation",
                value=corr,
                threshold=0.5,
            ))

        # Phase risk
        if phase_risk > 0.1:
            score -= 20
            self.issues.append(QAIssue(
                category="stereo",
                severity=IssueSeverity.WARNING,
                message=f"Phase risk detected ({phase_risk:.1%} of frames).",
                metric="phase_risk_ratio",
                value=phase_risk,
                threshold=0.1,
            ))

        return max(0, score)

    def _score_balance(self, result) -> float:
        """Score frequency balance (0-100)."""
        ratios = result.spectral.band_ratios

        if not ratios:
            return 50.0

        # Check for extreme imbalances
        bass = ratios.get("bass_60_120_hz", 0) + ratios.get("sub_20_60_hz", 0)
        mid = ratios.get("mid_250_500_hz", 0) + ratios.get("core_mid_500_2000_hz", 0)
        high = ratios.get("presence_2000_5000_hz", 0) + ratios.get("brilliance_5000_10000_hz", 0)

        score = 100.0

        # Bass-heavy
        if bass > 0.4:
            score -= 20
            self.issues.append(QAIssue(
                category="balance",
                severity=IssueSeverity.WARNING,
                message=f"Heavy bass content ({bass:.1%}). May sound muddy.",
                metric="bass_ratio",
                value=bass,
                threshold=0.4,
            ))
            self.recommendations.append(QARecommendation(
                issue_category="balance",
                priority=2,
                action="Reduce low-end energy",
                details=f"Bass content is {bass:.1%}. Consider high-pass filtering or EQ reduction below 120Hz.",
            ))

        # High-heavy
        if high > 0.3:
            score -= 15
            self.issues.append(QAIssue(
                category="balance",
                severity=IssueSeverity.WARNING,
                message=f"Bright mix ({high:.1%}). May sound harsh.",
                metric="high_ratio",
                value=high,
                threshold=0.3,
            ))
            self.recommendations.append(QARecommendation(
                issue_category="balance",
                priority=3,
                action="Tame high frequencies",
                details="Excessive high-frequency energy. Consider gentle shelving EQ above 5kHz.",
            ))

        # Thin mix
        if mid < 0.2:
            score -= 15
            self.issues.append(QAIssue(
                category="balance",
                severity=IssueSeverity.INFO,
                message="Thin midrange. May lack body.",
                metric="mid_ratio",
                value=mid,
                threshold=0.2,
            ))

        return max(0, score)

    def _score_frequency(self, result) -> float:
        """Score frequency distribution (0-100)."""
        flatness = result.spectral.flatness
        centroid = result.spectral.centroid_hz
        cutoff = result.spectral.high_freq_cutoff_hz

        score = 100.0

        # Flatness indicates tonal vs noisy
        if flatness > 0.3:
            score -= 20
            self.issues.append(QAIssue(
                category="frequency",
                severity=IssueSeverity.INFO,
                message=f"High spectral flatness ({flatness:.3f}). May lack tonal character.",
                metric="spectral_flatness",
                value=flatness,
                threshold=0.3,
            ))

        # Check if audio is band-limited
        if cutoff < 15000:
            score -= 10
            self.issues.append(QAIssue(
                category="frequency",
                severity=IssueSeverity.INFO,
                message=f"Limited high-frequency content (cutoff at {cutoff:.0f} Hz).",
                metric="high_freq_cutoff_hz",
                value=cutoff,
                threshold=15000.0,
            ))

        return max(0, score)

    def _score_energy(self, result) -> float:
        """Score energy curve quality (0-100)."""
        silence_ratio = result.integrity.silence_ratio
        longest_silence = result.integrity.longest_silence_seconds

        score = 100.0

        # Excessive silence
        if silence_ratio > 0.3:
            score -= 30
            self.issues.append(QAIssue(
                category="energy",
                severity=IssueSeverity.WARNING,
                message=f"High silence ratio ({silence_ratio:.1%}).",
                metric="silence_ratio",
                value=silence_ratio,
                threshold=0.3,
            ))
            self.recommendations.append(QARecommendation(
                issue_category="energy",
                priority=3,
                action="Review silent sections",
                details=f"{silence_ratio:.1%} of audio is silent. Consider trimming or fade handling.",
            ))

        # Long silence gaps
        if longest_silence > 2.0:
            score -= 15
            self.issues.append(QAIssue(
                category="energy",
                severity=IssueSeverity.INFO,
                message=f"Long silence gap detected ({longest_silence:.1f}s).",
                metric="longest_silence_seconds",
                value=longest_silence,
                threshold=2.0,
            ))

        return max(0, score)
