"""BasicPitch adapter — audio.separate_manifest via the 008 internal capability.

Basic Pitch is Moodify's own internal capability (Apache-2.0, from
DSK-MFY-STEM-MIDI-008). Unlike external-process adapters, this adapter
imports the 008 interface directly — it is the one sanctioned internal
integration. Accuracy claims remain prohibited (no ground truth).
"""

from __future__ import annotations

import tempfile
import time
from pathlib import Path

from moodify.capability_registry.adapters.base import AdapterResult, InvokeRequest

KNOWN_FAILURE_MODES = (
    "Demucs separation not installed (stem separation unavailable)",
    "No real-song ground truth; accuracy claims prohibited until benchmark",
    "Drums UNSUPPORTED for pitch transcription",
)

VENV_PYTHON = Path(r"E:\moodify\.venv-basic-pitch\Scripts\python.exe")


class BasicPitchAdapter:
    capability_id = "audio.separate_manifest"
    provider_id = "basic_pitch.moodify"
    license_label = "Apache-2.0 (internal)"

    def __init__(self, timeout_s: float = 600.0) -> None:
        self._timeout_s = timeout_s
        self._version: str | None = None

    def detect(self) -> bool:
        return VENV_PYTHON.is_file()

    def version(self) -> str | None:
        if self._version is None:
            if not self.detect():
                return None
            import subprocess

            try:
                proc = subprocess.run(
                    [str(VENV_PYTHON), "-c",
                     "import importlib.metadata as m; print(m.version('basic-pitch'))"],
                    capture_output=True, timeout=30, check=False,
                )
                out = (proc.stdout or b"").decode("utf-8", errors="replace").strip()
                self._version = out.splitlines()[-1] if out else None
            except (OSError, subprocess.TimeoutExpired):
                self._version = None
        return self._version

    def invoke(self, request: InvokeRequest) -> AdapterResult:
        if not self.detect():
            return AdapterResult(
                status="unavailable",
                errors=(f"{self.provider_id} venv not found: {VENV_PYTHON}",),
                error_class="environment_failure",
            )
        out_dir = request.output_path()
        if out_dir.exists() and any(out_dir.iterdir()):
            return AdapterResult(
                status="failure", errors=(f"output directory not empty: {out_dir}",),
                error_class="invalid_input",
            )
        out_dir.mkdir(parents=True, exist_ok=True)
        if "source" not in request.inputs:
            return AdapterResult(
                status="failure", errors=("audio.separate_manifest requires input role 'source'",),
                error_class="invalid_input",
            )
        source = Path(request.inputs["source"])
        if not source.exists():
            return AdapterResult(
                status="failure", errors=(f"input missing: {source}",),
                error_class="invalid_input",
            )

        t0 = time.perf_counter()
        with tempfile.TemporaryDirectory(prefix="moodify_basicpitch_"):
            try:
                from moodify.transcription_pipeline.runner import transcribe_stems
                from moodify.transcription_pipeline.stems import StemEntry, StemManifest
                from moodify.transcription_pipeline.profiles import StemKind
            except ImportError as exc:
                return AdapterResult(
                    status="failure", errors=(f"008 transcription unavailable: {exc}",),
                    error_class="environment_failure",
                )
            try:
                manifest = StemManifest(stems=(StemEntry(kind=StemKind.OTHER, path=source),))
                manifest.validate()
                result = transcribe_stems(manifest, out_dir)
            except Exception as exc:  # 008 raises ValueError/OSError on failure
                return AdapterResult(
                    status="failure", errors=(f"transcription failed: {exc}",),
                    error_class="provider_defect",
                )
            elapsed = time.perf_counter() - t0
            artifacts = [str(p) for p in out_dir.iterdir() if p.is_file() and p.stat().st_size > 0]
            status = "success" if result.status in ("success", "partial_success") else "failure"
            return AdapterResult(
                status=status,
                artifacts=tuple(artifacts),
                errors=() if status == "success" else (result.status,),
                error_class=None if status == "success" else "partial_output",
                elapsed_s=elapsed,
                evidence={
                    "provider_id": self.provider_id,
                    "capability_id": self.capability_id,
                    "provider_version": self.version(),
                    "manifest_status": result.status,
                    "output_hashes": {},
                },
            )
