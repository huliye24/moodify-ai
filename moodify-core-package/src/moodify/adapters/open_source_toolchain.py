"""Controlled adapters for the installed open-source audio toolchain."""
from __future__ import annotations

import importlib.metadata
import shutil
import subprocess
from pathlib import Path

from moodify.ports.processing import EngineProbe, ProcessingRequest, ProcessingResult


def _discover(name: str, candidates: tuple[Path, ...] = ()) -> str | None:
    found = shutil.which(name)
    if found:
        return found
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    return None


def _run(argv: list[str], timeout: int = 600) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(argv, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout, check=True)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"ENGINE_TIMEOUT: {argv[0]}") from exc
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "").strip()[-1000:]
        raise RuntimeError(f"ENGINE_FAILED: {argv[0]} exit={exc.returncode}: {detail}") from exc


class SoxAdapter:
    engine_id = "sox"

    def __init__(self) -> None:
        winget_root = Path.home() / "AppData/Local/Microsoft/WinGet/Packages"
        candidates = tuple(winget_root.glob("ChrisBagwell.SoX_*/sox-14.4.2/sox.exe"))
        self.executable = _discover("sox", candidates)

    def probe(self) -> EngineProbe:
        if not self.executable:
            return EngineProbe(self.engine_id, False, error="SOX_NOT_INSTALLED")
        result = _run([self.executable, "--version"], timeout=15)
        version = (result.stdout or result.stderr).strip().split()[-1]
        return EngineProbe(self.engine_id, True, version, self.executable, ("gain", "format_copy", "batch"))

    def execute(self, request: ProcessingRequest) -> ProcessingResult:
        probe = self.probe()
        if not probe.available:
            raise RuntimeError(probe.error)
        gain_db = float(request.params.get("gain_db", 0.0))
        argv = [self.executable, str(request.source), str(request.output)]
        if gain_db:
            argv += ["gain", f"{gain_db:.6f}"]
        _run(argv)
        if not request.output.is_file():
            raise RuntimeError("ENGINE_OUTPUT_MISSING: sox")
        return ProcessingResult(self.engine_id, request.output, tuple(argv), {"gain_db": gain_db})


class RubberBandAdapter:
    engine_id = "rubberband"

    def __init__(self) -> None:
        root = Path("E:/moodify/tools/third_party/rubberband-4.0.0")
        candidates = tuple(root.glob("**/rubberband.exe"))
        self.executable = _discover("rubberband", candidates)

    def probe(self) -> EngineProbe:
        if not self.executable:
            return EngineProbe(self.engine_id, False, error="RUBBERBAND_NOT_INSTALLED")
        result = _run([self.executable, "--version"], timeout=15)
        version = (result.stdout or result.stderr).strip().splitlines()[-1]
        return EngineProbe(self.engine_id, True, version, self.executable, ("time_stretch", "pitch_shift"))

    def execute(self, request: ProcessingRequest) -> ProcessingResult:
        if not self.executable:
            raise RuntimeError("RUBBERBAND_NOT_INSTALLED")
        ratio = float(request.params.get("time_ratio", 1.0))
        semitones = float(request.params.get("pitch_semitones", 0.0))
        if not 0.5 <= ratio <= 2.0 or not -12.0 <= semitones <= 12.0:
            raise ValueError("Rubber Band parameters outside Moodify safety bounds")
        argv = [self.executable, "-3", "-t", f"{ratio:.8f}", "-p", f"{semitones:.8f}", str(request.source), str(request.output)]
        _run(argv)
        if not request.output.is_file():
            raise RuntimeError("ENGINE_OUTPUT_MISSING: rubberband")
        return ProcessingResult(self.engine_id, request.output, tuple(argv), {"time_ratio": ratio, "pitch_semitones": semitones})


class MatcheringAdapter:
    engine_id = "matchering"

    def probe(self) -> EngineProbe:
        try:
            version = importlib.metadata.version("matchering")
        except importlib.metadata.PackageNotFoundError:
            return EngineProbe(self.engine_id, False, error="MATCHERING_NOT_INSTALLED")
        return EngineProbe(self.engine_id, True, version, "python:matchering", ("reference_mastering",))

    def execute(self, request: ProcessingRequest) -> ProcessingResult:
        if request.reference is None or not request.reference.is_file():
            raise ValueError("Matchering requires an existing reference audio file")
        try:
            import matchering as mg
        except ImportError as exc:
            raise RuntimeError("MATCHERING_NOT_INSTALLED") from exc
        mg.process(target=str(request.source), reference=str(request.reference), results=[mg.pcm24(str(request.output))])
        if not request.output.is_file():
            raise RuntimeError("ENGINE_OUTPUT_MISSING: matchering")
        return ProcessingResult(self.engine_id, request.output, ("python", "matchering.process"), {"reference": str(request.reference)})


def probe_toolchain() -> dict[str, EngineProbe]:
    return {adapter.engine_id: adapter.probe() for adapter in (SoxAdapter(), MatcheringAdapter(), RubberBandAdapter())}
