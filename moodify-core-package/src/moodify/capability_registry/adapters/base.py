"""Provider adapter protocol, result types and controlled execution base.

Adapters translate capability contracts into provider-specific argv-array
invocations. Provider knowledge stays inside adapters; workflow logic above
must depend only on capability contracts (Law 5). Errors are classified into
a shared taxonomy so failure knowledge is comparable across providers.
"""

from __future__ import annotations

import hashlib
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Protocol

AdapterStatus = Literal["success", "failure", "unavailable"]
ErrorClass = Literal[
    "invalid_input", "provider_defect", "environment_failure",
    "timeout", "partial_output", "policy_rejection",
]

DEFAULT_TIMEOUT_S = 120.0


@dataclass(frozen=True)
class AdapterResult:
    status: AdapterStatus
    artifacts: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()
    error_class: ErrorClass | None = None
    exit_code: int | None = None
    elapsed_s: float = 0.0
    evidence: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "artifacts": list(self.artifacts),
            "errors": list(self.errors),
            "error_class": self.error_class,
            "exit_code": self.exit_code,
            "elapsed_s": round(self.elapsed_s, 3),
            "evidence": self.evidence,
        }


@dataclass(frozen=True)
class InvokeRequest:
    capability_id: str
    inputs: dict[str, str]  # role -> absolute path
    parameters: dict = field(default_factory=dict)
    output_dir: str = ""
    timeout_s: float = DEFAULT_TIMEOUT_S
    allow_network: bool = False

    def output_path(self) -> Path:
        return Path(self.output_dir)


class ProviderAdapter(Protocol):
    capability_id: str
    provider_id: str

    def detect(self) -> bool: ...
    def version(self) -> str | None: ...
    def invoke(self, request: InvokeRequest) -> AdapterResult: ...


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _classify(proc: subprocess.CompletedProcess | None, timed_out: bool, out_dir: Path) -> tuple[ErrorClass, tuple[str, ...]]:
    if timed_out:
        return "timeout", ("provider timed out",)
    if proc is None:
        return "environment_failure", ("no process result",)
    if proc.returncode != 0:
        stderr = (proc.stderr or b"").decode("utf-8", errors="replace").strip()
        return "provider_defect", (stderr or f"exit code {proc.returncode}",)
    if not any(out_dir.iterdir()):
        return "partial_output", ("provider produced no output files",)
    return "policy_rejection", ("output rejected by policy",)


class ControlledProcessAdapter:
    """Base for argv-array external-process adapters.

    Guarantees: argument list (no shell concatenation), timeout, stdout/stderr
    capture, version + command + hashes in evidence, fresh output directory,
    path traversal rejection.
    """

    capability_id: str = ""
    provider_id: str = ""
    license_label: str = ""

    def __init__(self, timeout_s: float = DEFAULT_TIMEOUT_S) -> None:
        self._timeout_s = timeout_s
        self._binary: str | None = None
        self._version: str | None = None

    # detection hooks (override per adapter)
    def _candidate_paths(self) -> tuple[str, ...]:
        return ()

    def _which_names(self) -> tuple[str, ...]:
        return ()

    def _version_args(self) -> tuple[str, ...]:
        return ("--version",)

    def _detect_binary(self) -> None:
        for candidate in self._candidate_paths():
            if candidate and Path(candidate).is_file():
                self._binary = candidate
                return
        for name in self._which_names():
            found = shutil.which(name)
            if found:
                self._binary = found
                return

    def detect(self) -> bool:
        if self._binary is None:
            self._detect_binary()
        return self._binary is not None

    def version(self) -> str | None:
        if self._binary is None:
            self._detect_binary()
        if self._binary is None:
            return None
        if self._version is None:
            try:
                proc = subprocess.run(
                    [self._binary, *self._version_args()],
                    capture_output=True, timeout=10, check=False,
                )
                # some tools print version to stderr (ffmpeg, rubberband)
                out = (proc.stdout or b"").decode("utf-8", errors="replace").strip()
                err = (proc.stderr or b"").decode("utf-8", errors="replace").strip()
                text = out or err
                self._version = text.splitlines()[0] if text else None
            except (OSError, subprocess.TimeoutExpired):
                self._version = None
        return self._version

    # command construction hook (override per adapter)
    def build_command(self, request: InvokeRequest, work_dir: Path, out_dir: Path) -> list[str]:
        raise NotImplementedError

    # optional: capture stdout to a file in out_dir (e.g. ffprobe JSON)
    def stdout_target(self, request: InvokeRequest, out_dir: Path) -> Path | None:
        return None

    def _prepare_output_dir(self, request: InvokeRequest) -> Path:
        out_dir = request.output_path()
        if out_dir.exists() and any(out_dir.iterdir()):
            raise ValueError(f"output directory not empty: {out_dir}")
        out_dir.mkdir(parents=True, exist_ok=True)
        return out_dir

    def _verify_inputs(self, request: InvokeRequest) -> None:
        for role, path_str in request.inputs.items():
            path = Path(path_str)
            if not path.exists():
                raise ValueError(f"input missing for role {role!r}: {path_str}")
            # path traversal guard: inputs must be absolute
            if not path.is_absolute():
                raise ValueError(f"input path must be absolute: {path_str}")

    def invoke(self, request: InvokeRequest) -> AdapterResult:
        if not self.detect():
            return AdapterResult(
                status="unavailable",
                errors=(f"{self.provider_id} not detected",),
                error_class="environment_failure",
            )
        try:
            self._verify_inputs(request)
            out_dir = self._prepare_output_dir(request)
        except ValueError as exc:
            return AdapterResult(
                status="failure", errors=(str(exc),),
                error_class="invalid_input",
            )

        work_dir = Path(tempfile.mkdtemp(prefix=f"moodify_{self.provider_id}_"))
        try:
            try:
                command = self.build_command(request, work_dir, out_dir)
            except (ValueError, OSError) as exc:
                return AdapterResult(
                    status="failure", errors=(str(exc),),
                    error_class="invalid_input",
                )
            t0 = time.perf_counter()
            stdout_target = self.stdout_target(request, out_dir)
            try:
                if stdout_target is not None:
                    with stdout_target.open("wb") as fh:
                        proc = subprocess.run(
                            command, stdout=fh, stderr=subprocess.STDOUT,
                            timeout=request.timeout_s, check=False,
                        )
                else:
                    proc = subprocess.run(
                        command, capture_output=True, timeout=request.timeout_s, check=False,
                    )
                timed_out = False
            except subprocess.TimeoutExpired:
                proc = None
                timed_out = True
            elapsed = time.perf_counter() - t0

            artifacts = [str(p) for p in out_dir.iterdir() if p.is_file() and p.stat().st_size > 0]
            evidence = {
                "provider_id": self.provider_id,
                "capability_id": self.capability_id,
                "command": list(command),
                "provider_version": self.version(),
                "exit_code": proc.returncode if proc is not None else -1,
                "timed_out": timed_out,
                "elapsed_s": round(elapsed, 3),
                "stdout": (proc.stdout or b"").decode("utf-8", errors="replace")[:2000] if proc else "",
                "stderr": (proc.stderr or b"").decode("utf-8", errors="replace")[:2000] if proc else "",
                "input_hashes": {role: _sha256(Path(path_str)) for role, path_str in request.inputs.items()},
                "output_hashes": {str(p): _sha256(p) for p in (Path(a) for a in artifacts)},
            }

            if timed_out:
                return AdapterResult(
                    status="failure", artifacts=tuple(artifacts), errors=("provider timed out",),
                    error_class="timeout", exit_code=-1, elapsed_s=elapsed, evidence=evidence,
                )
            if proc is None or proc.returncode != 0:
                err_class, err_msgs = _classify(proc, False, out_dir)
                return AdapterResult(
                    status="failure", artifacts=tuple(artifacts), errors=err_msgs,
                    error_class=err_class, exit_code=proc.returncode if proc else None,
                    elapsed_s=elapsed, evidence=evidence,
                )
            if not artifacts:
                return AdapterResult(
                    status="failure", artifacts=(), errors=("provider produced no output files",),
                    error_class="partial_output", exit_code=0, elapsed_s=elapsed, evidence=evidence,
                )
            return AdapterResult(
                status="success", artifacts=tuple(artifacts),
                exit_code=proc.returncode, elapsed_s=elapsed, evidence=evidence,
            )
        finally:
            shutil.rmtree(work_dir, ignore_errors=True)
