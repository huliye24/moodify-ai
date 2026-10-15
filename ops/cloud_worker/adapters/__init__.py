"""adapter 注册表：job_type → 已有能力。

每个 adapter 不得自带领域逻辑，只做「参数 → 调用 → 产物声明」。

| job_type       | 映射到的能力                                          | 需要 Core |
| -------------- | --------------------------------------------------- | -------- |
| `smoke`        | 无（队列往返验证，不碰音频）                            | 否 |
| `media_probe`  | ffprobe —— **媒体事实**，非 DSP / 非 Judge（裁决 2026-10-15） | 否 |
| `transcode`    | ffmpeg —— 外部工具；输出校验复用 media_probe 的探测     | 否 |
| `analyze`      | `moodify.sound_protocol.execute_job`（MSP 0.2 analyze）| **是** |
| `judge_before` | 同上，状态取自 Core 的 `workflow_decision`              | **是** |
| `manifest`     | 无 Core 权威 → `TUNABLE_CORE_NOT_AVAILABLE`            | — |

`analyze` / `judge_before` 在 Core 未安装时必须返回 `CORE_NOT_AVAILABLE` 且
**不制造任何分析产物**（裁决：不接受无条件成功桩）。
"""

from __future__ import annotations

from typing import Callable, Dict, List

from contract import JOB_TYPES

from . import analyze, manifest, media_probe, smoke, transcode
from .base import AdapterContext, AdapterError, AdapterResult, Artifact

REGISTRY: Dict[str, Callable[[AdapterContext], AdapterResult]] = {
    "smoke": smoke.run,
    "media_probe": media_probe.run,
    "transcode": transcode.run,
    "analyze": analyze.run,
    "judge_before": analyze.run_judge_before,
    "manifest": manifest.run,
}

#: 需要唯一 Moodify Core 才能跑的 job_type。其余在没有 Core 的机器上也能跑完（W3A）。
CORE_REQUIRED_JOB_TYPES = ("analyze", "judge_before")


def get_adapter(job_type: str) -> Callable[[AdapterContext], AdapterResult]:
    try:
        return REGISTRY[job_type]
    except KeyError:
        raise AdapterError(
            "UNKNOWN_JOB_TYPE",
            f"没有 {job_type!r} 的 adapter",
            f"已注册：{', '.join(sorted(REGISTRY))}",
        ) from None


def unimplemented_job_types() -> List[str]:
    """契约里声明但只有降级实现的 job_type（用于自检与报告，不假装已支持）。"""
    return [t for t in JOB_TYPES if t in ("manifest",)]


def core_free_job_types() -> List[str]:
    """不需要 Core 就能跑的任务 —— W3A 的覆盖面。"""
    return [t for t in JOB_TYPES if t not in CORE_REQUIRED_JOB_TYPES and t != "manifest"]


def registry_covers_contract() -> bool:
    """契约列出的每一种 job_type 都必须有 adapter —— 否则等于收了任务却没人接。"""
    return set(REGISTRY) == set(JOB_TYPES)


__all__ = [
    "REGISTRY",
    "CORE_REQUIRED_JOB_TYPES",
    "get_adapter",
    "registry_covers_contract",
    "unimplemented_job_types",
    "core_free_job_types",
    "AdapterContext",
    "AdapterError",
    "AdapterResult",
    "Artifact",
]
