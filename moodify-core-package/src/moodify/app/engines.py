"""Controlled execution engines.

Engines receive an ApprovedExecutionEnvelope and return an ExecutionResult.
They never mutate case state, never approve plans, never select other
engines, and never write artistic approval records.
"""
from __future__ import annotations

import hashlib
import os
import shutil
import time
from pathlib import Path

import numpy as np
import soundfile as sf

from .production_control import ApprovedExecutionEnvelope, ExecutionResult


def _id() -> str:
    import uuid
    return f"MFY-EXEC-{hashlib.sha256(uuid.uuid4().bytes).hexdigest()[:12]}"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


class NativeExecutionEngine:
    """Deterministic pure-Python DSP engine (numpy + soundfile)."""

    name = "native"
    version = "1.0.0"
    sample_rate = 44100
    bit_depth = 24
    supported_actions = {"gain", "eq", "compressor", "limiter", "fade_in", "fade_out"}

    def execute(self, envelope: ApprovedExecutionEnvelope) -> ExecutionResult:
        execution_id = _id()
        started_at = _now()
        manifest: list[dict] = []
        warnings: list[str] = []
        errors: list[str] = []
        output_path = Path(envelope.output_path)
        staging_dir = output_path.parent / ".staging"

        for action in envelope.actions:
            if action.get("type") not in self.supported_actions:
                errors.append(f"unsupported action: {action.get('type')}")
        if errors:
            return ExecutionResult(
                execution_id=execution_id, success=False, engine_name=self.name,
                engine_version=self.version, started_at=started_at, completed_at=_now(),
                duration=0.0, command_or_action_manifest=[], output_path="",
                output_sha256="", warnings=warnings, errors=errors)

        source = Path(envelope.source_path)
        if not source.exists():
            return ExecutionResult(
                execution_id=execution_id, success=False, engine_name=self.name,
                engine_version=self.version, started_at=started_at, completed_at=_now(),
                duration=0.0, command_or_action_manifest=list(envelope.actions),
                output_path="", output_sha256="", warnings=warnings,
                errors=[f"source missing: {source}"])
        observed = _sha256(source)
        if observed != envelope.source_sha256:
            return ExecutionResult(
                execution_id=execution_id, success=False, engine_name=self.name,
                engine_version=self.version, started_at=started_at, completed_at=_now(),
                duration=0.0, command_or_action_manifest=list(envelope.actions),
                output_path="", output_sha256="", warnings=warnings,
                errors=["source hash mismatch: execution refused"])
        if output_path.resolve() == source.resolve():
            return ExecutionResult(
                execution_id=execution_id, success=False, engine_name=self.name,
                engine_version=self.version, started_at=started_at, completed_at=_now(),
                duration=0.0, command_or_action_manifest=list(envelope.actions),
                output_path="", output_sha256="", warnings=warnings,
                errors=["output would overwrite the registered source"])

        t_start = time.perf_counter()
        staging_dir.mkdir(parents=True, exist_ok=True)
        staged = staging_dir / "processed_audio.wav"
        try:
            y, sr = self._load(source)
            if sr != self.sample_rate:
                warnings.append(f"resampled {sr} -> {self.sample_rate}")
                y = self._resample(y, sr, self.sample_rate)
            for action in envelope.actions:
                manifest.append(dict(action))
                y = self._apply_action(y, self.sample_rate, action)
            sf.write(str(staged), y, self.sample_rate, subtype=f"PCM_{self.bit_depth}")
            sf.info(str(staged))
            if not output_path.parent.exists():
                output_path.parent.mkdir(parents=True, exist_ok=True)
            os.replace(str(staged), str(output_path))
            if staged.exists():
                raise RuntimeError("staging file not promoted")
        except Exception as exc:
            label = output_path.parent / f"failed_{output_path.stem}_{execution_id}.wav"
            if staged.exists():
                shutil.copy2(str(staged), str(label))
                (output_path.parent / f"failed_{output_path.stem}_{execution_id}.label.txt").write_text(
                    "FAILED_TEMPORARY_ARTIFACT — not final output; retained for diagnosis\n", encoding="utf-8")
            return ExecutionResult(
                execution_id=execution_id, success=False, engine_name=self.name,
                engine_version=self.version, started_at=started_at, completed_at=_now(),
                duration=round(time.perf_counter() - t_start, 3),
                command_or_action_manifest=manifest, output_path="",
                output_sha256="", warnings=warnings, errors=[str(exc)])

        source_unchanged = _sha256(source) == observed
        if not source_unchanged:
            errors.append("source changed during execution")
        return ExecutionResult(
            execution_id=execution_id, success=not errors, engine_name=self.name,
            engine_version=self.version, started_at=started_at, completed_at=_now(),
            duration=round(time.perf_counter() - t_start, 3),
            command_or_action_manifest=manifest,
            output_path=str(output_path) if not errors else "",
            output_sha256=_sha256(output_path) if not errors else "",
            warnings=warnings, errors=errors)

    # ---- DSP helpers ------------------------------------------------------

    def _load(self, path: Path) -> tuple[np.ndarray, int]:
        y, sr = sf.read(str(path), dtype="float64")
        if y.ndim == 1:
            y = np.column_stack([y, y])
        elif y.shape[1] == 1:
            y = np.column_stack([y[:, 0], y[:, 0]])
        return y, int(sr)

    def _resample(self, y: np.ndarray, src: int, dst: int) -> np.ndarray:
        from scipy.signal import resample
        new_len = int(len(y) * dst / src)
        return resample(y, new_len)

    def _apply_action(self, y: np.ndarray, sr: int, action: dict) -> np.ndarray:
        kind = action.get("type")
        params = action.get("params", {})
        if kind == "gain":
            db = float(params.get("gain_db", 0))
            return y * (10.0 ** (db / 20.0))
        if kind == "fade_in":
            dur = float(params.get("duration_s", 0.1))
            n = min(int(dur * sr), y.shape[0])
            env = np.ones(y.shape[0])
            env[:n] = np.linspace(0, 1, n)
            return (y.T * env).T
        if kind == "fade_out":
            dur = float(params.get("duration_s", 0.1))
            n = min(int(dur * sr), y.shape[0])
            env = np.ones(y.shape[0])
            env[-n:] = np.linspace(1, 0, n)
            return (y.T * env).T
        if kind == "eq":
            from moodify.processing import apply_rbj_eq
            return apply_rbj_eq(y, sr, params.get("filters", params.get("eq", [])))
        if kind == "compressor":
            from moodify.processing.operators import apply_compressor
            kwargs = {k: params[k] for k in ("threshold_db", "ratio", "attack_ms", "release_ms") if k in params}
            return apply_compressor(y, sr, **kwargs)
        if kind == "limiter":
            from moodify.processing.operators import apply_limiter
            kwargs = {k: params[k] for k in ("ceiling_db", "attack_ms", "release_ms", "mode") if k in params}
            return apply_limiter(y, sr, **kwargs)
        raise ValueError(f"Unsupported processing type: {kind}")
