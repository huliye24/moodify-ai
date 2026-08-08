from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import duckdb

from .hashing import sha256_bytes
from .schemas import HumanApproval, MeasurementRecord, ProductionCase, ValidationResult
from .serialization import canonical_json


class LedgerStore:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.db_path = self.root / "ledger.duckdb"
        self._migrate()

    def connect(self) -> duckdb.DuckDBPyConnection:
        return duckdb.connect(str(self.db_path))

    def _migrate(self) -> None:
        migration_dir = Path(__file__).parents[2] / "migrations"
        with self.connect() as con:
            con.execute("CREATE TABLE IF NOT EXISTS schema_migrations(version INTEGER PRIMARY KEY, applied_at TIMESTAMPTZ NOT NULL)")
            applied = {row[0] for row in con.execute("SELECT version FROM schema_migrations").fetchall()}
            for path in sorted(migration_dir.glob("*.sql")):
                version = int(path.stem.split("_", 1)[0])
                if version not in applied:
                    con.execute(path.read_text(encoding="utf-8"))
                    con.execute("INSERT INTO schema_migrations VALUES (?, ?)", [version, datetime.now(UTC)])

    def _append_event(self, con: duckdb.DuckDBPyConnection, aggregate_type: str,
                      aggregate_id: str, event_type: str, payload: str) -> None:
        con.execute(
            "INSERT INTO ledger_events(event_id,aggregate_type,aggregate_id,event_type,recorded_at,schema_version,payload_json,payload_sha256) VALUES (?,?,?,?,?,?,?,?)",
            [uuid4(), aggregate_type, aggregate_id, event_type, datetime.now(UTC), "1.0.0", payload, sha256_bytes(payload.encode())],
        )

    def create_case(self, case: ProductionCase) -> None:
        payload = canonical_json(case)
        with self.connect() as con:
            count_row = con.execute("SELECT count(*) FROM cases WHERE case_id=?", [case.case_id]).fetchone()
            if count_row is not None and count_row[0]:
                raise ValueError(f"Case already exists and is immutable: {case.case_id}")
            con.execute("INSERT INTO cases VALUES (?,?,?,?,?,?,?)", [case.case_id, case.created_at, case.title, case.moodify_version, case.golden, payload, sha256_bytes(payload.encode())])
            self._append_event(con, "case", str(case.case_id), "created", payload)

    def get_case(self, case_id: UUID) -> ProductionCase:
        with self.connect() as con:
            row = con.execute("SELECT payload_json FROM cases WHERE case_id=?", [case_id]).fetchone()
        if row is None:
            raise KeyError(f"Case not found: {case_id}")
        return ProductionCase.model_validate(json.loads(row[0]))

    def append_revision(self, case_id: UUID, patch: dict[str, Any], reason: str) -> None:
        self.get_case(case_id)
        payload = json.dumps({"patch": patch, "reason": reason}, sort_keys=True, separators=(",", ":"))
        with self.connect() as con:
            self._append_event(con, "case", str(case_id), "revision_appended", payload)

    def add_measurement(self, record: MeasurementRecord) -> None:
        self.get_case(record.case_id)
        payload = canonical_json(record)
        with self.connect() as con:
            con.execute("INSERT INTO measurements VALUES (?,?,?,?,?,?,?,?)", [record.measurement_id, record.case_id, record.asset_id, record.adapter, record.measured_at, record.parquet_path, payload, sha256_bytes(payload.encode())])
            self._append_event(con, "measurement", str(record.measurement_id), "recorded", payload)

    def measurements(self, case_id: UUID) -> list[MeasurementRecord]:
        with self.connect() as con:
            rows = con.execute("SELECT payload_json FROM measurements WHERE case_id=? ORDER BY measured_at, measurement_id", [case_id]).fetchall()
        return [MeasurementRecord.model_validate(json.loads(row[0])) for row in rows]

    def add_approval(self, approval: HumanApproval) -> None:
        payload = canonical_json(approval)
        with self.connect() as con:
            con.execute("INSERT INTO approvals VALUES (?,?,?,?,?,?,?)", [approval.approval_id, approval.rule_id, approval.rule_version, approval.approver, approval.approved_at, payload, sha256_bytes(payload.encode())])
            self._append_event(con, "rule", approval.rule_id, "human_approval_recorded", payload)

    def approval(self, rule_id: str, version: str) -> HumanApproval | None:
        with self.connect() as con:
            row = con.execute("SELECT payload_json FROM approvals WHERE rule_id=? AND rule_version=? ORDER BY approved_at DESC LIMIT 1", [rule_id, version]).fetchone()
        return None if row is None else HumanApproval.model_validate(json.loads(row[0]))

    def add_validation(self, result: ValidationResult) -> None:
        payload = canonical_json(result)
        with self.connect() as con:
            con.execute("INSERT INTO validations VALUES (?,?,?,?,?,?)", [result.validation_id, result.subject_type, result.subject_id, result.checked_at, result.valid, payload])
            self._append_event(con, result.subject_type, result.subject_id, "validated", payload)
