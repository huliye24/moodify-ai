from __future__ import annotations

import json
import math
import os
import sys
import wave
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .utils import write_json, utc_now_iso


AUDIO_SUFFIXES = {".wav", ".mp3", ".flac", ".m4a", ".aac", ".ogg"}

# ── MRS Open v0.3.1 safe import ──────────────────────────
_MRS_OPEN_ENGINE = None
_MRS_OPEN_DREF = None
_MRS_OPEN_ERROR = None


def _init_mrs_open() -> bool:
    """延迟初始化 MRS Open v0.3.1 引擎。成功返回 True。"""
    global _MRS_OPEN_ENGINE, _MRS_OPEN_DREF, _MRS_OPEN_ERROR
    if _MRS_OPEN_ENGINE is not None:
        return True
    if _MRS_OPEN_ERROR is not None:
        return False
    try:
        _project_root = Path(__file__).resolve().parent.parent
        _moodify_src = _project_root / "moodify-core-package" / "src"
        if str(_moodify_src) not in sys.path:
            sys.path.insert(0, str(_moodify_src))
        if str(_project_root) not in sys.path:
            sys.path.insert(0, str(_project_root))

        from workers.mrs_open_benchmark_v03 import compute_mrs_open, calibrate_dref
        import yaml

        # Load D_ref from config, with fallback default
        _MRS_OPEN_DREF = 0.274350  # default
        config_path = _project_root / "configs" / "mrs_open_v03.yaml"
        if config_path.exists():
            try:
                with open(config_path) as f:
                    cfg = yaml.safe_load(f) or {}
                cal = cfg.get("calibration", {})
                configured_dref = cal.get("d_ref")
                if configured_dref is not None:
                    _MRS_OPEN_DREF = float(configured_dref)
            except Exception:
                pass  # use default

        _MRS_OPEN_ENGINE = compute_mrs_open
        return True
    except Exception as e:
        _MRS_OPEN_ERROR = f"mrs_open_v031_init_failed: {e}"
        return False


def compute_mrs_open_v031(audio_path: str) -> Dict[str, Any]:
    """计算 MRS Open v0.3.1，失败时返回 error 字段但不崩溃。

    Returns:
        {
            "mrs_open": float | None,
            "d_real": float | None,
            "subscores": {...} | None,
            "extra_penalties": {...} | None,
            "penalty_flags": [...],
            "error": str | None,
        }
    """
    if not _init_mrs_open():
        return {"mrs_open": None, "d_real": None, "subscores": None,
                "penalty_flags": [], "error": _MRS_OPEN_ERROR}

    if not os.path.exists(audio_path):
        return {"mrs_open": None, "d_real": None, "subscores": None,
                "penalty_flags": [], "error": f"file_not_found: {audio_path}"}

    try:
        result = _MRS_OPEN_ENGINE(audio_path, _MRS_OPEN_DREF)
        if "error" in result:
            return {"mrs_open": None, "d_real": None, "subscores": None,
                    "penalty_flags": [], "error": result.get("error")}

        flags = list(result.get("extra_penalties", {}).keys()) if result.get("extra_penalties") else []

        return {
            "mrs_open": result.get("mrs_open"),
            "d_real": result.get("d_real"),
            "subscores": result.get("subscores"),
            "extra_penalties": result.get("extra_penalties"),
            "penalty_flags": flags,
            "error": None,
        }
    except Exception as e:
        return {"mrs_open": None, "d_real": None, "subscores": None,
                "penalty_flags": [], "error": f"{type(e).__name__}: {e}"}


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

    # ── MRS Open v0.3.1 ────────────────────────────────
    mrs_open_before = compute_mrs_open_v031(str(input_path))
    mrs_open_after_val = None
    mrs_open_delta = None
    mrs_open_flags: List[str] = []
    best_output_path = best_after.get("path") if best_after else None

    if best_output_path:
        mrs_open_after = compute_mrs_open_v031(best_output_path)
        mrs_open_after_val = mrs_open_after.get("mrs_open")
        mrs_open_flags = mrs_open_after.get("penalty_flags", [])
        if mrs_open_before.get("mrs_open") is not None and mrs_open_after_val is not None:
            mrs_open_delta = mrs_open_after_val - mrs_open_before["mrs_open"]

    return {
        "input": before,
        "outputs": after_list,
        "best_output": best_after,
        "pseudo_mrs_before": before_mrs,
        "pseudo_mrs_after": after_mrs,
        "pseudo_delta_mrs": delta,
        "mrs_open_v031_before": mrs_open_before.get("mrs_open"),
        "mrs_open_v031_after": mrs_open_after_val,
        "delta_mrs_open_v031": mrs_open_delta,
        "mrs_open_before_detail": mrs_open_before,
        "mrs_open_flags": mrs_open_flags,
        "mrs_open_avail": _init_mrs_open(),
        "mrs_open_error": mrs_open_before.get("error") or (_MRS_OPEN_ERROR if not _init_mrs_open() else None),
        "note": "pseudo_mrs_v001 是 Daily Run v0.1 占位指标。mrs_open_v031 是 MRS Open v0.3.1 实验指标。",
    }
