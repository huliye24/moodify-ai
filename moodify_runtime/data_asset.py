"""Unified job data pipeline — DSK-MFY-DATA-ASSET-001.

Collects every job's structured output (acoustic scans, scores, gates,
review labels, craft, evidence references) into one schema'd, append-only
store. Records are append-only; dedup is by content-derived record_id;
missing measurements are explicit nulls with reasons, never fabricated.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
import time
from pathlib import Path

SCHEMA_VERSION = "1.0.0"
SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schemas" / "job_data_record.schema.json"

DIMENSIONS = ("clarity", "warmth", "space", "harshness_control",
              "plastic_feel_control", "artifact_control", "target_fit")


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def record_id(record_type: str, *parts: str) -> str:
    raw = "\x00".join(parts)
    return f"{record_type}-{hashlib.sha256(raw.encode('utf-8')).hexdigest()[:16]}"


def load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def validate_record(record: dict) -> list[str]:
    """Return a list of schema violations; empty list means valid."""
    import jsonschema
    try:
        jsonschema.validate(record, load_schema())
        return []
    except jsonschema.ValidationError as exc:
        return [f"{'.'.join(str(p) for p in exc.path) or '<root>'}: {exc.message}"]


class _SkipSource(Exception):
    """Raised by collectors for files that are not the expected record type."""


# --------------------------------------------------------------- collectors

def collect_treatment_record(path: Path) -> dict:
    """treatment_records/*.json -> JobDataRecord (record_type=treatment)."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("record_type") != "moodify_treatment_record":
        raise _SkipSource(f"{path} is not a moodify_treatment_record")
    source_artifacts = {"treatment_record": str(path)}
    source_artifacts.update({k: v for k, v in data.get("paths", {}).items() if isinstance(v, str)})
    record = {
        "record_id": record_id("treatment", str(path), json.dumps(data.get("before_features", {}), sort_keys=True)),
        "record_type": "treatment",
        "schema_version": SCHEMA_VERSION,
        "collected_at": _now(),
        "source_artifacts": source_artifacts,
        "job": {"job_id": data.get("song_id", "unknown"), "status": "COMPLETED"},
        "scan": {"before_features": data.get("before_features", {}),
                 "after_features": data.get("after_features", {}),
                 "delta_features": data.get("delta_features", {})},
        "scores": {"mrs": None, "mrs_not_available": "case predates MRS scoring"},
        "gates": {"status": "NONE", "checks": {}},
        "review": _human_feedback_review(data.get("human_feedback", {})),
        "craft": {"preset": data.get("preset", ""),
                  "params": data.get("preset_params", {}),
                  "steps": data.get("preset_params", {}).get("steps", [])},
        "evidence": {},
    }
    _attach_audio(record, data.get("paths", {}).get("before_audio", ""))
    return record


def _human_feedback_review(feedback: dict) -> dict | None:
    if not isinstance(feedback, dict) or not feedback:
        return None
    preset = feedback.get("preset") or feedback.get("candidate")
    if not preset:
        return None
    dims = {d: feedback.get(d) for d in DIMENSIONS}
    dims = {k: v for k, v in dims.items() if isinstance(v, int) and 1 <= v <= 5}
    return {"preset": preset, "listener": feedback.get("listener", ""),
            "better_than_before": feedback.get("better_than_before"),
            "dimensions": dims, "notes": feedback.get("notes", "")}


def collect_listening_scorecard(path: Path) -> list[dict]:
    """listening_test/**/*scorecard*.md -> one JobDataRecord per preset section."""
    text = Path(path).read_text(encoding="utf-8")
    song_id = _markdown_field(text, "song_id") or path.parent.name
    source_file = _markdown_field(text, "源文件") or _markdown_field(text, "source_file")
    listener = _markdown_field(text, "试听者") or _markdown_field(text, "listener")
    volume_matched = _markdown_bool(text, "volume_matched")
    records = []
    sections = re.split(r"\n###\s+", text)
    for section in sections[1:]:
        header = section.split("\n", 1)[0].strip()
        match = re.match(r"([A-Za-z0-9_]+)", header)
        preset = match.group(1) if match else header
        dims = {}
        for dim in DIMENSIONS:
            value = _dimension_value(section, dim)
            if value is not None:
                dims[dim] = value
        better = _markdown_field(section, "better_than_before")
        notes = _notes_from(section)
        record = {
            "record_id": record_id("listening", str(path), preset),
            "record_type": "listening",
            "schema_version": SCHEMA_VERSION,
            "collected_at": _now(),
            "source_artifacts": {"scorecard": str(path)},
            "job": {"job_id": f"{song_id}_{preset}", "status": "COMPLETED"},
            "scores": {"mrs": None, "mrs_not_available": "case predates MRS scoring"},
            "gates": {"status": "NONE", "checks": {}},
            "review": {
                "preset": preset, "listener": listener or "",
                "volume_matched": volume_matched,
                "better_than_before": _parse_bool(better),
                "dimensions": dims, "notes": notes},
            "craft": {"preset": preset},
            "evidence": {},
        }
        _attach_audio(record, source_file)
        records.append(record)
    return records


def _markdown_field(text: str, key: str) -> str:
    pattern = re.compile(
        r"^\|\s*" + re.escape(key) + r"\s*\|\s*(.*?)\s*\|", re.MULTILINE)
    match = pattern.search(text)
    if not match:
        return ""
    value = match.group(1).strip()
    return value.strip("`")


def _markdown_bool(text: str, key: str) -> bool | None:
    return _parse_bool(_markdown_field(text, key))


def _parse_bool(value: str) -> bool | None:
    if not value:
        return None
    return value.strip().lower() in {"true", "yes", "是", "1"}


def _dimension_value(section: str, dim: str) -> int | None:
    match = re.search(r"^\|\s*" + re.escape(dim) + r"[^|]*\|\s*(\d)\s*\|", section, re.MULTILINE)
    if not match:
        match = re.search(dim + r"\s*=\s*(\d)", section)
    if not match:
        return None
    value = int(match.group(1))
    return value if 1 <= value <= 5 else None


def _notes_from(section: str) -> str:
    match = re.search(r"\*\*听感备注：\*\*\s*(.*?)(\n##|\n###|\n\*\*快速|\Z)", section, re.DOTALL)
    if not match:
        return ""
    return match.group(1).strip().strip("`").strip()


def collect_metrics_comparison(path: Path) -> dict:
    """inspector_reports/*/metrics_comparison.json -> JobDataRecord."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    record = {
        "record_id": record_id("metrics_comparison", str(path)),
        "record_type": "metrics_comparison",
        "schema_version": SCHEMA_VERSION,
        "collected_at": _now(),
        "source_artifacts": {"metrics_comparison": str(path)},
        "job": {"job_id": data.get("preset", ""), "status": "COMPLETED"},
        "scan": {"before_features": data.get("before", {}),
                 "after_features": data.get("after", {}),
                 "delta_features": data.get("delta", {}),
                 "loudness": data.get("loudness", {})},
        "scores": {"mrs": None, "mrs_not_available": "case predates MRS scoring"},
        "gates": {"status": "NONE", "checks": {}},
        "craft": {"preset": data.get("preset", "")},
        "evidence": {},
    }
    _attach_audio(record, data.get("before_path", ""))
    return record


def collect_night_metric_record(path: Path) -> dict:
    """reports/**/night_metric_record.json -> JobDataRecord."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    source_artifacts = {"night_metric_record": str(path)}
    source_artifacts.update({k: v for k, v in data.get("source_artifacts", {}).items() if isinstance(v, str)})
    return {
        "record_id": record_id("night_metric", str(path)),
        "record_type": "night_metric",
        "schema_version": SCHEMA_VERSION,
        "collected_at": _now(),
        "source_artifacts": source_artifacts,
        "job": {"job_id": data.get("run_id", ""), "status": "COMPLETED" if not data.get("fatal_error") else "FAILED"},
        "scores": {"mrs": None, "mrs_not_available": "night metric has no MRS score"},
        "gates": {"status": "NONE", "checks": {}},
        "evidence": {},
    }


def collect_evidence_package(path: Path) -> dict:
    """Formal evidence package (artifacts/verification/**/evidence) -> JobDataRecord."""
    evidence_dir = Path(path)
    if evidence_dir.is_file() and evidence_dir.name == "evidence_manifest.json":
        evidence_dir = evidence_dir.parent
    manifest = json.loads((evidence_dir / "evidence_manifest.json").read_text(encoding="utf-8"))
    case = json.loads((evidence_dir / "case.json").read_text(encoding="utf-8"))
    execution = {}
    verification = {}
    analysis = {}
    gate = {}
    plan = {}
    approval = {}
    if (evidence_dir / "execution_record.json").exists():
        execution = json.loads((evidence_dir / "execution_record.json").read_text(encoding="utf-8"))
    if (evidence_dir / "verification_result.json").exists():
        verification = json.loads((evidence_dir / "verification_result.json").read_text(encoding="utf-8"))
    if (evidence_dir / "analysis.json").exists():
        analysis = json.loads((evidence_dir / "analysis.json").read_text(encoding="utf-8"))
    if (evidence_dir / "technical_gate.json").exists():
        gate = json.loads((evidence_dir / "technical_gate.json").read_text(encoding="utf-8"))
    if (evidence_dir / "plan.json").exists():
        plan = json.loads((evidence_dir / "plan.json").read_text(encoding="utf-8"))
    if (evidence_dir / "artistic_approval.json").exists():
        approval = json.loads((evidence_dir / "artistic_approval.json").read_text(encoding="utf-8"))
    output_sha = execution.get("output_sha256", "")
    source_artifacts = {name: str(evidence_dir / name)
                        for name in sorted(p.name for p in evidence_dir.iterdir() if p.is_file())}
    record = {
        "record_id": record_id("evidence_package", str(evidence_dir)),
        "record_type": "evidence_package",
        "schema_version": SCHEMA_VERSION,
        "collected_at": _now(),
        "source_artifacts": source_artifacts,
        "job": {"job_id": case.get("case_id", ""), "case_id": case.get("case_id", ""),
                "status": case.get("state", "")},
        "scan": {"features": analysis},
        "scores": {"mrs": None, "mrs_not_available": "case predates MRS scoring"},
        "gates": {"status": gate.get("status", "NONE"), "checks": gate.get("checks", {}),
                  "errors": gate.get("errors", []), "checked_at": gate.get("checked_at", "")},
        "craft": {"preset": "", "chain": "", "engine_name": manifest.get("engine_name", ""),
                  "engine_version": manifest.get("engine_version", ""),
                  "steps": plan.get("steps", [])},
        "evidence": {
            "evidence_dir": str(evidence_dir),
            "evidence_manifest": {k: manifest[k] for k in (
                "case_id", "source_sha256", "plan_hash", "approval_id", "execution_id",
                "engine_name", "engine_version", "output_sha256", "verification_id",
                "verification_status", "moodify_version") if k in manifest},
            "execution_id": execution.get("execution_id", ""),
            "verification_id": verification.get("verification_id", ""),
            "verification_status": verification.get("status", ""),
            "output_path": execution.get("output_path", ""),
            "output_sha256": output_sha,
        },
    }
    if approval:
        record["evidence"]["approval"] = {"approval_id": approval.get("approval_id", ""),
                                          "human_owner": approval.get("human_owner", "")}
    source_path = case.get("source_path", "")
    source_sha = case.get("source_sha256", "")
    if (len(source_sha) == 64 and source_path and Path(source_path).is_file()):
        record["source_audio"] = {"path": source_path, "sha256": source_sha}
    return record


def _audio_identity(path: str) -> dict | None:
    """Return source_audio identity only when the file actually exists."""
    if not path:
        return None
    p = Path(path)
    if not p.is_file():
        return None
    return {"path": str(p), "sha256": _sha256_file(p)}


def _attach_audio(record: dict, path: str) -> None:
    identity = _audio_identity(path)
    if identity is not None:
        record["source_audio"] = identity


# ---------------------------------------------------------------- store

class DataAssetStore:
    """Append-only JSONL store, one file per record_type, atomic appends."""

    def __init__(self, root: Path):
        self.root = Path(root)
        self.records_dir = self.root / "records"
        self.records_dir.mkdir(parents=True, exist_ok=True)
        self._known: set[str] = set()
        self._load_known()

    def _file_for(self, record_type: str) -> Path:
        return self.records_dir / f"{record_type}.jsonl"

    def _load_known(self) -> None:
        for path in self.records_dir.glob("*.jsonl"):
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    try:
                        self._known.add(json.loads(line)["record_id"])
                    except (json.JSONDecodeError, KeyError):
                        continue

    def append(self, record: dict) -> bool:
        """Validate, dedup, append. Returns True when a new record was stored."""
        errors = validate_record(record)
        if errors:
            raise ValueError("record invalid: " + "; ".join(errors[:5]))
        if record["record_id"] in self._known:
            return False
        target = self._file_for(record["record_type"])
        line = json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n"
        fd, tmp_name = tempfile.mkstemp(prefix=".append.", suffix=".tmp", dir=self.records_dir)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                if target.exists():
                    handle.write(target.read_text(encoding="utf-8"))
                handle.write(line)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(tmp_name, target)
        finally:
            if os.path.exists(tmp_name):
                os.unlink(tmp_name)
        self._known.add(record["record_id"])
        return True

    def load_record(self, record_id_value: str) -> dict | None:
        for path in self.records_dir.glob("*.jsonl"):
            for line in path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if record.get("record_id") == record_id_value:
                    return record
        return None

    def all_records(self) -> list[dict]:
        records = []
        for path in sorted(self.records_dir.glob("*.jsonl")):
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        return records

    def stats(self) -> dict:
        counts: dict[str, int] = {}
        for record in self.all_records():
            counts[record["record_type"]] = counts.get(record["record_type"], 0) + 1
        return {"total": sum(counts.values()), "by_type": counts}


# ---------------------------------------------------------------- backfill

SOURCE_REGISTRY = [
    ("treatment", "treatment_records", "*.json", collect_treatment_record),
    ("listening", "listening_test", "**/*scorecard*.md", collect_listening_scorecard),
    ("metrics_comparison", "inspector_reports", "*/metrics_comparison.json", collect_metrics_comparison),
    ("night_metric", "reports", "**/night_metric_record.json", collect_night_metric_record),
    ("evidence_package", "artifacts", "**/evidence/evidence_manifest.json", collect_evidence_package),
]


def ingest_sources(store: DataAssetStore, repo_root: Path,
                   registry: list | None = None) -> dict:
    """Walk registered source locations and ingest every parseable record."""
    registry = registry or SOURCE_REGISTRY
    stats: dict[str, dict] = {}
    manifest: dict[str, str] = {}
    for record_type, relative_dir, pattern, collector in registry:
        base = repo_root / relative_dir
        if not base.exists():
            stats[record_type] = {"files": 0, "records": 0, "errors": 0}
            continue
        files = list(base.glob(pattern))
        ingested = 0
        errors = 0
        for source_path in files:
            try:
                records = collector(source_path)
                if isinstance(records, dict):
                    records = [records]
                for record in records:
                    if store.append(record):
                        ingested += 1
                    manifest[record["record_id"]] = str(source_path)
            except _SkipSource:
                continue
            except (OSError, json.JSONDecodeError, ValueError, KeyError) as exc:
                errors += 1
                manifest[f"__error__:{source_path}"] = str(exc)[:200]
        stats[record_type] = {"files": len(files), "records": ingested, "errors": errors}
    (store.root / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    return stats
