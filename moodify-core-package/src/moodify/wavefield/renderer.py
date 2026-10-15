"""Field renderer — deterministic algorithmic room field (v0).

The renderer places a waveform into the field named by a :class:`~moodify.wavefield.models.FieldSpec`
and writes the result as a normal WAV.  It is deliberately **not** routed
through :class:`moodify.processing.pedalboard_chain.MoodifyDSPChain`: that chain
also applies EQ, compression, distortion and a hard ceiling, which are finishing
operations, not the field itself.  v0 isolates spatial-field behaviour.

What is guaranteed:

* the source file is never opened for writing, and may never be the output;
* sample rate and channel count are preserved;
* non-finite output is rejected instead of written;
* the render is deterministic (same input + same field + same library versions
  give the same bytes);
* if the render would exceed a safe peak, a **minimal safety gain** is applied
  and recorded explicitly — never silent clipping;
* source and output SHA-256, the exact field, and the renderer version are all
  recorded next to the audio.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import soundfile as sf

from moodify.audio_io import load_audio
from moodify.auditory.models import utcnow
from moodify.wavefield.models import RENDER_SCHEMA, FieldSpec

#: Renderer identity.  Bump on any change to the audio path — it is part of the
#: reproducibility contract, so a render from an older version must be
#: recognisable as such.
RENDERER_ID = "moodify.wavefield.renderer/algorithmic-room-v0.1"
ENGINE_VERSION = "algorithmic-room-v0.1"

#: Peak ceiling.  Renders above this are attenuated, never clipped.
SAFE_PEAK_DBFS = -0.1
SAFE_PEAK_LINEAR = 10.0 ** (SAFE_PEAK_DBFS / 20.0)

#: WAV encoding of a render.  32-bit float keeps the field render exact (no
#: quantisation) and makes byte-level determinism checkable.
WAV_SUBTYPE = "FLOAT"

#: Engine gain calibration, **measured** on pedalboard 0.9.23 (see
#: ``docs`` note in the module docstring).  ``pedalboard.Reverb`` is JUCE's
#: reverb, whose ``dry_level`` is a *gain* where ``0.5`` is unity (+6 dB at
#: 1.0) and whose wet path is scaled by ``sqrt(2)``.
#:
#: Why this matters: taken literally, ``dry_level = 1 - wet`` would make every
#: field probe arrive ~5 LU louder than the source.  The loudness search would
#: then be dominated by a library gain convention rather than by space — a
#: field is supposed to change *space*, not level.  So the dry path is
#: normalised to unity and ``wet`` is made a true linear wet fraction:
#:
#:     dry path gain = 1 - wet        wet path gain = wet
#:
#: The compensation is recorded in every render, because a future pedalboard
#: version that changed these conventions would break reproducibility and must
#: be visible as such.
ENGINE_DRY_UNITY = 0.5
ENGINE_WET_SCALE = 2.0 ** 0.5
ENGINE_CALIBRATION_SOURCE = "measured on pedalboard 0.9.23"


def engine_calibration() -> dict:
    return {
        "dry_unity": ENGINE_DRY_UNITY,
        "wet_scale": round(ENGINE_WET_SCALE, 6),
        "source": ENGINE_CALIBRATION_SOURCE,
        "result": "dry path unity; FieldSpec.wet is the linear wet fraction",
    }


def engine_library() -> dict:
    import pedalboard  # hard dependency: a missing pedalboard is a broken install

    return {"name": "pedalboard", "version": getattr(pedalboard, "__version__", "unknown")}


class WaveFieldRenderError(RuntimeError):
    """A render that must not be written, with a machine-readable reason."""

    def __init__(self, code: str, detail: str = "") -> None:
        super().__init__(f"{code}: {detail}" if detail else code)
        self.code = code
        self.detail = detail

    def to_dict(self) -> dict[str, str]:
        return {"code": self.code, "detail": self.detail}


# ---------------------------------------------------------------------------
# Hashing / peak helpers
# ---------------------------------------------------------------------------


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: str | os.PathLike[str]) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def peak_dbfs(samples: np.ndarray) -> float:
    if samples.size == 0:
        return -240.0
    return float(20.0 * math.log10(float(np.max(np.abs(samples))) + 1e-12))


def _same_file(a: Path, b: Path) -> bool:
    try:
        if a.resolve() == b.resolve():
            return True
    except OSError:  # pragma: no cover - resolve() on exotic paths
        pass
    try:
        return a.exists() and b.exists() and os.path.samefile(a, b)
    except OSError:
        return False


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------


def _build_board(field: FieldSpec):
    import pedalboard

    params = field.parameters
    wet = params["wet"]
    return pedalboard.Pedalboard(
        [
            pedalboard.Reverb(
                room_size=params["room_size"],
                damping=params["damping"],
                wet_level=wet / ENGINE_WET_SCALE,
                dry_level=ENGINE_DRY_UNITY * (1.0 - wet),
                width=params["width"],
            )
        ]
    )


def render_array(
    samples: np.ndarray, sample_rate: int, field: FieldSpec
) -> tuple[np.ndarray, dict]:
    """Render ``samples`` in ``field``.  Returns ``(audio, safety)``.

    ``audio`` has the same shape as the input (``(n,)`` mono or ``(n, ch)``).
    """
    x = np.asarray(samples)
    if x.ndim not in (1, 2) or x.size == 0:
        raise WaveFieldRenderError(
            "UNSUPPORTED_SHAPE", f"expected 1-D or 2-D non-empty audio, got {x.shape}"
        )
    if not np.all(np.isfinite(x)):
        raise WaveFieldRenderError("NON_FINITE_INPUT", "source contains NaN/Inf samples")
    try:
        sample_rate = int(sample_rate)
    except (TypeError, ValueError) as exc:
        raise WaveFieldRenderError("BAD_SAMPLE_RATE", repr(sample_rate)) from exc
    if sample_rate <= 0:
        raise WaveFieldRenderError("BAD_SAMPLE_RATE", repr(sample_rate))

    is_stereo = x.ndim == 2
    board_input = np.ascontiguousarray(x.T if is_stereo else x.reshape(1, -1), dtype=np.float32)

    rendered = np.asarray(_build_board(field)(board_input, sample_rate))
    if not np.all(np.isfinite(rendered)):
        raise WaveFieldRenderError("NON_FINITE_OUTPUT", "renderer produced NaN/Inf")
    if rendered.shape != board_input.shape:
        raise WaveFieldRenderError(
            "CHANNEL_COUNT_CHANGED",
            f"{board_input.shape[0]} -> {rendered.shape[0]} channels",
        )

    out = np.ascontiguousarray(rendered.T if is_stereo else rendered[0], dtype=np.float32)

    before_dbfs = peak_dbfs(out)
    safety_gain_db = 0.0
    peak = float(np.max(np.abs(out))) if out.size else 0.0
    if peak > SAFE_PEAK_LINEAR:
        safety_gain_db = round(20.0 * math.log10(SAFE_PEAK_LINEAR / peak), 6)
        out = (out * np.float32(10.0 ** (safety_gain_db / 20.0))).astype(np.float32)
        # rounding the gain to 6 decimals can leave the peak a hair above the
        # ceiling; trim the residual rather than ship an over-ceiling render.
        residual = float(np.max(np.abs(out))) if out.size else 0.0
        if residual > SAFE_PEAK_LINEAR:
            out = (out * np.float32(SAFE_PEAK_LINEAR / residual)).astype(np.float32)

    safety = {
        "peak_dbfs_before_safety": round(before_dbfs, 4),
        "peak_dbfs_after_safety": round(peak_dbfs(out), 4),
        "safety_gain_db": safety_gain_db,
        "safety_gain_applied": safety_gain_db != 0.0,
        "clipped": False,
        "policy": f"attenuate to {SAFE_PEAK_DBFS} dBFS; never clip",
    }
    return out, safety


def normalise_wav_metadata(path: str | os.PathLike[str]) -> bool:
    """Zero the wall-clock timestamp libsndfile stamps into the WAV ``PEAK`` chunk.

    ``libsndfile`` writes a ``PEAK`` chunk into every float WAV and fills its
    timestamp with the current time.  Those four bytes make two *identical*
    renders differ, which would break the reproducibility claim for exactly the
    artifact we promise to reproduce — and would make "same field ⇒ same hash"
    quietly false.

    The chunk's peak values (the useful part, read by editors) are kept; only
    the timestamp is normalised.  Returns whether a chunk was found and patched.
    """
    target = Path(path)
    try:
        data = bytearray(target.read_bytes())
    except OSError:  # pragma: no cover - unfreadable just-written file
        return False

    offset = _wav_chunk_offset(data, b"PEAK")
    # layout: "PEAK" | uint32 size | uint32 version | uint32 timestamp | peaks...
    if offset < 0 or int.from_bytes(data[offset + 4 : offset + 8], "little") < 12:
        return False
    data[offset + 12 : offset + 16] = b"\x00\x00\x00\x00"
    target.write_bytes(bytes(data))
    return True


def _wav_chunk_offset(data: bytes | bytearray, target: bytes) -> int:
    """Offset of the first RIFF chunk with id ``target``, or -1."""
    if len(data) < 12 or bytes(data[:4]) != b"RIFF" or bytes(data[8:12]) != b"WAVE":
        return -1
    pos = 12
    while pos + 8 <= len(data):
        chunk_id = bytes(data[pos : pos + 4])
        size = int.from_bytes(data[pos + 4 : pos + 8], "little")
        if chunk_id == target:
            return pos
        pos += 8 + size + (size & 1)
    return -1


@dataclass(frozen=True)
class RenderResult:
    """The record written next to every rendered candidate."""

    source_path: str
    source_sha256: str
    field: dict
    field_hash: str
    output_path: str
    output_sha256: str
    sample_rate: int
    channels: int
    frames: int
    duration_seconds: float
    peak_dbfs_before_safety: float
    peak_dbfs_after_safety: float
    safety_gain_db: float
    safety_gain_applied: bool
    created_at: str
    renderer: str = RENDERER_ID
    engine_version: str = ENGINE_VERSION
    schema: str = RENDER_SCHEMA
    engine_calibration: dict = field(default_factory=engine_calibration)
    engine_library: dict = field(default_factory=engine_library)
    wav_metadata_normalised: bool = True

    def to_dict(self) -> dict:
        return {
            "schema": self.schema,
            "renderer": self.renderer,
            "engine_version": self.engine_version,
            "engine_calibration": self.engine_calibration,
            "engine_library": self.engine_library,
            "wav_metadata_normalised": self.wav_metadata_normalised,
            "source_path": self.source_path,
            "source_sha256": self.source_sha256,
            "field": self.field,
            "field_hash": self.field_hash,
            "output_path": self.output_path,
            "output_sha256": self.output_sha256,
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "frames": self.frames,
            "duration_seconds": self.duration_seconds,
            "peak_dbfs_before_safety": self.peak_dbfs_before_safety,
            "peak_dbfs_after_safety": self.peak_dbfs_after_safety,
            "safety_gain_db": self.safety_gain_db,
            "safety_gain_applied": self.safety_gain_applied,
            "created_at": self.created_at,
        }


def render_file(
    source_path: str | os.PathLike[str],
    field: FieldSpec,
    output_path: str | os.PathLike[str],
) -> RenderResult:
    """Render a file into a field and write the WAV.  The source is never written."""
    source = Path(source_path)
    output = Path(output_path)
    if not source.is_file():
        raise WaveFieldRenderError("SOURCE_NOT_FOUND", str(source))
    if _same_file(source, output):
        raise WaveFieldRenderError(
            "OUTPUT_IS_SOURCE", "refusing to render over the source audio"
        )

    samples, sample_rate = load_audio(str(source), always_2d=False)
    audio, safety = render_array(samples, sample_rate, field)

    output.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(output), audio, int(sample_rate), subtype=WAV_SUBTYPE)
    normalised = normalise_wav_metadata(output)

    channels = 1 if audio.ndim == 1 else int(audio.shape[1])
    frames = int(audio.shape[0])
    return RenderResult(
        source_path=str(source),
        source_sha256=sha256_file(source),
        field=field.to_dict(),
        field_hash=field.field_hash(),
        output_path=str(output),
        output_sha256=sha256_file(output),
        sample_rate=int(sample_rate),
        channels=channels,
        frames=frames,
        duration_seconds=round(frames / float(sample_rate), 6),
        peak_dbfs_before_safety=safety["peak_dbfs_before_safety"],
        peak_dbfs_after_safety=safety["peak_dbfs_after_safety"],
        safety_gain_db=safety["safety_gain_db"],
        safety_gain_applied=safety["safety_gain_applied"],
        created_at=utcnow(),
        wav_metadata_normalised=normalised,
    )


def render_field_dict(
    source_path: str | os.PathLike[str],
    field_json: str | Mapping,
    output_path: str | os.PathLike[str],
) -> RenderResult:
    """Reproduce a render from a stored ``FieldSpec`` record (JSON text or mapping)."""
    field = FieldSpec.from_json(field_json) if isinstance(field_json, str) else FieldSpec.from_dict(field_json)
    return render_file(source_path, field, output_path)


def render_result_from_dict(data: Mapping) -> RenderResult:
    return RenderResult(
        source_path=data["source_path"],
        source_sha256=data["source_sha256"],
        field=dict(data["field"]),
        field_hash=data.get("field_hash", ""),
        output_path=data["output_path"],
        output_sha256=data["output_sha256"],
        sample_rate=int(data["sample_rate"]),
        channels=int(data["channels"]),
        frames=int(data.get("frames", 0)),
        duration_seconds=float(data.get("duration_seconds", 0.0)),
        peak_dbfs_before_safety=float(data.get("peak_dbfs_before_safety", 0.0)),
        peak_dbfs_after_safety=float(data.get("peak_dbfs_after_safety", 0.0)),
        safety_gain_db=float(data.get("safety_gain_db", 0.0)),
        safety_gain_applied=bool(data.get("safety_gain_applied", False)),
        created_at=data.get("created_at", ""),
        renderer=data.get("renderer", RENDERER_ID),
        engine_version=data.get("engine_version", ENGINE_VERSION),
        schema=data.get("schema", RENDER_SCHEMA),
        engine_calibration=dict(data.get("engine_calibration") or engine_calibration()),
        engine_library=dict(data.get("engine_library") or engine_library()),
        wav_metadata_normalised=bool(data.get("wav_metadata_normalised", True)),
    )


def render_result_to_dict(result: RenderResult) -> dict:
    return result.to_dict()


def render_result_to_json(result: RenderResult, indent: int = 2) -> str:
    return json.dumps(result.to_dict(), ensure_ascii=False, indent=indent)
