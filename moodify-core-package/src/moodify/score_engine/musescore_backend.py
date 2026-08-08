"""MuseScoreBackend — external-process rendering of MoodifyScore.

MuseScore is treated strictly as an independent GPLv3 program. We never copy
or modify its source, site-packages, sounds or fonts; we only pass MIDI/
MusicXML in and receive PDF/SVG out through an argv-array subprocess call.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

from moodify.score_engine.backend import BackendCapabilities, BackendInfo, ExportResult, ValidationResult
from moodify.score_engine.model import MoodifyScore
from moodify.score_engine.musicxml_exporter import export_musicxml

DEFAULT_TIMEOUT_S = 120.0
ENV_VAR = "MUSESCORE_BIN"
DEFAULT_CANDIDATES = (
    r"C:\Program Files\MuseScore 4\bin\MuseScore4.exe",
    r"C:\Program Files (x86)\MuseScore 4\bin\MuseScore4.exe",
    "/usr/bin/musescore",
    "/usr/bin/musescore3",
    "/usr/local/bin/musescore",
    "/usr/bin/mscore",
)


@dataclass(frozen=True)
class ProcessEvidence:
    command: tuple[str, ...]
    exit_code: int
    timed_out: bool
    elapsed_s: float
    stdout: str
    stderr: str
    output_files: tuple[str, ...]
    hashes: dict

    def to_dict(self) -> dict:
        return {
            "command": list(self.command),
            "exit_code": self.exit_code,
            "timed_out": self.timed_out,
            "elapsed_s": round(self.elapsed_s, 3),
            "stdout": self.stdout[:2000],
            "stderr": self.stderr[:2000],
            "output_files": list(self.output_files),
            "hashes": self.hashes,
        }


class MuseScoreProbeError(RuntimeError):
    pass


class MuseScoreBackend:
    backend_id = "musescore"
    display_name = "MuseScore"
    license_label = "GPLv3 (external process)"
    capabilities = BackendCapabilities(
        musicxml_import=True, pdf_export=True, svg_export=True, png_export=True,
    )

    def __init__(self, binary: str | None = None, timeout_s: float = DEFAULT_TIMEOUT_S) -> None:
        self._binary: str | None = None
        self._version: str | None = None
        self._timeout_s = timeout_s
        self._detect(binary)

    # ── detection ────────────────────────────────────────────────────────
    def _detect(self, explicit: str | None) -> None:
        candidates: list[str] = []
        if explicit:
            candidates.append(explicit)
        env = os.environ.get(ENV_VAR)
        if env:
            candidates.append(env)
        candidates.extend(DEFAULT_CANDIDATES)
        for cand in candidates:
            if cand and Path(cand).is_file():
                self._binary = cand
                self._version = self._probe_version(cand)
                return
        found = shutil.which("musescore4") or shutil.which("musescore") or shutil.which("mscore")
        if found:
            self._binary = found
            self._version = self._probe_version(found)

    def _probe_version(self, binary: str) -> str | None:
        try:
            proc = subprocess.run(
                [binary, "--version"],
                capture_output=True, timeout=10, check=False,
            )
            out = (proc.stdout or b"").decode("utf-8", errors="replace").strip()
            if proc.returncode == 0 and out:
                return out
            err = (proc.stderr or b"").decode("utf-8", errors="replace").strip()
            return err if err else None
        except (OSError, subprocess.TimeoutExpired):
            return None

    def available(self) -> bool:
        return self._binary is not None

    def version(self) -> str | None:
        return self._version

    def validate(self, score: MoodifyScore) -> ValidationResult:
        issues: list[str] = []
        if not score.parts:
            issues.append("score has no parts")
        for part in score.parts:
            for staff in part.staves:
                for voice in staff.voices:
                    for ev in voice.events:
                        if ev.event_type == "note" and ev.pitch_midi is None:
                            issues.append(f"note without pitch: {ev.event_id}")
        return ValidationResult(valid=not issues, issues=tuple(issues))

    # ── export ───────────────────────────────────────────────────────────
    def export(self, score: MoodifyScore, out_dir: Path) -> ExportResult:
        if not self.available():
            return ExportResult(
                status="unavailable",
                errors=(f"{ENV_VAR} not set and no MuseScore binary found",),
            )
        if out_dir.exists() and any(out_dir.iterdir()):
            return ExportResult(
                status="failure",
                errors=(f"output directory not empty: {out_dir}",),
            )
        out_dir.mkdir(parents=True, exist_ok=True)

        work_dir = Path(tempfile.mkdtemp(prefix="moodify_score_"))
        try:
            score_xml = out_dir / f"{score.score_id or 'score'}.musicxml"
            export_musicxml(score, score_xml)

            pdf_out = out_dir / f"{score.score_id or 'score'}.pdf"
            svg_out = out_dir / f"{score.score_id or 'score'}.svg"
            commands = [
                [self._binary or "", "-o", str(pdf_out), str(score_xml)],
                [self._binary or "", "-o", str(svg_out), str(score_xml)],
            ]
            evidences: list[dict] = []
            artifacts: list[str] = []
            for command in commands:
                t0 = time.perf_counter()
                try:
                    proc = subprocess.run(
                        command, capture_output=True, timeout=self._timeout_s, check=False,
                    )
                    timed_out = False
                except subprocess.TimeoutExpired:
                    proc = None
                    timed_out = True
                elapsed = time.perf_counter() - t0
                target = Path(command[2])
                # MuseScore may append a page suffix to multi-page SVG (e.g. x-1.svg)
                produced = [str(target)] if target.exists() and target.stat().st_size > 0 else []
                if not produced:
                    produced = [str(p) for p in out_dir.glob(target.stem + "-*.svg") if p.stat().st_size > 0]
                evidences.append(
                    ProcessEvidence(
                        command=tuple(command),
                        exit_code=proc.returncode if proc is not None else -1,
                        timed_out=timed_out,
                        elapsed_s=elapsed,
                        stdout=(proc.stdout or b"").decode("utf-8", errors="replace") if proc else "",
                        stderr=(proc.stderr or b"").decode("utf-8", errors="replace") if proc else "",
                        output_files=tuple(produced),
                        hashes={str(p): hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in produced},
                    ).to_dict()
                )
                artifacts.extend(produced)
                if timed_out:
                    break
                if proc is None or proc.returncode != 0:
                    break

            if timed_out:
                return ExportResult(status="failure", artifacts=tuple(artifacts), errors=("MuseScore timed out",), evidence=evidences)
            if proc is None or proc.returncode != 0:
                return ExportResult(status="failure", artifacts=tuple(artifacts), errors=("MuseScore exit code != 0",), evidence=evidences)
            if not artifacts:
                return ExportResult(status="failure", artifacts=(), errors=("MuseScore produced no output files",), evidence=evidences)
            return ExportResult(status="success", artifacts=tuple(artifacts), evidence=evidences)
        finally:
            shutil.rmtree(work_dir, ignore_errors=True)

    def inspect(self, artifact: Path) -> dict:
        """Reparse a MusicXML artifact and summarize comparable fields."""
        from xml.etree import ElementTree as ET

        root = ET.parse(artifact).getroot()
        parts = root.findall("part")
        measures = sum(len(p.findall("measure")) for p in parts)
        notes = root.findall(".//note")
        pitches = [(n.findtext("pitch/step"), n.findtext("pitch/octave")) for n in notes if n.find("pitch") is not None]
        durations = [n.findtext("duration") for n in notes]
        return {
            "parts": len(parts),
            "measures": measures,
            "notes": len(notes),
            "pitches": pitches,
            "durations": durations,
        }


def make_backend_info(binary: str | None = None) -> BackendInfo:
    backend = MuseScoreBackend(binary=binary)
    return BackendInfo(
        backend_id=backend.backend_id,
        display_name=backend.display_name,
        license_label=backend.license_label,
        capabilities=backend.capabilities,
        implemented=True,
        available=backend.available(),
        version=backend.version(),
        binary_path=backend._binary,
    )


def make_unimplemented_info(backend_id: str) -> BackendInfo:
    from moodify.score_engine.backend import _UNIMPLEMENTED

    caps = _UNIMPLEMENTED[backend_id]
    labels = {"verovio": "LGPL-3.0", "lilypond": "GPL-3.0", "osmd": "MIT"}
    return BackendInfo(
        backend_id=backend_id,
        display_name=backend_id.capitalize(),
        license_label=labels[backend_id],
        capabilities=caps,
        implemented=False,
    )


def list_backends(binary: str | None = None) -> list[BackendInfo]:
    infos = [make_backend_info(binary=binary)]
    infos.extend(make_unimplemented_info(bid) for bid in ("verovio", "lilypond", "osmd"))
    return infos
