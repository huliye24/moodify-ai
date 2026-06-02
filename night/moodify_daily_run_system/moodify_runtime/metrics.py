from __future__ import annotations

import json
import math
import wave
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .utils import write_json, utc_now_iso


AUDIO_SUFFIXES = {".wav", ".mp3", ".flac", ".m4a", ".aac", ".ogg"}


def _safe_float(x: Any) -> Optional[float]:
    try:
        value = float(x)
        if math.isfinite(value):
            return value
    except Exception:
        pass
    return None


def analyze_wav_stdlib(path: Path) -> Dict[str, Any]:
    """
    无第三方依赖的 WAV 基础指标。
    非 WAV 文件会返回 unsupported，但不会让系统崩掉。
    """
    metrics: Dict[str, Any] = {
        "path": str(path),
        "filename": path.name,
        "suffix": path.suffix.lower(),
        "analyzed_at": utc_now_iso(),
        "supported": False,
        "engine": "stdlib_wave",
        "duration_seconds": None,
        "sample_rate": None,
        "channels": None,
        "sample_width_bytes": None,
        "frame_count": None,
        "rms": None,
        "peak": None,
        "crest_factor": None,
        "dc_offset": None,
        "error": None,
    }
    if path.suffix.lower() != ".wav":
        metrics["error"] = "non_wav_file_basic_metrics_only"
        return metrics

    try:
        with wave.open(str(path), "rb") as wf:
            channels = wf.getnchannels()
            sample_width = wf.getsampwidth()
            sample_rate = wf.getframerate()
            nframes = wf.getnframes()
            raw = wf.readframes(nframes)

        if sample_width not in (1, 2, 3, 4):
            metrics["error"] = f"unsupported_sample_width_{sample_width}"
            return metrics

        # 为避免依赖 numpy，这里手写 PCM 解析。24-bit 做近似解析。
        values: List[int] = []
        if sample_width == 1:
            # unsigned 8-bit PCM
            values = [b - 128 for b in raw]
            max_abs = 128.0
        elif sample_width == 2:
            import struct
            count = len(raw) // 2
            values = list(struct.unpack("<" + "h" * count, raw[:count * 2]))
            max_abs = 32768.0
        elif sample_width == 3:
            # signed 24-bit little-endian
            max_abs = 8388608.0
            values = []
            for i in range(0, len(raw) - 2, 3):
                b = raw[i:i+3]
                val = int.from_bytes(b + (b"\xff" if b[2] & 0x80 else b"\x00"), "little", signed=True)
                values.append(val)
        else:
            import struct
            count = len(raw) // 4
            values = list(struct.unpack("<" + "i" * count, raw[:count * 4]))
            max_abs = 2147483648.0

        if not values:
            metrics["error"] = "empty_audio"
            return metrics

        sum_sq = 0.0
        sum_v = 0.0
        peak_i = 0
        for v in values:
            sum_sq += v * v
            sum_v += v
            av = abs(v)
            if av > peak_i:
                peak_i = av

        rms_i = math.sqrt(sum_sq / len(values))
        rms = rms_i / max_abs
        peak = peak_i / max_abs
        crest = peak / rms if rms > 1e-12 else None
        dc = (sum_v / len(values)) / max_abs

        metrics.update({
            "supported": True,
            "duration_seconds": nframes / sample_rate if sample_rate else None,
            "sample_rate": sample_rate,
            "channels": channels,
            "sample_width_bytes": sample_width,
            "frame_count": nframes,
            "rms": rms,
            "peak": peak,
            "crest_factor": crest,
            "dc_offset": dc,
            "error": None,
        })
        return metrics
    except Exception as e:
        metrics["error"] = f"{type(e).__name__}: {e}"
        return metrics


def pseudo_mrs(metrics: Dict[str, Any]) -> Optional[float]:
    """
    MRS 占位版：不是最终 Moodify Reality Score。
    目的只是让 Daily Run v0.1 有可比较的数值入口。
    后续应替换为 MRS v0.2 / v0.3 的真实公式。
    """
    if not metrics.get("supported"):
        return None

    rms = _safe_float(metrics.get("rms"))
    peak = _safe_float(metrics.get("peak"))
    crest = _safe_float(metrics.get("crest_factor"))
    dc = abs(_safe_float(metrics.get("dc_offset")) or 0.0)

    if rms is None or peak is None or crest is None:
        return None

    # 只是工程占位：鼓励不过载、有一定动态、DC 偏移小。
    peak_score = max(0.0, min(1.0, 1.0 - max(0.0, peak - 0.98) * 10.0))
    rms_score = max(0.0, min(1.0, 1.0 - abs(rms - 0.12) / 0.20))
    crest_score = max(0.0, min(1.0, 1.0 - abs(crest - 8.0) / 12.0))
    dc_score = max(0.0, min(1.0, 1.0 - dc * 100.0))

    return 100.0 * (0.25 * peak_score + 0.25 * rms_score + 0.35 * crest_score + 0.15 * dc_score)


def analyze_audio(path: Path) -> Dict[str, Any]:
    metrics = analyze_wav_stdlib(path)
    metrics["pseudo_mrs_v001"] = pseudo_mrs(metrics)
    return metrics


def find_audio_outputs(output_dir: Path, suffixes: Optional[List[str]] = None) -> List[Path]:
    suffix_set = {s.lower() for s in (suffixes or list(AUDIO_SUFFIXES))}
    if not output_dir.exists():
        return []
    return sorted([p for p in output_dir.rglob("*") if p.is_file() and p.suffix.lower() in suffix_set])


def compare_before_after(input_path: Path, output_dir: Path) -> Dict[str, Any]:
    before = analyze_audio(input_path)
    outputs = find_audio_outputs(output_dir)
    after_list = [analyze_audio(p) for p in outputs]

    best_after = None
    if after_list:
        best_after = max(
            after_list,
            key=lambda m: m.get("pseudo_mrs_v001") if m.get("pseudo_mrs_v001") is not None else -1e9
        )

    before_mrs = before.get("pseudo_mrs_v001")
    after_mrs = best_after.get("pseudo_mrs_v001") if best_after else None
    delta = None
    if before_mrs is not None and after_mrs is not None:
        delta = after_mrs - before_mrs

    return {
        "input": before,
        "outputs": after_list,
        "best_output": best_after,
        "pseudo_mrs_before": before_mrs,
        "pseudo_mrs_after": after_mrs,
        "pseudo_delta_mrs": delta,
        "note": "pseudo_mrs_v001 是 Daily Run v0.1 占位指标，不是正式 MRS。",
    }
