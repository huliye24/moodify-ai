"""`media_probe` —— 媒体事实提取。用 ffprobe。

边界（2026-10-15 裁决）
-----------------------
`media_probe` **允许直接调用 ffprobe**。它只提取**容器、编码、时长、采样率、声道**等
媒体事实 —— 不是声音分析、不是 DSP、不是 Judge，因此不违反 One Core。
需要「这片声音听起来怎样」的判断一律走 `analyze`（必须调 Core）。

本模块同时是 ffprobe 的**唯一调用点**：`transcode` 校验产物也复用它，
免得同一个事实在两处各解析一遍。
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any, Dict, Optional

from .base import AdapterContext, AdapterError, AdapterResult, Artifact, read_params, write_json_artifact
from contract import NOT_ALIGNABLE, STATUS_DONE

ALLOWED = ("raw",)


def ffprobe_exe() -> str:
    import os

    return os.environ.get("MOODIFY_FFPROBE", "ffprobe")


def probe_media(path: Path, timeout: int) -> Dict[str, Any]:
    """跑一次 ffprobe，返回原始 JSON。失败抛 TOOL_FAILED。"""
    from .base import run_tool

    exe = shutil.which(ffprobe_exe()) or ffprobe_exe()
    proc = run_tool(
        [
            exe,
            "-v", "error",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            str(path),
        ],
        timeout,
    )
    try:
        return json.loads(proc.stdout or "{}")
    except json.JSONDecodeError as exc:
        raise AdapterError("TOOL_FAILED", "ffprobe 返回的不是合法 JSON", str(exc)) from exc


def summarize(raw: Dict[str, Any], size_bytes: Optional[int] = None) -> Dict[str, Any]:
    """把 ffprobe 输出收敛成一份**媒体事实**摘要。取不到的写 not_alignable，不补算。"""
    fmt = raw.get("format") or {}
    streams = raw.get("streams") or []
    audio = next((s for s in streams if s.get("codec_type") == "audio"), None)
    if audio is None:
        raise AdapterError("TOOL_FAILED", "输入里没有音频流")

    def num(v):
        try:
            return float(v)
        except (TypeError, ValueError):
            return NOT_ALIGNABLE

    def integer(v):
        try:
            return int(v)
        except (TypeError, ValueError):
            return NOT_ALIGNABLE

    bit_depth = audio.get("bits_per_sample")
    return {
        "container": fmt.get("format_name") or NOT_ALIGNABLE,
        "codec": audio.get("codec_name") or NOT_ALIGNABLE,
        "duration_seconds": num(audio.get("duration") or fmt.get("duration")),
        "sample_rate": integer(audio.get("sample_rate")),
        "channels": integer(audio.get("channels")),
        "channel_layout": audio.get("channel_layout") or NOT_ALIGNABLE,
        "bit_depth": integer(bit_depth) if bit_depth else NOT_ALIGNABLE,
        "file_size_bytes": integer(fmt.get("size") or size_bytes),
        "audio_stream_count": sum(1 for s in streams if s.get("codec_type") == "audio"),
        "stream_count": len(streams),
    }


def run(ctx: AdapterContext) -> AdapterResult:
    params = read_params(ctx, ALLOWED)
    keep_raw = bool(params.get("raw", True))

    raw = probe_media(ctx.input_path, ctx.timeout_seconds)
    facts = summarize(raw, ctx.input_path.stat().st_size)

    payload: Dict[str, Any] = {
        "media_facts": facts,
        "boundary": (
            "仅媒体事实（容器/编码/时长/采样率/声道）。"
            "本任务不做声音分析、不调 DSP、不产生判定。"
        ),
    }
    if keep_raw:
        payload["ffprobe"] = raw

    artifact, _ = write_json_artifact(ctx, "media_probe.json", payload, role="evidence")

    return AdapterResult(
        status=STATUS_DONE,
        artifacts=[artifact],
        params={"raw": keep_raw},
        core_version=NOT_ALIGNABLE,  # 本任务不碰 Core，如实写不可对齐
        tool_versions={"ffprobe": _ffprobe_version()},
        verdict=facts,
    )


def _ffprobe_version() -> str:
    from .base import run_tool

    try:
        proc = run_tool([shutil.which(ffprobe_exe()) or ffprobe_exe(), "-version"], 30)
        lines = (proc.stdout or "").splitlines()
        return lines[0].strip() if lines else NOT_ALIGNABLE
    except AdapterError:
        return NOT_ALIGNABLE


__all__ = ["run", "probe_media", "summarize", "ALLOWED", "Artifact"]
