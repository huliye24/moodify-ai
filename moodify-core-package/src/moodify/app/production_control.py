"""Production Control Spine — authoritative production lifecycle.

The spine is the only path through which a formal Moodify production asset
may be created:

    ProductionCase
    → valid OnePointSpec
    → bound Plan
    → TechnicalGate
    → exact-plan Human Artistic Approval
    → controlled execution
    → verification
    → evidence packaging
    → COMPLETED

Engines receive an immutable ApprovedExecutionEnvelope and never mutate the
case state. All transitions are enforced by the ALLOWED state graph; the only
legal transition into COMPLETED is from PACKAGED.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
import time
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any, Protocol
from uuid import uuid4


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _id(prefix: str) -> str:
    return f"{prefix}-{hashlib.sha256(uuid4().bytes).hexdigest()[:12]}"


class ControlError(Exception):
    """Structured control-spine failure surfaced by the CLI."""

    def __init__(self, code: str, message: str, field: str = "", state: str = ""):
        super().__init__(message)
        self.code = code
        self.message = message
        self.field = field
        self.state = state


class CaseState(StrEnum):
    CREATED = "CREATED"
    SOURCE_REGISTERED = "SOURCE_REGISTERED"; SPECIFIED = "SPECIFIED"
    ANALYZED = "ANALYZED"; PLANNED = "PLANNED"
    TECHNICALLY_VALIDATED = "TECHNICALLY_VALIDATED"
    AWAITING_ARTISTIC_APPROVAL = "AWAITING_ARTISTIC_APPROVAL"
    APPROVED = "APPROVED"; EXECUTING = "EXECUTING"; EXECUTED = "EXECUTED"
    VERIFYING = "VERIFYING"; VERIFIED = "VERIFIED"
    PACKAGED = "PACKAGED"; COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"; FAILED = "FAILED"


ALLOWED = {
    CaseState.CREATED: {CaseState.SOURCE_REGISTERED},
    CaseState.SOURCE_REGISTERED: {CaseState.SPECIFIED},
    CaseState.SPECIFIED: {CaseState.ANALYZED},
    CaseState.ANALYZED: {CaseState.PLANNED, CaseState.REJECTED},
    CaseState.PLANNED: {CaseState.TECHNICALLY_VALIDATED, CaseState.REJECTED},
    CaseState.TECHNICALLY_VALIDATED: {CaseState.AWAITING_ARTISTIC_APPROVAL, CaseState.REJECTED},
    CaseState.AWAITING_ARTISTIC_APPROVAL: {CaseState.APPROVED, CaseState.REJECTED},
    CaseState.APPROVED: {CaseState.EXECUTING, CaseState.REJECTED},
    CaseState.EXECUTING: {CaseState.EXECUTED, CaseState.FAILED},
    CaseState.EXECUTED: {CaseState.VERIFYING, CaseState.FAILED},
    CaseState.VERIFYING: {CaseState.VERIFIED, CaseState.FAILED},
    CaseState.VERIFIED: {CaseState.PACKAGED},
    CaseState.PACKAGED: {CaseState.COMPLETED, CaseState.FAILED},
    CaseState.COMPLETED: set(), CaseState.REJECTED: {CaseState.SPECIFIED},
    CaseState.FAILED: {CaseState.APPROVED},
}

COMPLETION_SHORTCUTS = (
    CaseState.APPROVED, CaseState.EXECUTING, CaseState.EXECUTED,
    CaseState.VERIFYING, CaseState.VERIFIED, CaseState.FAILED,
)


@dataclass
class TechnicalGateResult:
    status: str = "PASS"; checks: dict = field(default_factory=dict)
    errors: list = field(default_factory=list); checked_at: str = ""


@dataclass
class ArtisticApprovalRecord:
    approval_id: str; case_id: str; plan_id: str; plan_hash: str
    source_sha256: str; one_point_spec_hash: str; human_owner: str
    decision: str = "APPROVED"; approved_at: str = ""; comment: str = ""


def validate_spec_fields(essence, must_preserve, must_avoid, desired_change,
                         human_owner, preservation_acknowledgement) -> None:
    """Explicit-declaration semantics: no omitted/null fields, no implicit
    defaults. Empty constraint lists require a valid acknowledgement record."""
    if essence is None or not str(essence).strip():
        raise ControlError("SPEC_INVALID", "essence is required and must be non-empty", field="essence")
    if desired_change is None or not str(desired_change).strip():
        raise ControlError("SPEC_INVALID", "desired_change is required and must be non-empty", field="desired_change")
    if human_owner is None or not str(human_owner).strip():
        raise ControlError("SPEC_INVALID", "human_owner is required and must be non-empty", field="human_owner")
    for name, value in (("must_preserve", must_preserve), ("must_avoid", must_avoid)):
        if value is None:
            raise ControlError("SPEC_INVALID", f"{name} is required (may be an explicit empty list)", field=name)
        if not isinstance(value, list) or any(not str(v).strip() for v in value):
            raise ControlError("SPEC_INVALID", f"{name} must be a list of non-empty strings", field=name)
        if not value and not _valid_acknowledgement(preservation_acknowledgement):
            raise ControlError(
                "SPEC_INVALID",
                f"{name} is empty; an explicit preservation_acknowledgement "
                "(acknowledged=true, by, reason) is required",
                field=name)
    if preservation_acknowledgement is not None and not _valid_acknowledgement(preservation_acknowledgement):
        raise ControlError(
            "SPEC_INVALID",
            "preservation_acknowledgement must be {acknowledged: true, by, reason}",
            field="preservation_acknowledgement")


def _valid_acknowledgement(ack) -> bool:
    if not isinstance(ack, dict):
        return False
    if ack.get("acknowledged") is not True:
        return False
    if not str(ack.get("by", "")).strip():
        return False
    if not str(ack.get("reason", "")).strip():
        return False
    return True


@dataclass
class ProductionCase:
    case_id: str; state: CaseState = CaseState.CREATED
    version: str = "1"
    source_path: str = ""; source_sha256: str = ""
    one_point_spec: dict = field(default_factory=dict); one_point_spec_hash: str = ""
    analysis: dict = field(default_factory=dict)
    plan: dict = field(default_factory=dict); plan_hash: str = ""
    technical_gate: TechnicalGateResult | None = None
    artistic_approval: ArtisticApprovalRecord | None = None
    engine_name: str = "native"; engine_version: str = "1.0.0"
    execution_record: dict = field(default_factory=dict)
    verification_result: dict = field(default_factory=dict)
    evidence_path: str = ""; errors: list = field(default_factory=list)
    transitions: list = field(default_factory=list)
    created_at: str = ""; updated_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = _now()
            self.updated_at = _now()
            self.transitions.append({"from": None, "to": self.state.value, "at": _now()})

    def _transition(self, target: CaseState):
        if target not in ALLOWED.get(self.state, set()):
            raise ValueError(f"Invalid: {self.state.value} -> {target.value}")
        source = self.state.value
        self.state = target
        self.updated_at = _now()
        self.transitions.append({"from": source, "to": target.value, "at": _now()})

    def register_source(self, path: str):
        p = Path(path)
        if not p.exists():
            raise ControlError("SOURCE_NOT_FOUND", f"Source not found: {path}", field="source_path")
        self.source_path = str(p.resolve())
        self.source_sha256 = hashlib.sha256(p.read_bytes()).hexdigest()
        self._transition(CaseState.SOURCE_REGISTERED)

    def specify(self, essence: str, must_preserve: list, must_avoid: list,
                desired_change: str, human_owner: str,
                preservation_acknowledgement: dict | None = None):
        validate_spec_fields(essence, must_preserve, must_avoid, desired_change,
                             human_owner, preservation_acknowledgement)
        spec = {"essence": essence, "must_preserve": list(must_preserve),
                "must_avoid": list(must_avoid), "desired_change": desired_change,
                "human_owner": human_owner}
        if preservation_acknowledgement is not None:
            spec["preservation_acknowledgement"] = preservation_acknowledgement
        self.one_point_spec = spec
        self.one_point_spec_hash = hashlib.sha256(
            json.dumps(spec, sort_keys=True).encode()).hexdigest()
        self._transition(CaseState.SPECIFIED)

    def analyze(self, analysis: dict):
        if not analysis or not isinstance(analysis, dict):
            raise ControlError("ANALYSIS_INVALID", "analysis is required", field="analysis")
        self.analysis = dict(analysis)
        self._transition(CaseState.ANALYZED)

    def set_plan(self, plan: dict, engine_name: str = "native") -> str:
        if not self.one_point_spec_hash:
            raise ControlError("SPEC_REQUIRED", "OnePointSpec required before planning", field="plan")
        if not plan.get("plan_id") or not plan.get("steps"):
            raise ControlError("PLAN_INVALID", "plan requires plan_id and non-empty steps", field="plan")
        plan["one_point_spec_hash"] = self.one_point_spec_hash
        plan["source_sha256"] = self.source_sha256
        plan["engine_name"] = engine_name
        self.plan = plan
        self.engine_name = engine_name
        self.plan_hash = hashlib.sha256(
            json.dumps(plan, sort_keys=True).encode()).hexdigest()
        self._transition(CaseState.PLANNED)
        return self.plan_hash

    def run_technical_gate(self) -> TechnicalGateResult:
        errors = []
        if not Path(self.source_path).exists():
            errors.append("Source file missing")
        if not self.one_point_spec_hash:
            errors.append("OnePointSpec missing")
        if not self.plan_hash:
            errors.append("Plan missing")
        if self.plan.get("one_point_spec_hash") != self.one_point_spec_hash:
            errors.append("Plan not bound to current spec")
        if self.plan.get("source_sha256") != self.source_sha256:
            errors.append("Plan not bound to current source")
        gate = TechnicalGateResult(
            status="PASS" if not errors else "FAIL",
            checks={"source": Path(self.source_path).exists(),
                    "spec": bool(self.one_point_spec_hash),
                    "plan": bool(self.plan_hash)},
            errors=errors,
            checked_at=_now())
        self.technical_gate = gate
        if gate.status == "PASS":
            self._transition(CaseState.TECHNICALLY_VALIDATED)
        else:
            self.errors.extend(errors)
            raise ControlError("TECHNICAL_GATE_FAILED",
                               "Technical gate FAILED: " + "; ".join(errors) or "unknown",
                               field="technical_gate")
        return gate

    def approve(self, human_owner: str) -> ArtisticApprovalRecord:
        if self.technical_gate is None or self.technical_gate.status != "PASS":
            raise ControlError("TECHNICAL_GATE_REQUIRED",
                               "Technical gate must PASS before approval", field="technical_gate")
        if not human_owner.strip():
            raise ControlError("SPEC_INVALID", "human_owner required", field="human_owner")
        if self.state == CaseState.TECHNICALLY_VALIDATED:
            self._transition(CaseState.AWAITING_ARTISTIC_APPROVAL)
        approval = ArtisticApprovalRecord(
            approval_id=f"APR-{hashlib.sha256(f'{self.case_id}{self.plan_hash}'.encode()).hexdigest()[:12]}",
            case_id=self.case_id, plan_id=self.plan.get("plan_id", ""),
            plan_hash=self.plan_hash, source_sha256=self.source_sha256,
            one_point_spec_hash=self.one_point_spec_hash,
            human_owner=human_owner, decision="APPROVED",
            approved_at=_now())
        self.artistic_approval = approval
        self._transition(CaseState.APPROVED)
        return approval

    def check_approval_gate(self, engine_name: str):
        if self.state != CaseState.APPROVED:
            raise ControlError("ARTISTIC_APPROVAL_REQUIRED",
                               f"Execution requires approval bound to the current plan (state {self.state.value})",
                               field="artistic_approval", state=self.state.value)
        a = self.artistic_approval
        if a is None:
            raise ControlError("ARTISTIC_APPROVAL_REQUIRED",
                               "Artistic approval missing", field="artistic_approval",
                               state=self.state.value)
        if a.decision != "APPROVED":
            raise ControlError("ARTISTIC_APPROVAL_REQUIRED",
                               "Not artistically APPROVED", field="artistic_approval",
                               state=self.state.value)
        if a.plan_hash != self.plan_hash:
            raise ControlError("PLAN_HASH_STALE", "Plan modified after approval", field="plan_hash")
        if a.source_sha256 != self.source_sha256:
            raise ControlError("SOURCE_CHANGED", "Source modified after approval", field="source_sha256")
        if a.one_point_spec_hash != self.one_point_spec_hash:
            raise ControlError("SPEC_CHANGED", "Spec modified after approval", field="one_point_spec_hash")
        if engine_name != self.engine_name:
            raise ControlError("ENGINE_MISMATCH",
                               f"Engine mismatch: {self.engine_name}", field="engine_name")

    def to_dict(self) -> dict:
        return {
            "case_id": self.case_id, "state": self.state.value, "version": self.version,
            "source_path": self.source_path, "source_sha256": self.source_sha256,
            "one_point_spec": self.one_point_spec, "one_point_spec_hash": self.one_point_spec_hash,
            "analysis": self.analysis, "plan": self.plan, "plan_hash": self.plan_hash,
            "technical_gate": (None if self.technical_gate is None else {
                "status": self.technical_gate.status, "checks": self.technical_gate.checks,
                "errors": self.technical_gate.errors, "checked_at": self.technical_gate.checked_at}),
            "artistic_approval": (None if self.artistic_approval is None else {
                "approval_id": self.artistic_approval.approval_id,
                "case_id": self.artistic_approval.case_id,
                "plan_id": self.artistic_approval.plan_id,
                "plan_hash": self.artistic_approval.plan_hash,
                "source_sha256": self.artistic_approval.source_sha256,
                "one_point_spec_hash": self.artistic_approval.one_point_spec_hash,
                "human_owner": self.artistic_approval.human_owner,
                "decision": self.artistic_approval.decision,
                "approved_at": self.artistic_approval.approved_at,
                "comment": self.artistic_approval.comment}),
            "engine_name": self.engine_name, "engine_version": self.engine_version,
            "execution_record": self.execution_record,
            "verification_result": self.verification_result,
            "evidence_path": self.evidence_path, "errors": list(self.errors),
            "transitions": list(self.transitions),
            "created_at": self.created_at, "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ProductionCase":
        gate = data.get("technical_gate")
        approval = data.get("artistic_approval")
        case = cls(
            case_id=data["case_id"], state=CaseState(data["state"]),
            version=data.get("version", "1"),
            source_path=data.get("source_path", ""), source_sha256=data.get("source_sha256", ""),
            one_point_spec=data.get("one_point_spec", {}),
            one_point_spec_hash=data.get("one_point_spec_hash", ""),
            analysis=data.get("analysis", {}), plan=data.get("plan", {}),
            plan_hash=data.get("plan_hash", ""),
            technical_gate=(None if gate is None else TechnicalGateResult(
                status=gate.get("status", "FAIL"), checks=gate.get("checks", {}),
                errors=gate.get("errors", []), checked_at=gate.get("checked_at", ""))),
            artistic_approval=(None if approval is None else ArtisticApprovalRecord(
                approval_id=approval["approval_id"], case_id=approval.get("case_id", ""),
                plan_id=approval.get("plan_id", ""), plan_hash=approval.get("plan_hash", ""),
                source_sha256=approval.get("source_sha256", ""),
                one_point_spec_hash=approval.get("one_point_spec_hash", ""),
                human_owner=approval.get("human_owner", ""),
                decision=approval.get("decision", "APPROVED"),
                approved_at=approval.get("approved_at", ""), comment=approval.get("comment", ""))),
            engine_name=data.get("engine_name", "native"),
            engine_version=data.get("engine_version", "1.0.0"),
            execution_record=data.get("execution_record", {}),
            verification_result=data.get("verification_result", {}),
            evidence_path=data.get("evidence_path", ""), errors=list(data.get("errors", [])),
            transitions=list(data.get("transitions", [])),
            created_at=data.get("created_at", ""), updated_at=data.get("updated_at", ""))
        if not case.transitions:
            case.transitions.append({"from": None, "to": case.state.value, "at": case.created_at})
        return case


@dataclass(frozen=True)
class ApprovedExecutionEnvelope:
    """Immutable authorization to execute exactly one approved plan.

    Generated only after the approval gate succeeds. Engines receive this
    envelope, never an unbound plan or raw WAV path."""
    case_id: str
    case_version: str
    source_path: str
    source_sha256: str
    one_point_spec_hash: str
    plan_id: str
    plan_hash: str
    approval_id: str
    approved_by: str
    engine_name: str
    engine_version: str
    actions: tuple = ()
    parameters: tuple = ()
    output_path: str = ""
    created_at: str = ""

    def to_dict(self) -> dict:
        return {
            "case_id": self.case_id, "case_version": self.case_version,
            "source_path": self.source_path, "source_sha256": self.source_sha256,
            "one_point_spec_hash": self.one_point_spec_hash,
            "plan_id": self.plan_id, "plan_hash": self.plan_hash,
            "approval_id": self.approval_id, "approved_by": self.approved_by,
            "engine_name": self.engine_name, "engine_version": self.engine_version,
            "actions": list(self.actions), "parameters": list(self.parameters),
            "output_path": self.output_path, "created_at": self.created_at,
        }


class ExecutionEngine(Protocol):
    name: str
    version: str

    def execute(self, envelope: ApprovedExecutionEnvelope) -> "ExecutionResult":
        ...


@dataclass
class ExecutionResult:
    execution_id: str
    success: bool
    engine_name: str
    engine_version: str
    started_at: str
    completed_at: str
    duration: float
    command_or_action_manifest: list
    output_path: str
    output_sha256: str
    warnings: list
    errors: list

    def to_dict(self) -> dict:
        return {k: getattr(self, k) for k in (
            "execution_id", "success", "engine_name", "engine_version", "started_at",
            "completed_at", "duration", "command_or_action_manifest", "output_path",
            "output_sha256", "warnings", "errors")}


@dataclass
class VerificationResult:
    verification_id: str
    case_id: str
    execution_id: str
    source_sha256_expected: str
    source_sha256_observed: str
    output_sha256: str
    output_exists: bool
    output_readable: bool
    source_unchanged: bool
    engine_identity_matches: bool
    plan_identity_matches: bool
    basic_audio_checks: dict
    status: str
    started_at: str
    completed_at: str

    def to_dict(self) -> dict:
        return {k: getattr(self, k) for k in (
            "verification_id", "case_id", "execution_id", "source_sha256_expected",
            "source_sha256_observed", "output_sha256", "output_exists", "output_readable",
            "source_unchanged", "engine_identity_matches", "plan_identity_matches",
            "basic_audio_checks", "status", "started_at", "completed_at")}


def default_plan(analysis: dict, intent: dict | None = None) -> dict:
    """Deterministic default plan bound to an analysis measurement.

    intent supports: target_peak_db, compressor (bool), limit (bool),
    limiter_ceiling_db."""
    intent = intent or {}
    target_peak = float(intent.get("target_peak_db", -1.0))
    peak = float(analysis.get("peak_db", 0.0))
    steps = []
    if peak < target_peak:
        steps.append({"type": "gain",
                      "params": {"gain_db": round(target_peak - peak, 1)},
                      "reason": f"Normalize to {target_peak} dB peak"})
    if analysis.get("crest_factor", 0) > 15 or intent.get("compressor"):
        steps.append({"type": "compressor",
                      "params": {"threshold_db": -12.0, "ratio": 2.0},
                      "reason": "Reduce excessive crest factor"})
    if intent.get("limit"):
        steps.append({"type": "limiter",
                      "params": {"ceiling_db": float(intent.get("limiter_ceiling_db", -1.0))},
                      "reason": "Safe ceiling limiter"})
    if not steps:
        steps.append({"type": "gain", "params": {"gain_db": 0.0},
                      "reason": "No adjustment required"})
    plan_id = "PLN-" + hashlib.sha256(
        json.dumps(steps, sort_keys=True).encode()).hexdigest()[:12]
    return {"plan_id": plan_id, "steps": steps, "warnings": []}


class ProductionCaseStore:
    """Durable JSON store: one directory per case under a workspace root."""

    def __init__(self, root: Path):
        self.root = Path(root)

    def path_for(self, case_id: str) -> Path:
        return self.root / case_id

    def save(self, case: ProductionCase) -> None:
        case_dir = self.path_for(case.case_id)
        case_dir.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(case.to_dict(), indent=2, sort_keys=True)
        fd, tmp_name = tempfile.mkstemp(prefix=".case.", suffix=".tmp", dir=case_dir)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(payload)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(tmp_name, case_dir / "case.json")
        finally:
            if os.path.exists(tmp_name):
                os.unlink(tmp_name)

    def load(self, case_id: str) -> ProductionCase:
        path = self.path_for(case_id) / "case.json"
        if not path.exists():
            raise ControlError("CASE_NOT_FOUND", f"Unknown production case: {case_id}")
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ControlError("CASE_INVALID", f"Cannot read case {case_id}: {exc}") from exc
        return ProductionCase.from_dict(data)

    def exists(self, case_id: str) -> bool:
        return (self.path_for(case_id) / "case.json").exists()

    def list_case_ids(self) -> list[str]:
        if not self.root.exists():
            return []
        return sorted(p.name for p in self.root.iterdir() if (p / "case.json").exists())


class ProductionControlService:
    """Authorizes execution, observes execution, verifies the result, packages
    the evidence, and determines whether a production asset is complete."""

    REQUIRED_EVIDENCE_FILES = (
        "case.json", "source_manifest.json", "one_point_spec.json", "analysis.json",
        "plan.json", "technical_gate.json", "artistic_approval.json",
        "approved_execution_envelope.json", "execution_record.json",
        "verification_result.json", "evidence_manifest.json",
    )

    def __init__(self, store: ProductionCaseStore,
                 engine: ExecutionEngine | None = None,
                 moodify_version: str = ""):
        self.store = store
        self.engine = engine
        self.moodify_version = moodify_version or _package_version()

    # ---- workspace layout -------------------------------------------------

    def case_workspace(self, case: ProductionCase) -> Path:
        return self.store.path_for(case.case_id)

    def output_dir(self, case: ProductionCase) -> Path:
        return self.case_workspace(case) / "output"

    def evidence_dir(self, case: ProductionCase) -> Path:
        return self.case_workspace(case) / "evidence"

    # ---- execute ----------------------------------------------------------

    def execute(self, case_id: str, engine: ExecutionEngine | None = None) -> dict:
        """Canonical runtime entry point: authorize then execute."""
        engine = engine or self.engine
        if engine is None:
            raise ControlError("ENGINE_UNAVAILABLE", "No execution engine configured")
        case = self.store.load(case_id)
        previous_state = case.state.value

        case.check_approval_gate(engine.name)
        if engine.version != case.engine_version:
            raise ControlError("ENGINE_MISMATCH",
                               f"Engine version mismatch: expected {case.engine_version}, got {engine.version}",
                               field="engine_version")
        observed = _sha256_of(Path(case.source_path))
        if observed != case.source_sha256:
            raise ControlError("SOURCE_CHANGED", "Source modified after approval", field="source_sha256")

        case._transition(CaseState.EXECUTING)
        self.store.save(case)

        envelope = self._build_envelope(case, engine)
        result = engine.execute(envelope)
        case.execution_record = result.to_dict()
        case.execution_record["envelope"] = envelope.to_dict()
        case.execution_record["plan_id"] = envelope.plan_id
        case.execution_record["plan_hash"] = envelope.plan_hash
        if result.success and Path(result.output_path).exists():
            case._transition(CaseState.EXECUTED)
        else:
            case.errors.append(f"execution {result.execution_id} failed: "
                               + "; ".join(result.errors) or "engine returned failure")
            case._transition(CaseState.FAILED)
        self.store.save(case)
        return {
            "ok": result.success,
            "case_id": case.case_id,
            "previous_state": previous_state,
            "state": case.state.value,
            "execution_id": result.execution_id,
            "output_path": result.output_path,
            "warnings": list(result.warnings),
            "errors": list(result.errors),
        }

    def _build_envelope(self, case: ProductionCase, engine: ExecutionEngine) -> ApprovedExecutionEnvelope:
        output_path = str(self.output_dir(case) / "processed_audio.wav")
        return ApprovedExecutionEnvelope(
            case_id=case.case_id, case_version=case.version,
            source_path=case.source_path, source_sha256=case.source_sha256,
            one_point_spec_hash=case.one_point_spec_hash,
            plan_id=case.plan.get("plan_id", ""), plan_hash=case.plan_hash,
            approval_id=case.artistic_approval.approval_id,
            approved_by=case.artistic_approval.human_owner,
            engine_name=engine.name, engine_version=engine.version,
            actions=tuple(a for a in case.plan.get("steps", [])),
            parameters=(),
            output_path=output_path, created_at=_now())

    # ---- verify -----------------------------------------------------------

    def verify(self, case_id: str) -> VerificationResult:
        case = self.store.load(case_id)
        if case.state != CaseState.EXECUTED:
            raise ControlError("EXECUTION_REQUIRED",
                               f"Verification requires EXECUTED (state {case.state.value})",
                               field="execution_record", state=case.state.value)
        execution = case.execution_record
        started = _now()
        case._transition(CaseState.VERIFYING)
        self.store.save(case)

        output_path = Path(execution.get("output_path", ""))
        expected_source = case.artistic_approval.source_sha256 if case.artistic_approval else case.source_sha256
        observed_source = _sha256_of(Path(case.source_path))
        output_exists = output_path.exists()
        output_readable = False
        output_sha = ""
        basic_checks: dict = {"duration_s": None, "sample_rate": None, "channels": None}
        if output_exists:
            try:
                import soundfile as sf
                info = sf.info(str(output_path))
                output_readable = True
                output_sha = _sha256_of(output_path)
                basic_checks = {"duration_s": round(info.duration, 3),
                                "sample_rate": info.samplerate,
                                "channels": info.channels,
                                "duration_positive": info.duration > 0}
            except Exception:
                basic_checks = {"duration_s": None, "sample_rate": None,
                                "channels": None, "read_error": True}
        result = VerificationResult(
            verification_id=_id("VERIFY"),
            case_id=case.case_id,
            execution_id=execution.get("execution_id", ""),
            source_sha256_expected=expected_source,
            source_sha256_observed=observed_source,
            output_sha256=output_sha,
            output_exists=output_exists,
            output_readable=output_readable,
            source_unchanged=(observed_source == expected_source),
            engine_identity_matches=(execution.get("engine_name") == case.engine_name
                                     and execution.get("engine_version") == case.engine_version),
            plan_identity_matches=(execution.get("plan_id") == case.plan.get("plan_id")
                                   and execution.get("plan_hash") == case.plan_hash),
            basic_audio_checks=basic_checks,
            status="PENDING", started_at=started, completed_at=_now())

        failures = []
        if not output_exists:
            failures.append("output_missing")
        if not output_readable:
            failures.append("output_unreadable")
        if not result.source_unchanged:
            failures.append("source_changed")
        if not result.engine_identity_matches:
            failures.append("engine_identity_mismatch")
        if not result.plan_identity_matches:
            failures.append("plan_identity_mismatch")
        if not execution.get("success"):
            failures.append("engine_error")
        if not basic_checks.get("duration_positive"):
            failures.append("basic_audio_check_failed")
        result.status = "FAIL" if failures else "PASS"
        case.verification_result = result.to_dict()
        if result.status == "PASS":
            case._transition(CaseState.VERIFIED)
        else:
            case.errors.extend(failures)
            case._transition(CaseState.FAILED)
        self.store.save(case)
        return result

    # ---- packaging --------------------------------------------------------

    def package(self, case_id: str) -> dict:
        case = self.store.load(case_id)
        if case.state == CaseState.PACKAGED:
            case.evidence_path = str(self.evidence_dir(case))
            self._validate_package(case)
            case._transition(CaseState.COMPLETED)
            self.store.save(case)
            return {"ok": True, "case_id": case.case_id, "state": case.state.value,
                    "evidence_path": case.evidence_path}
        if case.state != CaseState.VERIFIED:
            raise ControlError("VERIFICATION_REQUIRED",
                               f"Packaging requires VERIFIED (state {case.state.value})",
                               field="verification_result", state=case.state.value)

        case._transition(CaseState.PACKAGED)
        self.store.save(case)
        evidence_dir = self.evidence_dir(case)
        execution = case.execution_record
        verification = case.verification_result
        output_source = Path(execution.get("output_path", ""))
        package_output = evidence_dir / "output" / "processed_audio.wav"

        self._write(case, evidence_dir / "case.json", case.to_dict())
        self._write(case, evidence_dir / "source_manifest.json", {
            "source_path": case.source_path, "source_sha256": case.source_sha256,
            "registered_at": case.created_at})
        self._write(case, evidence_dir / "one_point_spec.json", case.one_point_spec)
        self._write(case, evidence_dir / "analysis.json", case.analysis)
        self._write(case, evidence_dir / "plan.json", case.plan)
        self._write(case, evidence_dir / "technical_gate.json", {
            "status": case.technical_gate.status, "checks": case.technical_gate.checks,
            "errors": case.technical_gate.errors, "checked_at": case.technical_gate.checked_at})
        self._write(case, evidence_dir / "artistic_approval.json", {
            "approval_id": case.artistic_approval.approval_id,
            "case_id": case.artistic_approval.case_id,
            "plan_id": case.artistic_approval.plan_id,
            "plan_hash": case.artistic_approval.plan_hash,
            "source_sha256": case.artistic_approval.source_sha256,
            "one_point_spec_hash": case.artistic_approval.one_point_spec_hash,
            "human_owner": case.artistic_approval.human_owner,
            "decision": case.artistic_approval.decision,
            "approved_at": case.artistic_approval.approved_at,
            "comment": case.artistic_approval.comment})
        self._write(case, evidence_dir / "approved_execution_envelope.json",
                    case.execution_record.get("envelope") or _last_envelope(case))
        self._write(case, evidence_dir / "execution_record.json", execution)
        self._write(case, evidence_dir / "verification_result.json", verification)
        if output_source.exists():
            package_output.parent.mkdir(parents=True, exist_ok=True)
            import shutil
            shutil.copy2(str(output_source), str(package_output))
        manifest = {
            "case_id": case.case_id, "case_version": case.version,
            "source_sha256": case.source_sha256,
            "one_point_spec_hash": case.one_point_spec_hash,
            "plan_hash": case.plan_hash,
            "approval_id": case.artistic_approval.approval_id,
            "execution_id": execution.get("execution_id", ""),
            "engine_name": execution.get("engine_name", ""),
            "engine_version": execution.get("engine_version", ""),
            "output_sha256": execution.get("output_sha256", ""),
            "output_path": str(output_source),
            "verification_id": verification.get("verification_id", ""),
            "verification_status": verification.get("status", ""),
            "moodify_version": self.moodify_version,
            "evidence_package_sha256": None,
            "created_at": _now(),
        }
        manifest["evidence_package_sha256"] = hashlib.sha256(
            json.dumps(manifest, sort_keys=True).encode()).hexdigest()
        self._write(case, evidence_dir / "evidence_manifest.json", manifest)

        case.evidence_path = str(evidence_dir)
        self._validate_package(case)
        case._transition(CaseState.COMPLETED)
        self.store.save(case)
        return {"ok": True, "case_id": case.case_id, "state": case.state.value,
                "evidence_path": case.evidence_path}

    def _write(self, case: ProductionCase, path: Path, data: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
        os.replace(tmp, path)

    def _validate_package(self, case: ProductionCase) -> None:
        evidence_dir = self.evidence_dir(case)
        missing = [name for name in self.REQUIRED_EVIDENCE_FILES
                   if not (evidence_dir / name).exists()]
        if missing:
            raise ControlError("EVIDENCE_INCOMPLETE",
                               "Evidence package missing required files: " + ", ".join(missing),
                               field="evidence")
        manifest = json.loads((evidence_dir / "evidence_manifest.json").read_text(encoding="utf-8"))
        source_manifest = json.loads((evidence_dir / "source_manifest.json").read_text(encoding="utf-8"))
        execution = json.loads((evidence_dir / "execution_record.json").read_text(encoding="utf-8"))
        verification = json.loads((evidence_dir / "verification_result.json").read_text(encoding="utf-8"))
        approval = json.loads((evidence_dir / "artistic_approval.json").read_text(encoding="utf-8"))
        package_output = evidence_dir / "output" / "processed_audio.wav"

        problems = []
        if _sha256_of(Path(case.source_path)) != case.source_sha256:
            problems.append("source changed since registration")
        if manifest.get("source_sha256") != case.source_sha256:
            problems.append("manifest.source_sha256 != case.source_sha256")
        if source_manifest.get("source_sha256") != case.source_sha256:
            problems.append("source_manifest.sha256 != case.source_sha256")
        if manifest.get("plan_hash") != case.plan_hash:
            problems.append("manifest.plan_hash != case.plan_hash")
        if manifest.get("approval_id") != approval.get("approval_id"):
            problems.append("manifest.approval_id != approval record")
        if manifest.get("execution_id") != execution.get("execution_id"):
            problems.append("manifest.execution_id != execution record")
        if manifest.get("verification_id") != verification.get("verification_id"):
            problems.append("manifest.verification_id != verification result")
        if manifest.get("output_sha256") != execution.get("output_sha256"):
            problems.append("manifest.output_sha256 != execution record")
        if not package_output.exists():
            problems.append("package output missing")
        elif _sha256_of(package_output) != execution.get("output_sha256", ""):
            problems.append("package output hash != executed output hash")
        executed = Path(manifest.get("output_path", ""))
        if executed.exists() and _sha256_of(executed) != execution.get("output_sha256", ""):
            problems.append("executed output changed since execution")
        if verification.get("status") != "PASS":
            problems.append("verification status != PASS")
        if problems:
            raise ControlError("EVIDENCE_INCONSISTENT",
                               "Evidence package failed validation: " + "; ".join(problems),
                               field="evidence")


def _sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _last_envelope(case: ProductionCase) -> dict:
    """Reconstruct the execution envelope from the persisted case."""
    return {
        "case_id": case.case_id, "case_version": case.version,
        "source_path": case.source_path, "source_sha256": case.source_sha256,
        "one_point_spec_hash": case.one_point_spec_hash,
        "plan_id": case.plan.get("plan_id", ""), "plan_hash": case.plan_hash,
        "approval_id": case.artistic_approval.approval_id if case.artistic_approval else "",
        "approved_by": case.artistic_approval.human_owner if case.artistic_approval else "",
        "engine_name": case.engine_name, "engine_version": case.engine_version,
        "actions": list(case.plan.get("steps", [])), "parameters": [],
        "output_path": case.execution_record.get("output_path", ""),
        "created_at": case.updated_at,
    }


def _package_version() -> str:
    try:
        from moodify import __version__
        return __version__
    except Exception:
        return "0.0.0"
