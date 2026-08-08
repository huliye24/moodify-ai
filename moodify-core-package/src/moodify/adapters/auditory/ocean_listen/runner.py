from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from time import monotonic
from typing import Any
import json
import os
import subprocess
import uuid

from .config import OceanRunOptions
from .errors import OceanExecutionError
from .mapper import map_report_file
from .models import OceanExecution
from .provenance import (
    canonical_json_hash,
    capture_module_manifest,
    git_head,
    sha256_file,
)
from .quality_gate import evaluate_report


class OceanRunner:
    def __init__(self, options: OceanRunOptions):
        options.validate()
        self.options = options

    def _validate_upstream(self) -> str | None:
        root = self.options.ocean_root
        if not (root / "ocean.py").is_file():
            raise FileNotFoundError(f"Ocean entrypoint missing: {root / 'ocean.py'}")
        if not (root / "LICENSE").is_file():
            raise FileNotFoundError(f"Ocean LICENSE missing: {root / 'LICENSE'}")
        if not (root / "NOTICES").is_file():
            raise FileNotFoundError(f"Ocean NOTICES missing: {root / 'NOTICES'}")

        commit = git_head(root)
        expected = self.options.expected_commit
        if expected and commit and commit != expected:
            raise OceanExecutionError(
                "Ocean Listen commit does not match the pinned reviewed commit. "
                f"expected={expected} actual={commit}. Review upstream changes "
                "before changing the pin."
            )
        return commit

    def _build_command(
        self,
        source_audio: Path,
        report_path: Path,
        cache_dir: Path,
    ) -> list[str]:
        opts = self.options
        command = [
            opts.python_executable,
            str((opts.ocean_root / "ocean.py").resolve()),
            str(source_audio.resolve()),
            "--mode",
            opts.mode,
            "--output",
            str(report_path.resolve()),
            "--cache-dir",
            str(cache_dir.resolve()),
        ]
        if opts.deep:
            command.append("--deep")
        if opts.lyric:
            command.extend(["--lyric", opts.lyric])
        if opts.lyric_value:
            command.extend(["--lyric-value", opts.lyric_value])
        if opts.language:
            command.extend(["--language", opts.language])
        if opts.whisper_model:
            command.extend(["--whisper-model", opts.whisper_model])
        if opts.force:
            command.append("--force")
        return command

    def run(self, source_audio: str | Path) -> dict[str, Any]:
        source = Path(source_audio)
        if not source.is_file():
            raise FileNotFoundError(f"Audio source not found: {source}")

        upstream_commit = self._validate_upstream()
        module_manifest = capture_module_manifest(self.options.ocean_root)

        config_record = {
            "deep": self.options.deep,
            "mode": self.options.mode,
            "lyric": self.options.lyric,
            "lyric_value": self.options.lyric_value,
            "language": self.options.language,
            "whisper_model": self.options.whisper_model,
            "force": self.options.force,
            "expected_commit": self.options.expected_commit,
        }
        seed = (
            f"{sha256_file(source)}:{canonical_json_hash(config_record)}:"
            f"{upstream_commit or 'unknown'}"
        )
        run_id = str(uuid.uuid5(uuid.NAMESPACE_URL, seed))
        run_dir = self.options.output_root / run_id

        raw_dir = run_dir / "raw"
        normalized_dir = run_dir / "normalized"
        quality_dir = run_dir / "quality"
        evidence_dir = run_dir / "evidence"
        logs_dir = run_dir / "logs"
        for directory in (
            raw_dir,
            normalized_dir,
            quality_dir,
            evidence_dir,
            logs_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)

        report_path = raw_dir / "ocean_report.json"
        cache_dir = (
            self.options.cache_root / run_id
            if self.options.cache_root is not None
            else run_dir / "cache"
        )
        cache_dir.mkdir(parents=True, exist_ok=True)

        stdout_path = logs_dir / "stdout.log"
        stderr_path = logs_dir / "stderr.log"
        command = self._build_command(source, report_path, cache_dir)

        environment = os.environ.copy()
        environment.update(
            {
                "PYTHONHASHSEED": "0",
                "TOKENIZERS_PARALLELISM": "false",
                "CUBLAS_WORKSPACE_CONFIG": ":4096:8",
            }
        )
        environment.update(self.options.extra_env)

        started = monotonic()
        try:
            result = subprocess.run(
                command,
                cwd=str(self.options.ocean_root),
                env=environment,
                capture_output=True,
                text=True,
                timeout=self.options.timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            stdout_path.write_text(exc.stdout or "", encoding="utf-8")
            stderr_path.write_text(exc.stderr or "", encoding="utf-8")
            raise OceanExecutionError(
                f"Ocean Listen timed out after {self.options.timeout_seconds}s"
            ) from exc

        elapsed = monotonic() - started
        stdout_path.write_text(result.stdout or "", encoding="utf-8")
        stderr_path.write_text(result.stderr or "", encoding="utf-8")

        execution = OceanExecution(
            run_id=run_id,
            run_dir=str(run_dir.resolve()),
            report_path=str(report_path.resolve()),
            stdout_path=str(stdout_path.resolve()),
            stderr_path=str(stderr_path.resolve()),
            command=command,
            return_code=result.returncode,
            elapsed_seconds=round(elapsed, 3),
            upstream_commit=upstream_commit,
        )

        if result.returncode != 0:
            failure_manifest = {
                "status": "OCEAN_EXECUTION_FAILED",
                "execution": asdict(execution),
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            (evidence_dir / "run_manifest.json").write_text(
                json.dumps(failure_manifest, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            raise OceanExecutionError(
                f"Ocean Listen failed with exit code {result.returncode}. "
                f"See {stderr_path}"
            )

        if not report_path.is_file():
            raise OceanExecutionError(
                f"Ocean Listen exited successfully but did not create {report_path}"
            )

        raw_report = json.loads(report_path.read_text(encoding="utf-8"))
        gate = evaluate_report(raw_report, deep_expected=self.options.deep)
        gate_path = quality_dir / "gate_result.json"
        gate_path.write_text(
            json.dumps(gate.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        normalized_path = (
            normalized_dir / "auditory_observation.v1.json"
        )
        mapped = map_report_file(
            report_path,
            source_audio=source,
            run_id=run_id,
            upstream_commit=upstream_commit,
            module_manifest=module_manifest,
            output_path=normalized_path,
            deep_expected=self.options.deep,
        )

        run_manifest = {
            "status": "COMPLETED_WITH_SENSOR_EVIDENCE",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "execution": asdict(execution),
            "source": {
                "path": str(source.resolve()),
                "sha256": sha256_file(source),
                "size_bytes": source.stat().st_size,
            },
            "config": config_record,
            "config_sha256": canonical_json_hash(config_record),
            "upstream": module_manifest,
            "artifacts": {
                "raw_report": {
                    "path": str(report_path.resolve()),
                    "sha256": sha256_file(report_path),
                },
                "normalized_observation": {
                    "path": str(normalized_path.resolve()),
                    "sha256": sha256_file(normalized_path),
                },
                "quality_gate": {
                    "path": str(gate_path.resolve()),
                    "sha256": sha256_file(gate_path),
                },
            },
            "authority": {
                "sensor_output_only": True,
                "may_approve_artistic_decision": False,
                "may_transition_to_technically_validated": False,
            },
        }
        manifest_path = evidence_dir / "run_manifest.json"
        manifest_path.write_text(
            json.dumps(run_manifest, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        return {
            "execution": asdict(execution),
            "quality_gate": gate.to_dict(),
            "observation": mapped,
            "manifest_path": str(manifest_path.resolve()),
        }
