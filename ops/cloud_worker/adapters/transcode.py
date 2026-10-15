"""`transcode` —— WAV/FLAC → AAC/M4A。用 ffmpeg。

边界
----
Core 没有转码能力，ffmpeg 是机器上既有的外部工具（方案 §1 实测 ffmpeg 6.1.1）。
worker 在这里扮演**调用者**：给定显式参数、跑工具、校验产物。不实现任何 DSP，
也不定义任何质量判断 —— 时长漂移门限是**输入校验**，不是质量判定。

产物校验复用 :mod:`media_probe` 的 ffprobe 探测（同一份媒体事实，不解析两遍）。
因此本任务**不需要 Core**，属于 W3A 的覆盖面。

原始资产永不覆盖：只往本任务的 out_dir 写，输入是只读下载到 input/ 的副本。
"""

from __future__ import annotations

import os
from pathlib import Path

from .base import (
    AdapterContext,
    AdapterError,
    AdapterResult,
    Artifact,
    ffmpeg_version,
    read_params,
    run_tool,
    write_json_artifact,
)
from .media_probe import probe_media, summarize
from contract import NOT_ALIGNABLE, STATUS_DONE

ALLOWED = ("format", "bitrate", "sample_rate", "channels", "max_duration_drift_seconds")
DEFAULT_BITRATE = "256k"
DEFAULT_DRIFT = 0.05

#: 目标格式 → ffmpeg 编码器。容器统一 m4a。
FORMATS = {"m4a": "aac", "aac": "aac"}


def _ffmpeg_exe() -> str:
    return os.environ.get("MOODIFY_FFMPEG", "ffmpeg")


def run(ctx: AdapterContext) -> AdapterResult:
    params = read_params(ctx, ALLOWED)

    fmt = str(params.get("format", "m4a")).lower()
    if fmt not in FORMATS:
        raise AdapterError(
            "SCHEMA_INVALID", f"不支持的 format={fmt!r}", f"支持：{', '.join(sorted(FORMATS))}"
        )
    codec = FORMATS[fmt]
    bitrate = str(params.get("bitrate", DEFAULT_BITRATE))
    sample_rate = params.get("sample_rate")
    channels = params.get("channels")
    max_drift = float(params.get("max_duration_drift_seconds", DEFAULT_DRIFT))

    facts_in = summarize(probe_media(ctx.input_path, ctx.timeout_seconds))

    out_path = ctx.out_dir / f"{ctx.input_path.stem}.m4a"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    argv = [
        _ffmpeg_exe(), "-hide_banner", "-nostdin", "-y",
        "-i", str(ctx.input_path),
        "-c:a", codec, "-b:a", bitrate,
    ]
    if sample_rate:
        argv += ["-ar", str(int(sample_rate))]
    if channels:
        argv += ["-ac", str(int(channels))]
    argv += ["-movflags", "+faststart", str(out_path)]

    ctx.log(f"ffmpeg 转码 → {out_path.name} ({codec} {bitrate})")
    run_tool(argv, ctx.timeout_seconds)

    if not out_path.is_file() or out_path.stat().st_size == 0:
        raise AdapterError("TOOL_FAILED", "ffmpeg 声称成功但没有产出有效文件", str(out_path))

    facts_out = summarize(probe_media(out_path, ctx.timeout_seconds))

    drift = _drift(facts_in["duration_seconds"], facts_out["duration_seconds"])
    # 时长漂移是**输入校验**：漂太多说明转码错了，不是「质量稍差」
    if drift is not NOT_ALIGNABLE and drift > max_drift:
        raise AdapterError(
            "TOOL_FAILED",
            f"转码后时长漂移 {drift:.4f}s 超过门限 {max_drift}s",
            f"输入 {facts_in['duration_seconds']}s → 输出 {facts_out['duration_seconds']}s",
        )
    if channels and facts_out["channels"] is not NOT_ALIGNABLE:
        if int(facts_out["channels"]) != int(channels):
            raise AdapterError(
                "TOOL_FAILED",
                f"输出声道数 {facts_out['channels']} 与要求的 {channels} 不符",
            )

    in_bytes = facts_in["file_size_bytes"]
    report, _ = write_json_artifact(
        ctx,
        "transcode_report.json",
        {
            "format": fmt,
            "codec": codec,
            "bitrate": bitrate,
            "sample_rate_requested": sample_rate,
            "channels_requested": channels,
            "input_media_facts": facts_in,
            "output_media_facts": facts_out,
            "duration_drift_seconds": drift,
            "max_duration_drift_seconds": max_drift,
            "size_ratio": (
                round(out_path.stat().st_size / int(in_bytes), 4)
                if in_bytes is not NOT_ALIGNABLE and int(in_bytes) > 0
                else NOT_ALIGNABLE
            ),
        },
        role="report",
    )

    media = Artifact(path=str(out_path), role="media", key_suffix=out_path.name)

    return AdapterResult(
        status=STATUS_DONE,
        artifacts=[media, report],
        params={
            "format": fmt,
            "bitrate": bitrate,
            "sample_rate": sample_rate,
            "channels": channels,
            "max_duration_drift_seconds": max_drift,
        },
        core_version=NOT_ALIGNABLE,  # 本任务不碰 Core
        tool_versions={"ffmpeg": ffmpeg_version(_ffmpeg_exe())},
        verdict={
            "duration_drift_seconds": drift,
            "output_bytes": out_path.stat().st_size,
            "input_bytes": in_bytes,
        },
    )


def _drift(before, after):
    """时长漂移；任一侧不可对齐就写 not_alignable —— **不补算**。"""
    if before is NOT_ALIGNABLE or after is NOT_ALIGNABLE:
        return NOT_ALIGNABLE
    return round(abs(float(after) - float(before)), 6)


__all__ = ["run", "ALLOWED", "Artifact", "Path"]
