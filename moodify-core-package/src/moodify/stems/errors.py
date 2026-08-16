"""Stem separation error taxonomy (LALAL-STEMS-001).

Mirrors moodify.auditory.errors: every failure carries a stable code
and a human message so the API layer can map it to a detail.code.
"""

from __future__ import annotations


class StemError(Exception):
    code = "STEM_ERROR"

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)

    def to_dict(self) -> dict:
        return {"error_code": self.code, "message": self.message}


class StemLicenseInvalid(StemError):
    """lalal.ai rejected the license key (HTTP 401/403)."""

    code = "STEM_LICENSE_INVALID"


class StemUpstreamRejected(StemError):
    """lalal.ai rejected the request (other 4xx)."""

    code = "STEM_UPSTREAM_REJECTED"


class StemUpstreamError(StemError):
    """lalal.ai returned 5xx or the request failed at transport level."""

    code = "STEM_UPSTREAM_ERROR"


class StemTaskUnknown(StemError):
    """lalal.ai /check/ does not know the submitted task_id."""

    code = "STEM_TASK_UNKNOWN"
