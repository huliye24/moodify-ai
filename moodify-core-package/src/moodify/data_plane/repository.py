"""Metadata repository (W01-P03).

Data identity backbone DAO：tracks / jobs / objects / evidence / versions。
P03 只建立字段承载能力，不定义最终 authoritative state machine（P04 范围）。
实现基于 SQLite（可替换为 PolarDB MySQL——migration SQL 见 migrations/）。
所有写入幂等（INV-11）；orphan / missing 可检测（INV-08/09）。
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS tracks (
    track_id TEXT PRIMARY KEY,
    owner_scope TEXT,
    source_object_id TEXT,
    source_hash TEXT NOT NULL,
    source_format TEXT,
    source_duration_ms INTEGER,
    source_sample_rate INTEGER,
    source_channels INTEGER,
    status_class TEXT,
    canonical_source_version TEXT,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS jobs (
    job_id TEXT PRIMARY KEY,
    track_id TEXT NOT NULL REFERENCES tracks(track_id),
    job_type TEXT NOT NULL,
    requested_at TEXT,
    created_by TEXT,
    pipeline_version TEXT,
    processing_profile_version TEXT,
    current_state TEXT,
    current_attempt INTEGER DEFAULT 0,
    failure_code TEXT,
    failure_summary TEXT,
    started_at TEXT,
    finished_at TEXT,
    ready_object_id TEXT
);
CREATE TABLE IF NOT EXISTS objects (
    object_id TEXT PRIMARY KEY,
    track_id TEXT NOT NULL REFERENCES tracks(track_id),
    job_id TEXT REFERENCES jobs(job_id),
    artifact_type TEXT NOT NULL,
    artifact_role TEXT,
    bucket TEXT NOT NULL,
    object_key TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    hash_algorithm TEXT NOT NULL DEFAULT 'sha256',
    byte_size INTEGER NOT NULL,
    mime_type TEXT,
    producer TEXT NOT NULL,
    producer_version TEXT,
    pipeline_version TEXT,
    parent_object_id TEXT,
    immutable INTEGER NOT NULL DEFAULT 1,
    retention_class TEXT NOT NULL,
    evidence_class TEXT,
    created_at TEXT NOT NULL,
    UNIQUE (object_key)
);
CREATE TABLE IF NOT EXISTS evidence (
    evidence_id TEXT PRIMARY KEY,
    track_id TEXT NOT NULL REFERENCES tracks(track_id),
    job_id TEXT REFERENCES jobs(job_id),
    object_id TEXT REFERENCES objects(object_id),
    evidence_type TEXT NOT NULL,
    claim TEXT NOT NULL,
    method TEXT,
    evaluator TEXT,
    evaluator_version TEXT,
    verdict TEXT,
    uncertainty REAL,
    evidence_object_id TEXT,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS versions (
    version_id TEXT PRIMARY KEY,
    version_kind TEXT NOT NULL,
    version_value TEXT NOT NULL,
    created_at TEXT NOT NULL,
    status TEXT,
    UNIQUE (version_kind, version_value)
);
"""


class DataPlaneRepository:
    """Idempotent, traceable metadata store (SQLite implementation)."""

    def __init__(self, db_path: str | Path) -> None:
        self._conn = sqlite3.connect(str(db_path))
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(SCHEMA)
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    # ---------- tracks ----------

    def register_track(
        self,
        *,
        track_id: str,
        source_hash: str,
        source_object_id: str | None = None,
        owner_scope: str | None = None,
        source_format: str | None = None,
        status_class: str | None = "INTAKE",
        created_at: str | None = None,
    ) -> dict:
        """Idempotent: same track_id re-registers as no-op returning existing row."""
        existing = self._conn.execute("SELECT * FROM tracks WHERE track_id=?", (track_id,)).fetchone()
        if existing:
            return dict(existing)
        self._conn.execute(
            "INSERT INTO tracks (track_id, owner_scope, source_object_id, source_hash, source_format, status_class, created_at)"
            " VALUES (?,?,?,?,?,?,COALESCE(?, datetime('now')))",
            (track_id, owner_scope, source_object_id, source_hash, source_format, status_class, created_at),
        )
        self._conn.commit()
        row = self._conn.execute("SELECT * FROM tracks WHERE track_id=?", (track_id,)).fetchone()
        return dict(row)

    def get_track(self, track_id: str) -> dict | None:
        row = self._conn.execute("SELECT * FROM tracks WHERE track_id=?", (track_id,)).fetchone()
        return dict(row) if row else None

    # ---------- jobs ----------

    def register_job(
        self,
        *,
        job_id: str,
        track_id: str,
        job_type: str,
        pipeline_version: str | None = None,
        current_state: str = "CREATED",
        created_by: str | None = None,
        requested_at: str | None = None,
    ) -> dict:
        existing = self._conn.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
        if existing:
            return dict(existing)
        self._conn.execute(
            "INSERT INTO jobs (job_id, track_id, job_type, pipeline_version, current_state, created_by, requested_at)"
            " VALUES (?,?,?,?,?,?,COALESCE(?, datetime('now')))",
            (job_id, track_id, job_type, pipeline_version, current_state, created_by, requested_at),
        )
        self._conn.commit()
        row = self._conn.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
        return dict(row)

    def update_job_state(self, job_id: str, *, current_state: str, failure_code: str | None = None, failure_summary: str | None = None) -> None:
        self._conn.execute(
            "UPDATE jobs SET current_state=?, failure_code=COALESCE(?, failure_code), failure_summary=COALESCE(?, failure_summary)"
            " WHERE job_id=?",
            (current_state, failure_code, failure_summary, job_id),
        )
        self._conn.commit()

    def get_job(self, job_id: str) -> dict | None:
        row = self._conn.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
        return dict(row) if row else None

    # ---------- objects ----------

    def register_object(
        self,
        *,
        object_id: str,
        track_id: str,
        artifact_type: str,
        bucket: str,
        object_key: str,
        content_hash: str,
        byte_size: int,
        producer: str,
        job_id: str | None = None,
        artifact_role: str | None = None,
        mime_type: str | None = None,
        producer_version: str | None = None,
        pipeline_version: str | None = None,
        parent_object_id: str | None = None,
        immutable: bool = True,
        retention_class: str = "render_versioned",
        evidence_class: str | None = None,
        created_at: str | None = None,
    ) -> dict:
        """Idempotent by object_id: repeated registration returns existing row."""
        existing = self._conn.execute("SELECT * FROM objects WHERE object_id=?", (object_id,)).fetchone()
        if existing:
            return dict(existing)
        self._conn.execute(
            "INSERT INTO objects (object_id, track_id, job_id, artifact_type, artifact_role, bucket, object_key,"
            " content_hash, byte_size, mime_type, producer, producer_version, pipeline_version, parent_object_id,"
            " immutable, retention_class, evidence_class, created_at)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,COALESCE(?, datetime('now')))",
            (object_id, track_id, job_id, artifact_type, artifact_role, bucket, object_key,
             content_hash, byte_size, mime_type, producer, producer_version, pipeline_version, parent_object_id,
             int(immutable), retention_class, evidence_class, created_at),
        )
        self._conn.commit()
        row = self._conn.execute("SELECT * FROM objects WHERE object_id=?", (object_id,)).fetchone()
        return dict(row)

    def get_object(self, object_id: str) -> dict | None:
        row = self._conn.execute("SELECT * FROM objects WHERE object_id=?", (object_id,)).fetchone()
        return dict(row) if row else None

    def find_by_key(self, object_key: str) -> dict | None:
        row = self._conn.execute("SELECT * FROM objects WHERE object_key=?", (object_key,)).fetchone()
        return dict(row) if row else None

    # ---------- evidence ----------

    def register_evidence(
        self,
        *,
        evidence_id: str,
        track_id: str,
        evidence_type: str,
        claim: str,
        object_id: str | None = None,
        job_id: str | None = None,
        method: str | None = None,
        evaluator: str | None = None,
        evaluator_version: str | None = None,
        verdict: str | None = None,
        uncertainty: float | None = None,
        evidence_object_id: str | None = None,
        created_at: str | None = None,
    ) -> dict:
        """INV-07: evidence must carry a claim."""
        if not claim or not claim.strip():
            raise ValueError("evidence requires a non-empty claim (INV-07)")
        existing = self._conn.execute("SELECT * FROM evidence WHERE evidence_id=?", (evidence_id,)).fetchone()
        if existing:
            return dict(existing)
        self._conn.execute(
            "INSERT INTO evidence (evidence_id, track_id, job_id, object_id, evidence_type, claim, method,"
            " evaluator, evaluator_version, verdict, uncertainty, evidence_object_id, created_at)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,COALESCE(?, datetime('now')))",
            (evidence_id, track_id, job_id, object_id, evidence_type, claim, method,
             evaluator, evaluator_version, verdict, uncertainty, evidence_object_id, created_at),
        )
        self._conn.commit()
        row = self._conn.execute("SELECT * FROM evidence WHERE evidence_id=?", (evidence_id,)).fetchone()
        return dict(row)

    # ---------- invariants / detection ----------

    def missing_objects(self, adapter) -> list[dict]:
        """INV-09: DB references objects the store does not have."""
        out: list[dict] = []
        for row in self._conn.execute("SELECT * FROM objects").fetchall():
            o = dict(row)
            if adapter.head(o["bucket"], o["object_key"]) is None:
                out.append(o)
        return out

    def orphan_objects(self, adapter, prefix: str = "") -> list[str]:
        """INV-08: store has objects the DB does not reference (optional prefix filter)."""
        keys = {row["object_key"] for row in self._conn.execute("SELECT object_key FROM objects").fetchall()}
        orphans: list[str] = []
        buckets = self._list_buckets(adapter)
        for bucket in buckets:
            for k in adapter.list_prefix(bucket, prefix):
                if k not in keys:
                    orphans.append(f"{bucket}/{k}")
        return orphans

    @staticmethod
    def _list_buckets(adapter) -> list[str]:
        # LocalFileAdapter stores buckets as top-level dirs; OSS adapter not yet usable.
        try:
            base = adapter.root
        except AttributeError:
            return []
        if not base.exists():
            return []
        return [d.name for d in sorted(base.iterdir()) if d.is_dir()]

    # ---------- provenance ----------

    def provenance_chain(self, object_id: str) -> list[dict] | None:
        """Trace object -> job -> track -> source (INV-05/06)."""
        obj = self.get_object(object_id)
        if obj is None:
            return None
        track = self.get_track(obj["track_id"])
        job = self.get_job(obj["job_id"]) if obj.get("job_id") else None
        source_obj = self.get_object(track["source_object_id"]) if track and track.get("source_object_id") else None
        return [
            {"stage": "object", "data": obj},
            {"stage": "job", "data": job},
            {"stage": "track", "data": track},
            {"stage": "source_object", "data": source_obj},
        ]

    def versions(self) -> list[dict]:
        return [dict(r) for r in self._conn.execute("SELECT * FROM versions ORDER BY created_at").fetchall()]
