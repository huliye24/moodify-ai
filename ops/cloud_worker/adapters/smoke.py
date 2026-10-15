"""`smoke` —— 队列往返验证任务。不碰音频，不调 Core。

用途（方案 §3.1）：验证 ``pending → claimed → done/failed`` 闭环本身。
它同时是**失败路径的主动演习**：``mode=fail`` 故意让任务进 failed/，
证明失败分支真的被走过，而不是靠推理认为它存在。
"""

from __future__ import annotations

import time

from .base import AdapterContext, AdapterError, AdapterResult, Artifact, read_params, write_json_artifact
from contract import NOT_ALIGNABLE, STATUS_DONE

ALLOWED = ("mode", "echo", "sleep_seconds", "fail_with")


def run(ctx: AdapterContext) -> AdapterResult:
    params = read_params(ctx, ALLOWED)

    mode = params.get("mode", "ok")
    if mode not in ("ok", "fail"):
        raise AdapterError("SCHEMA_INVALID", f"smoke.mode 只支持 ok|fail，收到 {mode!r}")

    sleep_seconds = float(params.get("sleep_seconds", 0) or 0)
    if sleep_seconds:
        ctx.log(f"smoke 按参数休眠 {sleep_seconds}s")
        time.sleep(sleep_seconds)

    if mode == "fail":
        code = params.get("fail_with", "INTERNAL_ERROR")
        raise AdapterError(code, "smoke 按参数故意失败（失败路径演习）", "mode=fail")

    # 产物必须**只由任务的输入决定**，一个字都不许来自「谁在什么时候跑的」——
    # 否则同一 request_id 重跑会得到不同的产物哈希，「重复执行得到同一结果」就成了空话。
    # 时间戳属于结果 JSON（started_at / finished_at），不属于产物。
    payload = {
        "mode": mode,
        "echo": params.get("echo"),
        "job_id": ctx.job["job_id"],
        "job_type": ctx.job["job_type"],
        "input_name": ctx.input_path.name,
        "input_bytes": ctx.input_path.stat().st_size if ctx.input_path.is_file() else 0,
        "note": "队列往返验证通过；此任务不做任何音频处理。",
    }
    artifact, _ = write_json_artifact(ctx, "smoke.json", payload, role="evidence")

    return AdapterResult(
        status=STATUS_DONE,
        artifacts=[artifact],
        params={"mode": mode, "sleep_seconds": sleep_seconds},
        core_version=NOT_ALIGNABLE,
        tool_versions={},
    )


__all__ = ["run", "ALLOWED", "Artifact"]
