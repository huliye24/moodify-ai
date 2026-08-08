"""ExecutionGateway — the single approved execution entry point.

Every provider execution must pass through the gateway (Law 3). The gateway:
1. verifies the envelope approval signature (immutability);
2. re-verifies input hashes against the locked values;
3. enforces permissions (network off unless allowed, output whitelist);
4. runs the adapter and records the full ExecutionRecord;
5. refuses unapproved or mutated envelopes.

Adapters must not be invoked directly by workflow code; the gateway tracks
in-flight executions so bypass attempts are detectable in tests.
"""

from __future__ import annotations

import datetime
import uuid
from pathlib import Path
from typing import Protocol

from moodify.capability_registry.adapters import all_adapters
from moodify.capability_registry.adapters.base import InvokeRequest, ProviderAdapter
from moodify.capability_registry.execution.envelope import (
    ApprovedExecutionEnvelope,
    ExecutionRecord,
    verify_envelope,
)

RECORD_SCHEMA = "execution-record/0.1"


def _utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class RecordStore(Protocol):
    def save_record(self, record: ExecutionRecord) -> Path: ...


class FileRecordStore:
    """Persist ExecutionRecords as JSONL under a case directory."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def save_record(self, record: ExecutionRecord) -> Path:
        self.root.mkdir(parents=True, exist_ok=True)
        target = self.root / f"{record.record_id}.json"
        from moodify.capability_registry.execution.envelope import record_dumps

        target.write_text(record_dumps(record), encoding="utf-8")
        return target


class ExecutionGateway:
    def __init__(
        self,
        adapters: list[ProviderAdapter] | None = None,
        store: RecordStore | None = None,
    ) -> None:
        self._adapters = {a.provider_id: a for a in (adapters if adapters is not None else all_adapters())}
        self._store = store or FileRecordStore(Path("execution_records"))
        self._in_flight: set[str] = set()

    def adapter_for(self, provider_id: str) -> ProviderAdapter | None:
        return self._adapters.get(provider_id)

    def adapter_for_capability(self, capability_id: str) -> ProviderAdapter | None:
        for adapter in self._adapters.values():
            if adapter.capability_id == capability_id:
                return adapter
        return None

    # ── envelope validation ─────────────────────────────────────────────
    def _validate(self, envelope: ApprovedExecutionEnvelope) -> tuple[bool, str]:
        ok, reason = verify_envelope(envelope)
        if not ok:
            return False, reason
        if envelope.allow_network:
            return False, "network execution is not permitted by this gateway"
        out_dir = Path(envelope.output_dir)
        if not out_dir.is_absolute():
            return False, f"output_dir must be absolute: {envelope.output_dir}"
        adapter = self._adapters.get(envelope.provider_id)
        if adapter is None:
            return False, f"unknown provider: {envelope.provider_id}"
        if adapter.capability_id != envelope.capability_id:
            return False, (
                f"provider {envelope.provider_id} serves {adapter.capability_id}, "
                f"envelope requests {envelope.capability_id}"
            )
        # input hash re-verification against locked values
        for entry in envelope.inputs:
            path = Path(entry.path)
            if not path.exists():
                return False, f"input missing: {entry.path}"
            import hashlib

            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            if actual != entry.sha256:
                return False, f"input hash mismatch for role {entry.role}: {actual} != {entry.sha256}"
        return True, "envelope valid"

    # ── execution ───────────────────────────────────────────────────────
    def execute(self, envelope: ApprovedExecutionEnvelope) -> ExecutionRecord:
        record_id = f"rec-{uuid.uuid4().hex[:12]}"
        started = _utc_now()
        ok, reason = self._validate(envelope)
        if not ok:
            record = ExecutionRecord(
                schema_version=RECORD_SCHEMA,
                record_id=record_id,
                case_id=envelope.case_id,
                envelope_id=envelope.envelope_id,
                status="failed",
                provider_id=envelope.provider_id,
                capability_id=envelope.capability_id,
                started_at=started,
                finished_at=_utc_now(),
                errors=(reason,),
                error_class="policy_rejection",
                evidence={"validation": reason},
            )
            self._store.save_record(record)
            return record

        adapter = self._adapters[envelope.provider_id]
        request = InvokeRequest(
            capability_id=envelope.capability_id,
            inputs={entry.role: entry.path for entry in envelope.inputs},
            parameters=dict(envelope.parameters),
            output_dir=envelope.output_dir,
            timeout_s=envelope.timeout_s,
            allow_network=envelope.allow_network,
        )

        self._in_flight.add(envelope.envelope_id)
        try:
            result = adapter.invoke(request)
        finally:
            self._in_flight.discard(envelope.envelope_id)

        status: str = "completed" if result.status == "success" else "failed"
        record = ExecutionRecord(
            schema_version=RECORD_SCHEMA,
            record_id=record_id,
            case_id=envelope.case_id,
            envelope_id=envelope.envelope_id,
            status=status,
            provider_id=envelope.provider_id,
            capability_id=envelope.capability_id,
            started_at=started,
            finished_at=_utc_now(),
            exit_code=result.exit_code,
            elapsed_s=result.elapsed_s,
            artifacts=result.artifacts,
            errors=result.errors,
            error_class=result.error_class,
            evidence=result.evidence,
        )
        self._store.save_record(record)
        return record

    # ── unauthorized-execution detection (tests) ────────────────────────
    def is_in_flight(self, envelope_id: str) -> bool:
        return envelope_id in self._in_flight

    def active_execution_count(self) -> int:
        return len(self._in_flight)
