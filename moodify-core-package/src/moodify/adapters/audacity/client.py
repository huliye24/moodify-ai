"""mod-script-pipe client for Audacity (DSK-MFY-AUDACITY-MACRO-RUNTIME-001).

Controls Audacity exclusively through the named-pipe scripting interface.
Ordinary CLI startup flags are never used to execute macros.
"""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path
from typing import TextIO

from moodify.adapters.audacity.errors import (
    AudacityCommandFailed,
    AudacityNotRunning,
    AudacityOutputMissing,
    AudacityPipeUnavailable,
)
from moodify.adapters.audacity.models import AudacityCommandInfo

TO_AUDACITY_PIPE = r"\\.\pipe\ToSrvPipe"
FROM_AUDACITY_PIPE = r"\\.\pipe\FromSrvPipe"
COMMAND_END = "\r\n\0"

DEFAULT_AUDACITY_PATHS = [
    Path(r"C:\Program Files\Audacity\Audacity.exe"),
    Path(r"C:\Program Files\Audacity 3\Audacity.exe"),
]


def detect_audacity_process() -> bool:
    """True if an Audacity process is running."""
    try:
        out = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq Audacity.exe"],
            capture_output=True, text=True, timeout=15,
        ).stdout
        return "Audacity.exe" in out
    except Exception:
        return False


def start_audacity() -> None:
    """Launch Audacity (Windows)."""
    exe = next((p for p in DEFAULT_AUDACITY_PATHS if p.exists()), None)
    if exe is None:
        raise AudacityNotRunning("Audacity.exe not found in default install paths")
    subprocess.Popen([str(exe)])


def wait_for_named_pipes(timeout_s: float = 30.0) -> bool:
    """Block until both scripting pipes are openable or timeout."""
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        if _pipe_available(TO_AUDACITY_PIPE) and _pipe_available(FROM_AUDACITY_PIPE):
            return True
        time.sleep(1.0)
    return False


def _pipe_available(pipe: str) -> bool:
    """Probe a pipe WITHOUT establishing a connection.

    WaitNamedPipeW only waits for server availability; opening the pipe
    for a probe creates a phantom client session that can desync the
    Audacity pipe server.
    """
    try:
        import ctypes
        return bool(ctypes.windll.kernel32.WaitNamedPipeW(pipe, 0))
    except Exception:
        return False


class AudacityClient:
    """One serial connection to the Audacity scripting pipes.

    A client is single-project and serial: no parallel command streams.
    """

    def __init__(self) -> None:
        self._writer: TextIO | None = None
        self._reader: TextIO | None = None

    # -- lifecycle ---------------------------------------------------------

    def connect(self) -> None:
        try:
            # binary mode like the official pipeclient: text mode buffers
            # and desyncs the response stream
            self._writer = open(TO_AUDACITY_PIPE, mode="wb")
            self._reader = open(FROM_AUDACITY_PIPE, mode="rb")
        except OSError as exc:
            raise AudacityPipeUnavailable(
                "无法连接 Audacity 脚本管道。确认：Audacity 已启动、"
                "mod-script-pipe 已启用并重启。"
            ) from exc

    def disconnect(self) -> None:
        if self._writer is not None:
            self._writer.close()
            self._writer = None
        if self._reader is not None:
            self._reader.close()
            self._reader = None

    def __enter__(self) -> "AudacityClient":
        self.connect()
        return self

    def __exit__(self, *exc) -> None:
        self.disconnect()

    # -- commands ----------------------------------------------------------

    def send_command(self, command: str) -> str:
        if self._writer is None or self._reader is None:
            raise AudacityPipeUnavailable("client not connected")
        self._writer.write((command + COMMAND_END).encode("utf-8"))
        self._writer.flush()
        lines: list[str] = []
        while True:
            raw = self._reader.readline()
            if raw == b"":
                raise AudacityPipeUnavailable("Audacity 管道已断开")
            line = raw.decode("utf-8", errors="replace")
            if line == "\n":
                break
            lines.append(line)
        response = "".join(lines).strip()
        if "BatchCommand finished: Failed!" in response:
            raise AudacityCommandFailed(command, response)
        return response

    def get_version(self) -> str:
        """Best-effort version string; may be empty if the instance reports none."""
        try:
            return self.send_command("GetInfo: Type=Version Format=JSON").strip()
        except AudacityCommandFailed:
            return "unknown"

    def get_available_commands(self, retries: int = 6) -> list[AudacityCommandInfo]:
        """GetInfo Type=Commands -> scripting-id inventory (JSON).

        Audacity 3.x desyncs large pipe responses (they arrive on a later
        command), so retry until a parseable JSON array is observed.
        """
        raw = ""
        payload = None
        for _ in range(retries):
            raw = self.send_command("GetInfo: Type=Commands")
            try:
                payload = json.loads(raw)
                if isinstance(payload, list):
                    break
            except json.JSONDecodeError:
                payload = None
            time.sleep(1.0)
        if payload is None:
            raise AudacityCommandFailed("GetInfo", raw)
        items = payload if isinstance(payload, list) else payload.get("commands", [])
        result: list[AudacityCommandInfo] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            sid = str(item.get("id", ""))
            result.append(
                AudacityCommandInfo(
                    scripting_id=sid,
                    display_name=str(item.get("name", "")),
                    help_url=str(item.get("url", "")),
                )
            )
        return result

    # -- script commands ----------------------------------------------------

    def import_audio(self, path: Path) -> str:
        return self.send_command(f'Import2: Filename="{path.resolve().as_posix()}"')

    def select_all(self) -> str:
        return self.send_command("SelectAll:")

    def execute_macro(self, scripting_id: str) -> str:
        return self.send_command(f"{scripting_id}:")

    def export_audio(self, path: Path, channels: int = 2) -> str:
        return self.send_command(
            f'Export2: Filename="{path.resolve().as_posix()}" NumChannels={channels}'
        )

    def close_current_project_safely(self) -> str:
        """Close the project without saving (script pipe command, not key simulation)."""
        return self.send_command("Close:")

    @staticmethod
    def verify_output_exists(path: Path) -> None:
        if not path.is_file() or path.stat().st_size == 0:
            raise AudacityOutputMissing(f"输出文件缺失或为空：{path}")
