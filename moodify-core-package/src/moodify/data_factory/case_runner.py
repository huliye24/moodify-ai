"""Deterministic Case Runner — idempotent, atomic, configuration-snapshotted.

MFY_EAR_DETERMINISTIC_CASE_RUNNER_001:
- canonical orchestration path = data_factory.runner.run_production_case
  (queue/worker path); the synchronous /analyze route is an adapter, not a
  second state machine.
- idempotency: same (idempotency_key) never produces a second case.
- atomicity: work lands in a temp dir and is promoted to the final case dir
  only on success.
- stable failure codes: INVALID_INPUT / HASH_FAILED / EXECUTION_FAILED.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from moodify.auditory.manifests import sha256_file
from moodify.auditory.profiles import get_profile
from moodify.data_factory.runner import run_production_case
try:
    from moodify.node.models import utc_now_iso  # type: ignore[no-redef]
except ImportError:  # pragma: no cover
    def utc_now_iso() -> str:
        from datetime import datetime, timezone

        return datetime.now(timezone.utc).isoformat()


IDEMPOTENCY_FILE = ".idempotency.json"
CONFIG_FILE = "case_config.json"

FAILURE_INVALID_INPUT = "INVALID_INPUT"
FAILURE_HASH_FAILED = "HASH_FAILED"
FAILURE_EXECUTION_FAILED = "EXECUTION_FAILED"


class CaseRunnerError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


class CaseRunner:
    def __init__(self, output_root: Path):
        self.output_root = Path(output_root)
        self.output_root.mkdir(parents=True, exist_ok=True)

    def _idempotency_path(self, idempotency_key: str) -> Path:
        return self.output_root / "cases" / ".idempotency" / f"{idempotency_key}.json"

    def _existing_for_key(self, idempotency_key: str) -> Path | None:
        marker = self._idempotency_path(idempotency_key)
        if marker.is_file():
            return Path(json.loads(marker.read_text(encoding="utf-8"))["case_dir"])
        return None

    def _record_key(self, idempotency_key: str, case_dir: Path) -> None:
        marker = self._idempotency_path(idempotency_key)
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text(
            json.dumps({"idempotency_key": idempotency_key, "case_dir": str(case_dir)}, indent=2),
            encoding="utf-8",
        )

    def submit(
        self,
        source_path: Path,
        *,
        idempotency_key: str,
        scan_profile_id: str = "MFY-WSE-SCAN-PROFILE-001",
    ) -> Path:
        """Run one case deterministically; returns the canonical case dir.

        Same idempotency_key + same source => the existing completed case is
        returned (no second case, no duplicate artifacts).
        """
        source_path = Path(source_path)
        if not source_path.is_file():
            raise CaseRunnerError(FAILURE_INVALID_INPUT, f"source not found: {source_path}")

        existing = self._existing_for_key(idempotency_key)
        if existing is not None and existing.is_dir():
            return existing

        # input validation + digest before any work
        try:
            source_sha256 = sha256_file(source_path)
        except OSError as exc:  # pragma: no cover
            raise CaseRunnerError(FAILURE_HASH_FAILED, f"hash failed: {exc}") from exc

        profile = get_profile(scan_profile_id)
        # temp dir: atomic promotion only on success
        tmp_root = self.output_root / "cases" / ".tmp"
        tmp_dir = tmp_root / f"{idempotency_key}"
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir)
        tmp_dir.mkdir(parents=True, exist_ok=True)

        try:
            case_dir = run_production_case(
                source_path,
                tmp_dir,
                scan_profile_id=scan_profile_id,
            )
        except Exception as exc:
            shutil.rmtree(tmp_dir, ignore_errors=True)
            raise CaseRunnerError(FAILURE_EXECUTION_FAILED, f"execution failed: {exc}") from exc

        # configuration snapshot next to the case (immutable record)
        config = {
            "idempotency_key": idempotency_key,
            "source_sha256": source_sha256,
            "scan_profile_id": profile.profile_id,
            "scan_profile_hash": profile.hash(),
            "runner_contract": "MFY-EAR-DETERMINISTIC-CASE-RUNNER-001",
            "created_at": utc_now_iso(),
        }
        (case_dir / CONFIG_FILE).write_text(
            json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        final_dir = self.output_root / "cases" / case_dir.name
        if final_dir.exists():
            shutil.rmtree(final_dir)
        case_dir.rename(final_dir)
        self._record_key(idempotency_key, final_dir)
        return final_dir
