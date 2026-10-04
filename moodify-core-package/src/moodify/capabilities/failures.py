"""Moodify-level failure vocabulary.

A provider's native traceback is *not* the ecosystem contract. Every failure
that crosses a capability boundary is expressed in this vocabulary, so a
caller (an Agent, a CLI, a Production Graph node) can react to a stable code
instead of parsing engine-specific text.

This is the registry-level expression of a rule already enforced in code by
HOTFIX 000: a missing external runtime must surface as ``DEPENDENCY_MISSING``,
never as a deep ABI traceback from an engine Moodify happens to have called.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator

from moodify.compat import StrEnum


class FailureCode(StrEnum):
    """The canonical Moodify failure vocabulary."""

    # --- required set ---
    DEPENDENCY_MISSING = "DEPENDENCY_MISSING"
    """A required runtime, model, binary or service is absent."""

    PROVIDER_UNAVAILABLE = "PROVIDER_UNAVAILABLE"
    """A provider is known but not reachable or not eligible for this request."""

    INVALID_INPUT = "INVALID_INPUT"
    """The input violates the capability contract."""

    UNSUPPORTED_FORMAT = "UNSUPPORTED_FORMAT"
    """The input format is outside the capability's declared set."""

    RESOURCE_LIMIT = "RESOURCE_LIMIT"
    """Memory, disk, GPU or time budget exceeded."""

    AUTH_REQUIRED = "AUTH_REQUIRED"
    """Credentials are absent or were rejected."""

    RATE_LIMITED = "RATE_LIMITED"
    """The provider throttled the caller."""

    EXECUTION_FAILED = "EXECUTION_FAILED"
    """The provider ran and failed. The catch-all floor."""

    QUALITY_GATE_FAILED = "QUALITY_GATE_FAILED"
    """Output was produced but failed a declared gate."""

    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    """The result is uncertain and human authority is required to proceed."""

    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"
    """The capability is declared but has no implementation in this build."""

    # --- optional set, justified by repository evidence ---
    TIMEOUT = "TIMEOUT"
    """Exceeded a caller-declared deadline. Distinct from RESOURCE_LIMIT,
    which is about resource exhaustion rather than elapsed time."""

    INTEGRITY_ERROR = "INTEGRITY_ERROR"
    """A digest or size check failed. Moodify verifies content by sha256
    throughout (evidence artifacts, project sources, cloud node ingest), so
    corruption needs its own code rather than a generic failure."""

    CONFLICT = "CONFLICT"
    """Two sources of truth disagree. ``moodify.auditory.evidence.conflicts``
    already models contradictory evidence explicitly."""

    CANCELLED = "CANCELLED"
    """The caller or a single-flight lock abandoned the work. Long runs are
    cancellable in the desktop shell and the node queue."""


#: Codes where retrying the identical request can plausibly succeed.
#: Deliberately excludes INVALID_INPUT, UNSUPPORTED_FORMAT, NOT_IMPLEMENTED
#: and REVIEW_REQUIRED: those are deterministic properties of the request.
RETRYABLE_FAILURE_CODES = frozenset(
    {
        FailureCode.PROVIDER_UNAVAILABLE,
        FailureCode.RESOURCE_LIMIT,
        FailureCode.RATE_LIMITED,
        FailureCode.TIMEOUT,
        FailureCode.EXECUTION_FAILED,
        FailureCode.CANCELLED,
    }
)


def is_retryable(code: FailureCode) -> bool:
    """Whether a failure of *code* may be retried unchanged."""
    return code in RETRYABLE_FAILURE_CODES


class Failure(BaseModel):
    """A structured failure crossing a capability boundary.

    Immutable and strict: an unexpected field is a programming error, not
    something to silently carry along.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    code: FailureCode
    message: str
    retryable: bool
    provider: str | None = None
    details: dict[str, Any] | None = None

    @field_validator("message")
    @classmethod
    def require_message(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("failure message must be non-empty")
        return value

    @classmethod
    def of(
        cls,
        code: FailureCode,
        message: str,
        *,
        provider: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> "Failure":
        """Build a failure, deriving ``retryable`` from the canonical table."""
        return cls(
            code=code,
            message=message,
            retryable=is_retryable(code),
            provider=provider,
            details=details,
        )
