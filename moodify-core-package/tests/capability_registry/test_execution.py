"""Tests for approved execution: envelope immutability, gateway, records."""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from unittest import mock

import pytest

from moodify.capability_registry.adapters import FfprobeAdapter
from moodify.capability_registry.execution.envelope import (
    ApprovedExecutionEnvelope,
    EnvelopeInput,
    envelope_dumps,
    envelope_loads,
    envelope_signature,
    sign_envelope,
    verify_envelope,
)
from moodify.capability_registry.execution.gateway import ExecutionGateway, FileRecordStore


def make_wav(tmp_path: Path) -> Path:
    import math
    import struct
    import wave

    path = tmp_path / "a.wav"
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(8000)
        frames = b"".join(
            struct.pack("<h", int(8000 * math.sin(2 * math.pi * 440 * i / 8000)))
            for i in range(8000)
        )
        w.writeframes(frames)
    return path


def make_envelope(
    tmp_path: Path,
    *,
    approved: bool = False,
    inputs: tuple[EnvelopeInput, ...] | None = None,
    output_dir: str | None = None,
    allow_network: bool = False,
) -> ApprovedExecutionEnvelope:
    source = make_wav(tmp_path)
    if inputs is None:
        import hashlib

        inputs = (EnvelopeInput(role="source", path=str(source), sha256=hashlib.sha256(source.read_bytes()).hexdigest()),)
    envelope = ApprovedExecutionEnvelope(
        schema_version="approved-execution-envelope/0.1",
        envelope_id=f"env-{uuid.uuid4().hex[:8]}",
        case_id="case-test-1",
        capability_id="media.probe",
        provider_id="ffprobe.cli",
        inputs=inputs,
        parameters={},
        output_dir=output_dir or str((tmp_path / "out").resolve()),
        timeout_s=10.0,
        allow_network=allow_network,
    )
    if approved:
        envelope = sign_envelope(envelope, issuer="test-issuer", policy_version="policy/test")
    return envelope


class TestEnvelopeImmutability:
    def test_signature_derived_from_content(self, tmp_path: Path) -> None:
        e = make_envelope(tmp_path)
        assert envelope_signature(e) == envelope_signature(e)

    def test_approval_binds_signature(self, tmp_path: Path) -> None:
        e = make_envelope(tmp_path)
        signed = sign_envelope(e, issuer="op", policy_version="p/1")
        ok, _ = verify_envelope(signed)
        assert ok

    def test_mutation_invalidates_signature(self, tmp_path: Path) -> None:
        signed = make_envelope(tmp_path, approved=True)
        # mutate content by replacing inputs with a different hash
        mutated = ApprovedExecutionEnvelope(
            schema_version=signed.schema_version,
            envelope_id=signed.envelope_id,
            case_id=signed.case_id,
            capability_id=signed.capability_id,
            provider_id=signed.provider_id,
            inputs=(EnvelopeInput(role="source", path="C:/other.wav", sha256="f" * 64),),
            parameters=signed.parameters,
            output_dir=signed.output_dir,
            timeout_s=signed.timeout_s,
            allow_network=signed.allow_network,
            approval=signed.approval,
        )
        ok, reason = verify_envelope(mutated)
        assert not ok
        assert "signature mismatch" in reason

    def test_cannot_sign_twice(self, tmp_path: Path) -> None:
        signed = make_envelope(tmp_path, approved=True)
        with pytest.raises(ValueError, match="already approved"):
            sign_envelope(signed, issuer="x", policy_version="p/1")

    def test_serialization_roundtrip(self, tmp_path: Path) -> None:
        signed = make_envelope(tmp_path, approved=True)
        restored = envelope_loads(envelope_dumps(signed))
        assert restored == signed
        ok, _ = verify_envelope(restored)
        assert ok

    def test_unsigned_envelope_fails_verification(self, tmp_path: Path) -> None:
        e = make_envelope(tmp_path)
        ok, reason = verify_envelope(e)
        assert not ok
        assert "not approved" in reason


class TestGateway:
    def test_execute_requires_approval(self, tmp_path: Path) -> None:
        gateway = ExecutionGateway(adapters=[FfprobeAdapter()], store=FileRecordStore(tmp_path / "recs"))
        unsigned = make_envelope(tmp_path)
        record = gateway.execute(unsigned)
        assert record.status == "failed"
        assert record.error_class == "policy_rejection"
        assert "not approved" in record.errors[0]

    def test_input_hash_mismatch_rejected(self, tmp_path: Path) -> None:
        gateway = ExecutionGateway(adapters=[FfprobeAdapter()], store=FileRecordStore(tmp_path / "recs"))
        source = make_wav(tmp_path)
        envelope = make_envelope(
            tmp_path,
            approved=True,
            inputs=(EnvelopeInput(role="source", path=str(source), sha256="0" * 64),),
        )
        record = gateway.execute(envelope)
        assert record.status == "failed"
        assert record.error_class == "policy_rejection"
        assert "hash mismatch" in record.errors[0]

    def test_network_execution_rejected(self, tmp_path: Path) -> None:
        gateway = ExecutionGateway(adapters=[FfprobeAdapter()], store=FileRecordStore(tmp_path / "recs"))
        envelope = make_envelope(tmp_path, approved=True, allow_network=True)
        record = gateway.execute(envelope)
        assert record.status == "failed"
        assert "network" in record.errors[0]

    def test_tampered_envelope_rejected_at_gateway(self, tmp_path: Path) -> None:
        """Mutated capability/provider is caught by signature check — tampering
        cannot reach the adapter. This is the design guarantee of immutability."""
        gateway = ExecutionGateway(adapters=[FfprobeAdapter()], store=FileRecordStore(tmp_path / "recs"))
        envelope = make_envelope(tmp_path, approved=True)
        tampered = ApprovedExecutionEnvelope(
            schema_version=envelope.schema_version,
            envelope_id=envelope.envelope_id,
            case_id=envelope.case_id,
            capability_id="notation.render",  # tampered
            provider_id=envelope.provider_id,
            inputs=envelope.inputs,
            parameters=envelope.parameters,
            output_dir=envelope.output_dir,
            timeout_s=envelope.timeout_s,
            allow_network=envelope.allow_network,
            approval=envelope.approval,
        )
        record = gateway.execute(tampered)
        assert record.status == "failed"
        assert record.error_class == "policy_rejection"
        assert "signature mismatch" in record.errors[0]

    def test_successful_execution_records_evidence(self, tmp_path: Path) -> None:
        store = FileRecordStore(tmp_path / "recs")
        gateway = ExecutionGateway(adapters=[FfprobeAdapter()], store=store)
        envelope = make_envelope(tmp_path, approved=True)
        record = gateway.execute(envelope)
        assert record.status == "completed"
        assert record.exit_code == 0
        assert record.artifacts
        assert record.evidence.get("provider_version")
        saved = next((tmp_path / "recs").glob("rec-*.json"))
        assert saved.exists()

    def test_failure_record_preserves_evidence(self, tmp_path: Path) -> None:
        store = FileRecordStore(tmp_path / "recs")
        gateway = ExecutionGateway(adapters=[FfprobeAdapter()], store=store)
        envelope = make_envelope(tmp_path, approved=True)
        with mock.patch.object(FfprobeAdapter, "invoke") as mocked:
            from moodify.capability_registry.adapters.base import AdapterResult

            mocked.return_value = AdapterResult(
                status="failure", errors=("provider exploded",),
                error_class="provider_defect", exit_code=1, evidence={"detail": "boom"},
            )
            record = gateway.execute(envelope)
        assert record.status == "failed"
        assert record.error_class == "provider_defect"
        assert record.evidence.get("detail") == "boom"
        assert "provider exploded" in record.errors

    def test_in_flight_tracking(self, tmp_path: Path) -> None:
        gateway = ExecutionGateway(adapters=[FfprobeAdapter()], store=FileRecordStore(tmp_path / "recs"))
        envelope = make_envelope(tmp_path, approved=True)
        with mock.patch.object(FfprobeAdapter, "invoke") as mocked:
            from moodify.capability_registry.adapters.base import AdapterResult

            def slow_invoke(request):
                assert gateway.is_in_flight(envelope.envelope_id)
                return AdapterResult(status="success", artifacts=("x",), exit_code=0)

            mocked.side_effect = slow_invoke
            record = gateway.execute(envelope)
        assert record.status == "completed"
        assert not gateway.is_in_flight(envelope.envelope_id)

    def test_store_persists_record(self, tmp_path: Path) -> None:
        store = FileRecordStore(tmp_path / "recs")
        gateway = ExecutionGateway(adapters=[FfprobeAdapter()], store=store)
        envelope = make_envelope(tmp_path, approved=True)
        gateway.execute(envelope)
        files = list((tmp_path / "recs").glob("*.json"))
        assert len(files) == 1
        data = json.loads(files[0].read_text(encoding="utf-8"))
        assert data["case_id"] == "case-test-1"
        assert data["envelope_id"] == envelope.envelope_id
