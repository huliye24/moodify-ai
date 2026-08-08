"""Audacity macro execution runtime (DSK-MFY-AUDACITY-MACRO-RUNTIME-001).

Orchestrates one serial execution:
    Import2 -> SelectAll -> Macro_<id> -> Export2
and produces a full evidence bundle. Moodify owns analysis, decision,
approval and verification; Audacity owns the sound craft via macros.
"""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import asdict
from pathlib import Path

from moodify.adapters.audacity.client import (
    AudacityClient,
    detect_audacity_process,
    start_audacity,
    wait_for_named_pipes,
)
from moodify.adapters.audacity.errors import (
    AudacityMacroNameInvalid,
    AudacityNotRunning,
)
from moodify.adapters.audacity.macro_registry import MacroRegistry
from moodify.adapters.audacity.models import ExecutionRecord, MacroRegistration

EXECUTION_COMPLETED = "AUDACITY_MACRO_EXECUTION_COMPLETED"
STATUS_COMPLETED = "COMPLETED"
STATUS_FAILED = "FAILED"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


class AudacityMacroRuntime:
    """Single-instance, serial macro executor."""

    def __init__(
        self,
        macro_dir: Path | None = None,
        autostart: bool = True,
        pipe_timeout_s: float = 30.0,
    ) -> None:
        self.macro_dir = macro_dir
        self.autostart = autostart
        self.pipe_timeout_s = pipe_timeout_s
        self._client: AudacityClient | None = None

    # -- lifecycle -----------------------------------------------------------

    def _ensure_running(self) -> None:
        if not detect_audacity_process():
            if not self.autostart:
                raise AudacityNotRunning("Audacity 未运行且 autostart=False")
            start_audacity()
            if not wait_for_named_pipes(self.pipe_timeout_s):
                raise AudacityNotRunning("Audacity 启动但管道未就绪（mod-script-pipe 未启用？）")

    def _client_connected(self) -> AudacityClient:
        if self._client is None:
            self._ensure_running()
            if not wait_for_named_pipes(self.pipe_timeout_s):
                raise AudacityNotRunning("Audacity 管道未就绪")
            client = AudacityClient()
            client.connect()
            self._client = client
        return self._client

    def close(self) -> None:
        if self._client is not None:
            self._client.disconnect()
            self._client = None

    def __enter__(self) -> "AudacityMacroRuntime":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    # -- registry ------------------------------------------------------------

    def registry(self) -> MacroRegistry:
        client = self._client_connected()
        return MacroRegistry.from_commands(client.get_available_commands())

    def list_available_macros(self) -> list[MacroRegistration]:
        return self.registry().list()

    # -- execution -----------------------------------------------------------

    def run_macro(
        self,
        input_path: Path,
        macro_name: str,
        output_path: Path,
        case_id: str | None = None,
    ) -> ExecutionRecord:
        input_path = input_path.resolve()
        output_path = output_path.resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if not MacroRegistration.is_valid_name(macro_name):
            raise AudacityMacroNameInvalid(
                f"宏名必须匹配 MFY_<PROCESS>_<VARIANT>_V<NNN>：{macro_name}"
            )
        if not input_path.is_file():
            raise FileNotFoundError(f"输入文件不存在：{input_path}")

        # macro file for evidence (Moodify-managed copy; not required for execution)
        macro_file_path = Path("")
        macro_sha = ""
        if self.macro_dir is not None:
            candidate = self.macro_dir / f"{macro_name}.txt"
            if candidate.is_file():
                macro_file_path = candidate
                macro_sha = sha256_file(candidate)

        record = ExecutionRecord(
            case_id=case_id or f"amr-{uuid.uuid4().hex[:12]}",
            source_path=str(input_path),
            source_sha256=sha256_file(input_path),
            macro_display_name=macro_name,
            macro_scripting_id="",
            macro_file_path=str(macro_file_path),
            macro_sha256=macro_sha,
            audacity_version="",
        )

        client = self._client_connected()
        started = time.perf_counter()
        try:
            # resolve macro BEFORE touching the project (fail fast)
            reg = self.registry().resolve(macro_name)
            record.macro_scripting_id = reg.scripting_id

            record.audacity_version = client.get_version()
            record.raw_command_log.append(f'Import2: Filename="{input_path.as_posix()}"')
            record.raw_audacity_response.append(client.import_audio(input_path))

            record.raw_command_log.append("SelectAll:")
            record.raw_audacity_response.append(client.select_all())

            record.raw_command_log.append(f"{reg.scripting_id}:")
            record.raw_audacity_response.append(client.execute_macro(reg.scripting_id))

            record.raw_command_log.append(f'Export2: Filename="{output_path.as_posix()}" NumChannels=2')
            record.raw_audacity_response.append(client.export_audio(output_path))

            AudacityClient.verify_output_exists(output_path)
            record.output_path = str(output_path)
            record.output_sha256 = sha256_file(output_path)
            record.finish(STATUS_COMPLETED)
            return record
        except Exception as exc:
            record.finish(STATUS_FAILED)
            record.raw_audacity_response.append(f"ERROR: {exc}")
            raise
        finally:
            try:
                client.close_current_project_safely()
            except Exception:
                pass
            _ = started

    # -- evidence ------------------------------------------------------------

    def write_evidence(self, record: ExecutionRecord, bundle_dir: Path) -> Path:
        bundle_dir.mkdir(parents=True, exist_ok=True)
        manifest = {
            "execution": EXECUTION_COMPLETED if record.execution_status == STATUS_COMPLETED else "FAILED",
            "record": asdict(record),
            "elapsed_s": None,
        }
        path = bundle_dir / f"{record.case_id}_evidence.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
        return path
