"""Approved execution — every provider execution derives from an approved envelope.

Envelopes are immutable execution descriptions: inputs locked by SHA-256,
frozen parameters, explicit permissions, resource limits and an approval
signature. Any change produces a new envelope with a new signature; the old
envelope is invalidated. The ExecutionGateway is the only execution entry
point; providers never run outside it (Law 3).
"""

from moodify.capability_registry.execution.envelope import (
    ApprovedExecutionEnvelope,
    ExecutionRecord,
    ExecutionStatus,
    envelope_signature,
    sign_envelope,
    verify_envelope,
)
from moodify.capability_registry.execution.gateway import ExecutionGateway

__all__ = [
    "ApprovedExecutionEnvelope",
    "ExecutionGateway",
    "ExecutionRecord",
    "ExecutionStatus",
    "envelope_signature",
    "sign_envelope",
    "verify_envelope",
]
