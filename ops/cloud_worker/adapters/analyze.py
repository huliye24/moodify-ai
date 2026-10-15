"""`analyze` —— 只读分析。调 Core 的 MSP 0.2 analyze 作业。

Core 侧走的是 ``moodify.sound_protocol.execute_job``（``moodify protocol process``
用的同一个函数），产出 case bundle + report 三件套。worker 不重算任何指标，
只负责把产物收集、上传、并把 Core 的结论原样写进证据。

判定规则（judge_before 复用本模块）
-----------------------------------
Core 的 ``workflow_decision`` 是权威结论，这里只做**翻译**，不做二次判断：

    PASS_TO_LISTENING  → HUMAN_REQUIRED   机器说技术证据够了，听感归人类
    INCONCLUSIVE       → INCONCLUSIVE     证据不足，不装成 PASS
    REJECT_TECHNICAL   → DONE             机器给出了确定的否定技术结论
    其它/缺失          → INCONCLUSIVE     认不出就保守，绝不默认 PASS
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Tuple

from .base import (
    AdapterContext,
    AdapterError,
    AdapterResult,
    Artifact,
    collect_tree_artifacts,
    read_params,
    write_json_artifact,
)
from contract import STATUS_DONE, STATUS_HUMAN_REQUIRED, STATUS_INCONCLUSIVE

ALLOWED = ("max_artifact_bytes",)
DEFAULT_MAX_ARTIFACT_BYTES = 64 * 1024 * 1024

#: Core 的 `workflow_decision` 取值是 **Core 的词汇表**（大写），不是本项目的生命周期状态；
#: 键必须原样保留才能匹配 Core 的输出。右侧才是我们的小写终态。
DECISION_TO_STATUS: Dict[str, str] = {
    "PASS_TO_LISTENING": STATUS_HUMAN_REQUIRED,
    "INCONCLUSIVE": STATUS_INCONCLUSIVE,
    "REJECT_TECHNICAL": STATUS_DONE,
}


def _write_msp_job(ctx: AdapterContext) -> Path:
    """落一个 MSP 0.2 analyze job。

    路径按 MSP 的既有约定相对 job 文件解析，所以两个路径都给绝对路径。
    job 文件放 scratch（不进上传目录），case bundle 直接落在 out_dir。
    """
    job_path = ctx.scratch_dir / "msp_job.json"
    job_path.write_text(
        json.dumps(
            {
                "protocol": "moodify.sound/0.2",
                "type": "analyze",
                "source": str(ctx.input_path.resolve()),
                "output_dir": str(ctx.out_dir.resolve()),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return job_path


def _run_core_analyze(ctx: AdapterContext) -> Tuple[Dict[str, Any], str]:
    job_path = _write_msp_job(ctx)
    out_json = str(ctx.scratch_dir / "analyze.json")
    payload = ctx.core.call(
        ["analyze", "--job", str(job_path)], ctx.timeout_seconds, out_path=out_json
    )
    return payload["result"], payload.get("core_version", "not_alignable")


def _collect(ctx: AdapterContext) -> Tuple[list, list]:
    params = read_params(ctx, ALLOWED)
    max_bytes = int(params.get("max_artifact_bytes", DEFAULT_MAX_ARTIFACT_BYTES))
    return collect_tree_artifacts(ctx, ctx.out_dir, max_bytes=max_bytes)


def _summary(ctx: AdapterContext, core_result: Dict[str, Any]) -> Artifact:
    return write_json_artifact(
        ctx,
        "worker_analysis_summary.json",
        {
            "case_id": core_result.get("case_id"),
            "case_root": core_result.get("case_root"),
            "overall_status": core_result.get("overall_status"),
            "workflow_decision": core_result.get("workflow_decision"),
            "judgment_boundary": core_result.get("judgment_boundary"),
            "plan_status": core_result.get("plan_status"),
            "review_required": core_result.get("review_required"),
            "source_sha256": core_result.get("source_sha256"),
            "note": "本文件由 worker 汇总 Core 的返回；判定本身由 Core 做出。",
        },
        role="report",
    )[0]


def _verdict_of(core_result: Dict[str, Any], artifacts: list, skipped: list) -> Dict[str, Any]:
    return {
        "overall_status": core_result.get("overall_status"),
        "workflow_decision": core_result.get("workflow_decision"),
        "judgment_boundary": core_result.get("judgment_boundary"),
        "case_id": core_result.get("case_id"),
        "artifact_count": len(artifacts),
        "skipped": skipped,
    }


def status_for_decision(decision: Any) -> str:
    """Core 的 workflow_decision → 任务状态。认不出就 INCONCLUSIVE，绝不默认 PASS。"""
    return DECISION_TO_STATUS.get(str(decision), STATUS_INCONCLUSIVE)


def run(ctx: AdapterContext) -> AdapterResult:
    require_core_available(ctx.core)
    core_result, core_version = _run_core_analyze(ctx)
    artifacts, skipped = _collect(ctx)
    summary = _summary(ctx, core_result)
    artifacts = [summary, *artifacts]
    if skipped:
        ctx.log(f"analyze 跳过 {len(skipped)} 个中间产物（已记入结果）")

    return AdapterResult(
        status=STATUS_DONE,
        artifacts=artifacts,
        params={"max_artifact_bytes": DEFAULT_MAX_ARTIFACT_BYTES},
        core_version=core_version,
        tool_versions={},
        verdict=_verdict_of(core_result, artifacts, skipped),
    )


def run_judge_before(ctx: AdapterContext) -> AdapterResult:
    """`judge_before`：跑同一条 analyze 路径，但以 Core 的判定作为任务状态。

    不新增任何判断逻辑 —— 状态是 ``workflow_decision`` 的翻译结果。
    Core 不在就 `CORE_NOT_AVAILABLE`，绝不退化成桩式成功。
    """
    require_core_available(ctx.core)
    core_result, core_version = _run_core_analyze(ctx)
    artifacts, skipped = _collect(ctx)
    summary = _summary(ctx, core_result)
    artifacts = [summary, *artifacts]

    decision = core_result.get("workflow_decision")
    status = status_for_decision(decision)

    return AdapterResult(
        status=status,
        artifacts=artifacts,
        params={"max_artifact_bytes": DEFAULT_MAX_ARTIFACT_BYTES},
        core_version=core_version,
        tool_versions={},
        verdict=_verdict_of(core_result, artifacts, skipped),
    )


def require_core_available(core) -> None:
    """前置检查：Core 装不上就早失败（`CORE_NOT_AVAILABLE`），别先把大文件拉下来。

    裁决（2026-10-15）：`analyze` / `judge_before` **必须**调用唯一 Moodify Core；
    Core 未安装时不得制造分析产物。worker 在下载输入**之前**调一次，adapter 自己也调一次
    —— 前置检查是省流量，adapter 里那次才是不可绕过的那道。
    """
    from contract import NOT_ALIGNABLE

    if core is None or core.version() == NOT_ALIGNABLE:
        raise AdapterError(
            "CORE_NOT_AVAILABLE",
            "Core 未安装或不可导入",
            "在节点 venv 安装可复现的版本化 wheel 后重试；不从仓库源码路径临时 import。",
        )


__all__ = ["run", "run_judge_before", "status_for_decision", "ALLOWED", "Artifact"]
