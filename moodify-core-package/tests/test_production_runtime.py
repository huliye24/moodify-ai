"""DSK-MFY-RUNTIME-INTEGRATION-001 — control-spine runtime tests.

State machine, runtime, verification, evidence, and legacy-path coverage
for the authoritative production lifecycle.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

from moodify.app.engines import NativeExecutionEngine
from moodify.app.production_control import (
    ALLOWED,
    CaseState,
    ControlError,
    ExecutionResult,
    ProductionCase,
    ProductionCaseStore,
    ProductionControlService,
    default_plan,
)

SR = 44100


@pytest.fixture
def source_wav(tmp_path: Path) -> Path:
    t = np.arange(SR // 2) / SR
    path = tmp_path / "source.wav"
    sf.write(str(path), 0.3 * np.sin(2 * np.pi * 440 * t), SR)
    return path


def make_case(source_wav: Path, store: ProductionCaseStore, case_id: str = "MFY-CASE-TEST") -> ProductionCase:
    case = ProductionCase(case_id=case_id)
    case.register_source(str(source_wav))
    case.specify("warm vocal", ["vocal intimacy"], ["harsh highs"],
                 "gentle normalization", "tester")
    case.begin_analysis()
    case.analyze({"peak_db": -12.0, "crest_factor": 8.0})
    case.set_plan(default_plan(case.analysis), engine_name="native")
    case.run_technical_gate()
    case.approve("tester")
    store.save(case)
    return case


def make_service(tmp_path: Path) -> ProductionControlService:
    return ProductionControlService(ProductionCaseStore(tmp_path / "cases"), NativeExecutionEngine())


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class FailingEngine:
    name = "native"
    version = "1.0.0"

    def __init__(self):
        self.calls = []

    def execute(self, envelope):
        self.calls.append(envelope)
        return ExecutionResult(
            execution_id="MFY-EXEC-FAIL", success=False, engine_name=self.name,
            engine_version=self.version, started_at="", completed_at="", duration=0.1,
            command_or_action_manifest=[], output_path="", output_sha256="",
            warnings=[], errors=["injected engine failure"])


class OtherEngine:
    name = "other"
    version = "1.0.0"

    def __init__(self):
        self.calls = []

    def execute(self, envelope):
        self.calls.append(envelope)
        return ExecutionResult(
            execution_id="MFY-EXEC-OTHER", success=True, engine_name=self.name,
            engine_version=self.version, started_at="", completed_at="", duration=0.1,
            command_or_action_manifest=[], output_path="", output_sha256="",
            warnings=[], errors=[])


# ---------------------------------------------------------------- state graph

@pytest.mark.parametrize("state", [
    CaseState.APPROVED, CaseState.EXECUTING, CaseState.EXECUTED,
    CaseState.VERIFYING, CaseState.VERIFIED, CaseState.FAILED,
])
def test_completion_shortcut_transitions_are_impossible(state):
    assert CaseState.COMPLETED not in ALLOWED.get(state, set())


def test_only_packaged_can_transition_to_completed():
    assert ALLOWED.get(CaseState.PACKAGED) == {CaseState.COMPLETED, CaseState.FAILED}


def test_specified_must_pass_through_analyzing():
    assert ALLOWED[CaseState.SPECIFIED] == {CaseState.ANALYZING}
    assert ALLOWED[CaseState.ANALYZING] == {CaseState.ANALYZED}


def test_specified_to_analyzed_rejected_at_runtime():
    case = ProductionCase(case_id="MFY-CASE-X", state=CaseState.SPECIFIED)
    with pytest.raises(ValueError, match="Invalid"):
        case._transition(CaseState.ANALYZED)


@pytest.mark.parametrize("state", [
    CaseState.APPROVED, CaseState.EXECUTING, CaseState.EXECUTED,
    CaseState.VERIFYING, CaseState.VERIFIED, CaseState.FAILED,
])
def test_transition_to_completed_rejected_at_runtime(state):
    case = ProductionCase(case_id="MFY-CASE-X", state=state)
    with pytest.raises(ValueError, match="Invalid"):
        case._transition(CaseState.COMPLETED)


# ---------------------------------------------------------------- runtime

def test_engine_not_invoked_when_approval_gate_fails(tmp_path, source_wav):
    store = ProductionCaseStore(tmp_path / "cases")
    case = ProductionCase(case_id="MFY-CASE-NA")
    case.register_source(str(source_wav))
    case.specify("x", ["a"], ["b"], "c", "tester")
    case.begin_analysis()
    case.analyze({"peak_db": -3.0})
    case.set_plan(default_plan(case.analysis))
    case.run_technical_gate()
    store.save(case)  # never approved
    engine = FailingEngine()
    service = ProductionControlService(store, engine)
    with pytest.raises(ControlError) as exc:
        service.execute("MFY-CASE-NA")
    assert exc.value.code == "ARTISTIC_APPROVAL_REQUIRED"
    assert engine.calls == []
    assert store.load("MFY-CASE-NA").state == CaseState.TECHNICALLY_VALIDATED


def test_execute_with_stale_plan_hash_rejected(tmp_path, source_wav):
    store = ProductionCaseStore(tmp_path / "cases")
    make_case(source_wav, store, "MFY-CASE-STALE")
    case = store.load("MFY-CASE-STALE")
    case.plan["steps"] = [{"type": "gain", "params": {"gain_db": 99.0}, "reason": "tampered"}]
    case.plan_hash = hashlib.sha256(json.dumps(case.plan, sort_keys=True).encode()).hexdigest()
    store.save(case)
    service = make_service(tmp_path)
    with pytest.raises(ControlError) as exc:
        service.execute("MFY-CASE-STALE")
    assert exc.value.code == "PLAN_HASH_STALE"
    assert store.load("MFY-CASE-STALE").state == CaseState.APPROVED


def test_execute_with_changed_source_rejected(tmp_path, source_wav):
    store = ProductionCaseStore(tmp_path / "cases")
    make_case(source_wav, store, "MFY-CASE-SRC")
    source_wav.write_bytes(source_wav.read_bytes() + b"x")
    service = make_service(tmp_path)
    with pytest.raises(ControlError) as exc:
        service.execute("MFY-CASE-SRC")
    assert exc.value.code == "SOURCE_CHANGED"
    assert store.load("MFY-CASE-SRC").state == CaseState.APPROVED


def test_execute_with_engine_mismatch_rejected(tmp_path, source_wav):
    store = ProductionCaseStore(tmp_path / "cases")
    make_case(source_wav, store, "MFY-CASE-ENG")  # plan bound to engine "native"
    service = ProductionControlService(store, OtherEngine())
    with pytest.raises(ControlError) as exc:
        service.execute("MFY-CASE-ENG")
    assert exc.value.code == "ENGINE_MISMATCH"


def test_execute_success_reaches_executed(tmp_path, source_wav):
    store = ProductionCaseStore(tmp_path / "cases")
    make_case(source_wav, store, "MFY-CASE-OK")
    service = make_service(tmp_path)
    result = service.execute("MFY-CASE-OK")
    assert result["ok"] is True
    assert result["previous_state"] == "APPROVED"
    assert result["state"] == "EXECUTED"
    assert result["execution_id"].startswith("MFY-EXEC-")
    output = Path(result["output_path"])
    assert output.exists()
    case = store.load("MFY-CASE-OK")
    assert case.execution_record["engine_name"] == "native"
    assert case.execution_record["plan_hash"] == case.plan_hash
    assert case.execution_record["envelope"]["approval_id"] == case.artistic_approval.approval_id


def test_engine_failure_prevents_executed(tmp_path, source_wav):
    store = ProductionCaseStore(tmp_path / "cases")
    make_case(source_wav, store, "MFY-CASE-FAIL")
    failing = FailingEngine()
    service = ProductionControlService(store, failing)
    result = service.execute("MFY-CASE-FAIL")
    assert result["ok"] is False
    assert result["state"] == "FAILED"
    assert store.load("MFY-CASE-FAIL").state == CaseState.FAILED


def test_source_is_never_overwritten(tmp_path, source_wav):
    store = ProductionCaseStore(tmp_path / "cases")
    make_case(source_wav, store, "MFY-CASE-SAFE")
    before = sha256(source_wav)
    service = make_service(tmp_path)
    service.execute("MFY-CASE-SAFE")
    assert sha256(source_wav) == before


def test_partial_output_not_classified_as_final(tmp_path, source_wav):
    store = ProductionCaseStore(tmp_path / "cases")
    make_case(source_wav, store, "MFY-CASE-PART")
    service = make_service(tmp_path)
    service.execute("MFY-CASE-PART")
    case = store.load("MFY-CASE-PART")
    # staged artifacts are not referenced as the executed output
    assert case.execution_record["output_path"].endswith("processed_audio.wav")
    workspace = store.path_for("MFY-CASE-PART")
    assert not (workspace / "output" / ".staging" / "processed_audio.wav").exists()


def test_unsupported_action_fails_closed_without_final_output(tmp_path, source_wav):
    store = ProductionCaseStore(tmp_path / "cases")
    case = ProductionCase(case_id="MFY-CASE-UNSUP")
    case.register_source(str(source_wav))
    case.specify("x", ["a"], ["b"], "c", "tester")
    case.begin_analysis()
    case.analyze({"peak_db": -3.0})
    case.set_plan({"plan_id": "PLN-x", "steps": [{"type": "unknown_action", "params": {}}]})
    case.run_technical_gate()
    case.approve("tester")
    store.save(case)
    service = make_service(tmp_path)
    result = service.execute("MFY-CASE-UNSUP")
    assert result["ok"] is False
    assert result["state"] == "FAILED"
    assert not (store.path_for("MFY-CASE-UNSUP") / "output" / "processed_audio.wav").exists()


def test_retry_is_explicit_and_completed_case_is_immutable(tmp_path, source_wav):
    store = ProductionCaseStore(tmp_path / "cases")
    make_case(source_wav, store, "MFY-CASE-RETRY")
    failing = FailingEngine()
    service = ProductionControlService(store, failing)
    service.execute("MFY-CASE-RETRY")
    assert store.load("MFY-CASE-RETRY").state == CaseState.FAILED
    # retry requires an explicit approval again (FAILED -> APPROVED via approve)
    with pytest.raises(ControlError) as exc:
        service.execute("MFY-CASE-RETRY")
    assert exc.value.code == "ARTISTIC_APPROVAL_REQUIRED"
    case = store.load("MFY-CASE-RETRY")
    assert case.state == CaseState.FAILED
    # re-approve, then succeed with the real engine
    case.approve("tester")
    store.save(case)
    ok_service = make_service(tmp_path)
    result = ok_service.execute("MFY-CASE-RETRY")
    assert result["state"] == "EXECUTED"
    # golden completion; a completed case cannot be re-packaged
    ok_service.verify("MFY-CASE-RETRY")
    ok_service.package("MFY-CASE-RETRY")
    assert store.load("MFY-CASE-RETRY").state == CaseState.COMPLETED
    with pytest.raises(ControlError) as exc:
        ok_service.package("MFY-CASE-RETRY")
    assert exc.value.code == "VERIFICATION_REQUIRED"


# ---------------------------------------------------------------- verification

def _executed_case(tmp_path, source_wav, case_id="MFY-CASE-V") -> ProductionControlService:
    store = ProductionCaseStore(tmp_path / "cases")
    make_case(source_wav, store, case_id)
    service = make_service(tmp_path)
    service.execute(case_id)
    return service


def test_verification_missing_output_fails(tmp_path, source_wav):
    service = _executed_case(tmp_path, source_wav)
    case = service.store.load("MFY-CASE-V")
    Path(case.execution_record["output_path"]).unlink()
    result = service.verify("MFY-CASE-V")
    assert result.status == "FAIL"
    assert result.output_exists is False
    assert service.store.load("MFY-CASE-V").state == CaseState.FAILED


def test_verification_changed_source_fails(tmp_path, source_wav):
    service = _executed_case(tmp_path, source_wav)
    source_wav.write_bytes(source_wav.read_bytes() + b"x")
    result = service.verify("MFY-CASE-V")
    assert result.status == "FAIL"
    assert result.source_unchanged is False
    assert service.store.load("MFY-CASE-V").state == CaseState.FAILED


def test_verification_wrong_engine_identity_fails(tmp_path, source_wav):
    service = _executed_case(tmp_path, source_wav)
    case = service.store.load("MFY-CASE-V")
    case.execution_record["engine_name"] = "sox"
    service.store.save(case)
    result = service.verify("MFY-CASE-V")
    assert result.status == "FAIL"
    assert result.engine_identity_matches is False


def test_verification_wrong_plan_identity_fails(tmp_path, source_wav):
    service = _executed_case(tmp_path, source_wav)
    case = service.store.load("MFY-CASE-V")
    case.execution_record["plan_hash"] = "deadbeef"
    service.store.save(case)
    result = service.verify("MFY-CASE-V")
    assert result.status == "FAIL"
    assert result.plan_identity_matches is False


def test_verification_success_reaches_verified(tmp_path, source_wav):
    service = _executed_case(tmp_path, source_wav)
    result = service.verify("MFY-CASE-V")
    assert result.status == "PASS"
    assert result.source_unchanged is True
    assert result.engine_identity_matches is True
    assert result.plan_identity_matches is True
    assert result.basic_audio_checks["duration_positive"] is True
    assert service.store.load("MFY-CASE-V").state == CaseState.VERIFIED


def test_verification_does_not_create_artistic_approval(tmp_path, source_wav):
    service = _executed_case(tmp_path, source_wav)
    before = service.store.load("MFY-CASE-V").artistic_approval.approval_id
    service.verify("MFY-CASE-V")
    after = service.store.load("MFY-CASE-V").artistic_approval
    assert after.approval_id == before
    assert after.decision == "APPROVED"


# ---------------------------------------------------------------- evidence

def test_package_before_verified_rejected(tmp_path, source_wav):
    service = _executed_case(tmp_path, source_wav)
    with pytest.raises(ControlError) as exc:
        service.package("MFY-CASE-V")
    assert exc.value.code == "VERIFICATION_REQUIRED"
    assert service.store.load("MFY-CASE-V").state == CaseState.EXECUTED


def _verified_case(tmp_path, source_wav, case_id="MFY-CASE-E") -> ProductionControlService:
    service = _executed_case(tmp_path, source_wav, case_id)
    service.verify(case_id)
    return service


def test_package_success_golden_path(tmp_path, source_wav):
    service = _verified_case(tmp_path, source_wav)
    result = service.package("MFY-CASE-E")
    assert result["state"] == "COMPLETED"
    evidence = service.evidence_dir(service.store.load("MFY-CASE-E"))
    for name in service.REQUIRED_EVIDENCE_FILES:
        assert (evidence / name).is_file()
    assert (evidence / "output" / "processed_audio.wav").is_file()


def test_evidence_manifest_binds_all_identities(tmp_path, source_wav):
    service = _verified_case(tmp_path, source_wav)
    service.package("MFY-CASE-E")
    case = service.store.load("MFY-CASE-E")
    manifest = json.loads((service.evidence_dir(case) / "evidence_manifest.json").read_text(encoding="utf-8"))
    assert manifest["case_id"] == case.case_id
    assert manifest["source_sha256"] == case.source_sha256
    assert manifest["one_point_spec_hash"] == case.one_point_spec_hash
    assert manifest["plan_hash"] == case.plan_hash
    assert manifest["approval_id"] == case.artistic_approval.approval_id
    assert manifest["execution_id"] == case.execution_record["execution_id"]
    assert manifest["engine_name"] == "native"
    assert manifest["output_sha256"] == case.execution_record["output_sha256"]
    assert manifest["verification_id"] == case.verification_result["verification_id"]
    assert manifest["verification_status"] == "PASS"
    assert manifest["moodify_version"]


def test_package_output_tampered_prevents_completed(tmp_path, source_wav):
    service = _verified_case(tmp_path, source_wav)
    case = service.store.load("MFY-CASE-E")
    output = Path(case.execution_record["output_path"])
    output.write_bytes(output.read_bytes() + b"tampered")
    with pytest.raises(ControlError) as exc:
        service.package("MFY-CASE-E")
    assert exc.value.code == "EVIDENCE_INCONSISTENT"
    # stays PACKAGED: verification failure must not reach COMPLETED
    assert service.store.load("MFY-CASE-E").state == CaseState.PACKAGED


def test_package_source_changed_prevents_completed(tmp_path, source_wav):
    service = _verified_case(tmp_path, source_wav)
    source_wav.write_bytes(source_wav.read_bytes() + b"x")
    with pytest.raises(ControlError) as exc:
        service.package("MFY-CASE-E")
    assert exc.value.code == "EVIDENCE_INCONSISTENT"
    assert service.store.load("MFY-CASE-E").state == CaseState.PACKAGED


def test_package_missing_required_artifact_prevents_completed(tmp_path, source_wav, monkeypatch):
    service = _verified_case(tmp_path, source_wav)
    original = service._write

    def skipping_write(case, path, data):
        if path.name == "analysis.json":
            return  # simulate an interrupted/failed artifact write
        original(case, path, data)

    monkeypatch.setattr(service, "_write", skipping_write)
    with pytest.raises(ControlError) as exc:
        service.package("MFY-CASE-E")
    assert exc.value.code == "EVIDENCE_INCOMPLETE"
    assert service.store.load("MFY-CASE-E").state == CaseState.PACKAGED


def test_completed_evidence_package_internally_consistent(tmp_path, source_wav):
    service = _verified_case(tmp_path, source_wav)
    service.package("MFY-CASE-E")
    case = service.store.load("MFY-CASE-E")
    evidence = service.evidence_dir(case)
    manifest = json.loads((evidence / "evidence_manifest.json").read_text(encoding="utf-8"))
    execution = json.loads((evidence / "execution_record.json").read_text(encoding="utf-8"))
    verification = json.loads((evidence / "verification_result.json").read_text(encoding="utf-8"))
    source_manifest = json.loads((evidence / "source_manifest.json").read_text(encoding="utf-8"))
    approval = json.loads((evidence / "artistic_approval.json").read_text(encoding="utf-8"))
    assert manifest["source_sha256"] == source_manifest["source_sha256"] == sha256(source_wav)
    assert manifest["output_sha256"] == execution["output_sha256"] == sha256(evidence / "output" / "processed_audio.wav")
    assert manifest["approval_id"] == approval["approval_id"]
    assert manifest["verification_id"] == verification["verification_id"]
    assert manifest["verification_status"] == verification["status"] == "PASS"


def test_packaged_retry_validates_before_completing(tmp_path, source_wav):
    service = _verified_case(tmp_path, source_wav)
    service.package("MFY-CASE-E")
    case = service.store.load("MFY-CASE-E")
    assert case.state == CaseState.COMPLETED
    # simulate a crash between PACKAGED and COMPLETED: state persisted as PACKAGED
    case.state = CaseState.PACKAGED
    output = Path(case.execution_record["output_path"])
    output.write_bytes(output.read_bytes() + b"x")
    service.store.save(case)
    with pytest.raises(ControlError) as exc:
        service.package("MFY-CASE-E")
    assert exc.value.code == "EVIDENCE_INCONSISTENT"
    assert service.store.load("MFY-CASE-E").state == CaseState.PACKAGED


# ---------------------------------------------------------------- persistence

def test_case_persists_across_service_restart(tmp_path, source_wav):
    store = ProductionCaseStore(tmp_path / "cases")
    make_case(source_wav, store, "MFY-CASE-PERSIST")
    service = ProductionControlService(store, NativeExecutionEngine())
    service.execute("MFY-CASE-PERSIST")
    service.verify("MFY-CASE-PERSIST")
    service.package("MFY-CASE-PERSIST")
    # simulate a process restart: a brand-new store and service
    fresh = ProductionControlService(ProductionCaseStore(tmp_path / "cases"), NativeExecutionEngine())
    case = fresh.store.load("MFY-CASE-PERSIST")
    assert case.state == CaseState.COMPLETED
    assert case.plan_hash and case.artistic_approval is not None
    assert case.execution_record["execution_id"]
    assert case.verification_result["status"] == "PASS"
    assert case.evidence_path and Path(case.evidence_path).exists()


def test_interrupted_executing_is_never_assumed_successful(tmp_path, source_wav):
    store = ProductionCaseStore(tmp_path / "cases")
    make_case(source_wav, store, "MFY-CASE-INTERRUPT")
    case = store.load("MFY-CASE-INTERRUPT")
    case._transition(CaseState.EXECUTING)  # crash during execution
    store.save(case)
    fresh = ProductionControlService(ProductionCaseStore(tmp_path / "cases"), NativeExecutionEngine())
    # a restarted process must not fabricate EXECUTED; the gate requires APPROVED
    with pytest.raises(ControlError) as exc:
        fresh.execute("MFY-CASE-INTERRUPT")
    assert exc.value.code == "ARTISTIC_APPROVAL_REQUIRED"
    with pytest.raises(ControlError) as exc:
        fresh.verify("MFY-CASE-INTERRUPT")
    assert exc.value.code == "EXECUTION_REQUIRED"
    assert fresh.store.load("MFY-CASE-INTERRUPT").state == CaseState.EXECUTING


# ---------------------------------------------------------------- spec semantics

def test_empty_constraints_rejected_without_acknowledgement(source_wav, tmp_path):
    case = ProductionCase(case_id="MFY-CASE-SPEC1")
    case.register_source(str(source_wav))
    with pytest.raises(ControlError) as exc:
        case.specify("x", [], ["b"], "c", "tester")
    assert exc.value.code == "SPEC_INVALID"
    assert "preservation_acknowledgement" in exc.value.message


def test_omitted_and_null_fields_rejected(source_wav, tmp_path):
    case = ProductionCase(case_id="MFY-CASE-SPEC2")
    case.register_source(str(source_wav))
    with pytest.raises(ControlError, match="essence"):
        case.specify(None, ["a"], ["b"], "c", "tester")
    with pytest.raises(ControlError, match="must_preserve"):
        case.specify("x", None, ["b"], "c", "tester")


def test_empty_constraints_with_acknowledgement_accepted(source_wav, tmp_path):
    case = ProductionCase(case_id="MFY-CASE-SPEC3")
    case.register_source(str(source_wav))
    ack = {"acknowledged": True, "by": "human_owner",
           "reason": "No specific preservation constraint was identified."}
    case.specify("x", [], [], "c", "tester", preservation_acknowledgement=ack)
    assert case.state == CaseState.SPECIFIED
    assert case.one_point_spec["preservation_acknowledgement"]["acknowledged"] is True


def test_acknowledgement_without_true_rejected(source_wav, tmp_path):
    case = ProductionCase(case_id="MFY-CASE-SPEC4")
    case.register_source(str(source_wav))
    with pytest.raises(ControlError, match="acknowledgement"):
        case.specify("x", [], ["b"], "c", "tester",
                     preservation_acknowledgement={"acknowledged": False, "by": "x", "reason": "y"})


# ---------------------------------------------------------------- legacy paths

def test_orchestrator_execute_plan_is_classified_uncontrolled(tmp_path, source_wav):
    from moodify.app.orchestrator import generate_plan, execute_plan, analyze_audio
    analysis = analyze_audio(str(source_wav))
    plan = generate_plan({"source": str(source_wav)}, analysis)
    result = execute_plan(plan, str(source_wav), tmp_path / "legacy-out")
    assert result["production_controlled"] is False
    assert result["classification"] == "UNCONTROLLED_TOOL_EXECUTION"
    assert result["formal_moodify_asset"] is False
    assert result["status"].startswith("UNCONTROLLED")


def test_uncontrolled_execution_creates_no_evidence_package(tmp_path, source_wav):
    from moodify.app.orchestrator import generate_plan, execute_plan, analyze_audio
    analysis = analyze_audio(str(source_wav))
    plan = generate_plan({"source": str(source_wav)}, analysis)
    out = tmp_path / "legacy-out"
    execute_plan(plan, str(source_wav), out)
    assert not (out / "evidence").exists()
    assert not (out / "evidence_manifest.json").exists()


def test_uncontrolled_execution_creates_no_completed_case(tmp_path, source_wav):
    from moodify.app.orchestrator import generate_plan, execute_plan, analyze_audio
    analysis = analyze_audio(str(source_wav))
    plan = generate_plan({"source": str(source_wav)}, analysis)
    execute_plan(plan, str(source_wav), tmp_path / "legacy-out")
    store = ProductionCaseStore(tmp_path / "cases")
    assert store.list_case_ids() == []
