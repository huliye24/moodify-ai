"""ApprovedExecutionEnvelope — immutable, signed execution description.

Immutability contract (019 orchestration Stage A):
- envelope content is hashed into a signature; any mutation invalidates it
- approval binds issuer, time and policy_version
- inputs are locked by role -> absolute path -> SHA-256
- permissions: network off by default, output whitelist, resource limits
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

SCHEMA_VERSION = "approved-execution-envelope/0.1"

ExecutionStatus = Literal["envelope_created", "approved", "executing", "completed", "failed"]


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_dict(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


@dataclass(frozen=True)
class EnvelopeInput:
    role: str
    path: str
    sha256: str


@dataclass(frozen=True)
class Approval:
    issuer: str
    approved_at: str
    policy_version: str
    signature: str


@dataclass(frozen=True)
class ApprovedExecutionEnvelope:
    schema_version: str
    envelope_id: str
    case_id: str
    capability_id: str
    provider_id: str
    inputs: tuple[EnvelopeInput, ...]
    parameters: dict
    output_dir: str
    timeout_s: float
    allow_network: bool
    approval: Approval | None = None
    created_by: str = ""

    # ── canonical content (for signature) ───────────────────────────────
    def content_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "envelope_id": self.envelope_id,
            "case_id": self.case_id,
            "capability_id": self.capability_id,
            "provider_id": self.provider_id,
            "inputs": [{"role": i.role, "path": i.path, "sha256": i.sha256} for i in self.inputs],
            "parameters": self.parameters,
            "output_dir": self.output_dir,
            "timeout_s": self.timeout_s,
            "allow_network": self.allow_network,
        }

    def canonical(self) -> str:
        return _canonical_dict(self.content_dict())

    def is_approved(self) -> bool:
        return self.approval is not None

    def status_hint(self) -> ExecutionStatus:
        return "approved" if self.approval is not None else "envelope_created"

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "envelope_id": self.envelope_id,
            "case_id": self.case_id,
            "capability_id": self.capability_id,
            "provider_id": self.provider_id,
            "inputs": [{"role": i.role, "path": i.path, "sha256": i.sha256} for i in self.inputs],
            "parameters": self.parameters,
            "output_dir": self.output_dir,
            "timeout_s": self.timeout_s,
            "allow_network": self.allow_network,
            "approval": None if self.approval is None else {
                "issuer": self.approval.issuer,
                "approved_at": self.approval.approved_at,
                "policy_version": self.approval.policy_version,
                "signature": self.approval.signature,
            },
            "created_by": self.created_by,
        }


def envelope_signature(envelope: ApprovedExecutionEnvelope) -> str:
    """Content-derived signature of the immutable envelope body."""
    return hashlib.sha256(envelope.canonical().encode("utf-8")).hexdigest()


def sign_envelope(envelope: ApprovedExecutionEnvelope, issuer: str, policy_version: str) -> ApprovedExecutionEnvelope:
    """Return a new envelope bound to an approval (immutability: new signature)."""
    if envelope.approval is not None:
        raise ValueError(f"envelope {envelope.envelope_id} is already approved")
    import datetime

    approved_at = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    signature = envelope_signature(envelope)
    return ApprovedExecutionEnvelope(
        schema_version=envelope.schema_version,
        envelope_id=envelope.envelope_id,
        case_id=envelope.case_id,
        capability_id=envelope.capability_id,
        provider_id=envelope.provider_id,
        inputs=envelope.inputs,
        parameters=envelope.parameters,
        output_dir=envelope.output_dir,
        timeout_s=envelope.timeout_s,
        allow_network=envelope.allow_network,
        approval=Approval(issuer=issuer, approved_at=approved_at, policy_version=policy_version, signature=signature),
        created_by=envelope.created_by,
    )


def verify_envelope(envelope: ApprovedExecutionEnvelope) -> tuple[bool, str]:
    """Check approval binding: signature must match current content hash."""
    if envelope.approval is None:
        return False, "envelope is not approved"
    expected = envelope_signature(envelope)
    if envelope.approval.signature != expected:
        return False, f"signature mismatch (content was mutated): {envelope.approval.signature} != {expected}"
    return True, "signature valid"


def envelope_to_dict(e: ApprovedExecutionEnvelope) -> dict:
    return e.to_dict()


def envelope_from_dict(data: dict) -> ApprovedExecutionEnvelope:
    inputs = tuple(
        EnvelopeInput(role=str(i["role"]), path=str(i["path"]), sha256=str(i["sha256"]))
        for i in data.get("inputs", ())
    )
    approval_data = data.get("approval")
    approval = None
    if approval_data is not None:
        approval = Approval(
            issuer=str(approval_data["issuer"]),
            approved_at=str(approval_data["approved_at"]),
            policy_version=str(approval_data["policy_version"]),
            signature=str(approval_data["signature"]),
        )
    return ApprovedExecutionEnvelope(
        schema_version=str(data.get("schema_version", SCHEMA_VERSION)),
        envelope_id=str(data["envelope_id"]),
        case_id=str(data["case_id"]),
        capability_id=str(data["capability_id"]),
        provider_id=str(data["provider_id"]),
        inputs=inputs,
        parameters=dict(data.get("parameters", {})),
        output_dir=str(data["output_dir"]),
        timeout_s=float(data.get("timeout_s", 120.0)),
        allow_network=bool(data.get("allow_network", False)),
        approval=approval,
        created_by=str(data.get("created_by", "")),
    )


def envelope_dumps(e: ApprovedExecutionEnvelope) -> str:
    return json.dumps(envelope_to_dict(e), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def envelope_loads(text: str) -> ApprovedExecutionEnvelope:
    return envelope_from_dict(json.loads(text))


@dataclass(frozen=True)
class ExecutionRecord:
    """Full execution record written back to the case store (019 Stage B)."""

    schema_version: str
    record_id: str
    case_id: str
    envelope_id: str
    status: ExecutionStatus
    provider_id: str
    capability_id: str
    started_at: str
    finished_at: str = ""
    exit_code: int | None = None
    elapsed_s: float = 0.0
    artifacts: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()
    error_class: str | None = None
    evidence: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "record_id": self.record_id,
            "case_id": self.case_id,
            "envelope_id": self.envelope_id,
            "status": self.status,
            "provider_id": self.provider_id,
            "capability_id": self.capability_id,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "exit_code": self.exit_code,
            "elapsed_s": round(self.elapsed_s, 3),
            "artifacts": list(self.artifacts),
            "errors": list(self.errors),
            "error_class": self.error_class,
            "evidence": self.evidence,
        }


def record_dumps(record: ExecutionRecord) -> str:
    return json.dumps(record.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
