"""Auditory scan error taxonomy (DSK-MFY-AUDITORY-SCAN-001).

Every failure carries a stable code, a human message, case/candidate ids,
the failed operation, timestamp, recoverability and optional cause.
"""

from __future__ import annotations

from datetime import datetime, timezone


class AuditoryError(Exception):
    code = "AUDITORY_ERROR"

    def __init__(
        self,
        message: str,
        *,
        case_id: str | None = None,
        candidate_id: str | None = None,
        operation: str | None = None,
        recoverable: bool = False,
        cause: Exception | None = None,
    ) -> None:
        self.message = message
        self.case_id = case_id
        self.candidate_id = candidate_id
        self.operation = operation
        self.recoverable = recoverable
        self.timestamp = datetime.now(timezone.utc).isoformat()
        super().__init__(message)
        if cause is not None:
            self.__cause__ = cause

    def to_dict(self) -> dict:
        return {
            "error_code": self.code,
            "message": self.message,
            "case_id": self.case_id,
            "candidate_id": self.candidate_id,
            "operation": self.operation,
            "timestamp": self.timestamp,
            "recoverable": self.recoverable,
        }


class AuditoryScanInputNotFound(AuditoryError):
    code = "AUDITORY_SCAN_INPUT_NOT_FOUND"


class FfmpegNotFound(AuditoryError):
    code = "FFMPEG_NOT_FOUND"


class FfprobeNotFound(AuditoryError):
    code = "FFPROBE_NOT_FOUND"


class AudioDecodeFailed(AuditoryError):
    code = "AUDIO_DECODE_FAILED"


class AudioEmpty(AuditoryError):
    code = "AUDIO_EMPTY"


class AudioInvalidSamples(AuditoryError):
    code = "AUDIO_INVALID_SAMPLES"


class SpectrogramGenerationFailed(AuditoryError):
    code = "SPECTROGRAM_GENERATION_FAILED"


class MetricsComputationFailed(AuditoryError):
    code = "METRICS_COMPUTATION_FAILED"


class ScanProfileNotFound(AuditoryError):
    code = "SCAN_PROFILE_NOT_FOUND"


class ScanProfileMismatch(AuditoryError):
    code = "SCAN_PROFILE_MISMATCH"


class CandidateNotRegistered(AuditoryError):
    code = "CANDIDATE_NOT_REGISTERED"


class CandidateHashMismatch(AuditoryError):
    code = "CANDIDATE_HASH_MISMATCH"


class ComparisonDurationMismatch(AuditoryError):
    code = "COMPARISON_DURATION_MISMATCH"


class ComparisonChannelMismatch(AuditoryError):
    code = "COMPARISON_CHANNEL_MISMATCH"


class ProcessingPlanInvalid(AuditoryError):
    code = "PROCESSING_PLAN_INVALID"


class ComparisonEvidenceIncomplete(AuditoryError):
    code = "COMPARISON_EVIDENCE_INCOMPLETE"


class ComparisonInvalid(AuditoryError):
    code = "COMPARISON_INVALID"


class EvidenceHashMismatch(AuditoryError):
    code = "EVIDENCE_HASH_MISMATCH"
