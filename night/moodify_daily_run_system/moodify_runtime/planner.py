from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import RuntimeConfig
from .failure import analyze_failures
from .queue import plan_queue


def suggest_next_plan(cfg: RuntimeConfig, run_id: Optional[str] = None) -> Dict[str, Any]:
    """
    v0.1 简单实验规划器：
    - 如果失败多，先建议 smoke / CLI 修复
    - 如果成功稳定，建议扩大样本
    - 未来可接入 MRS 分项指标，自动生成更精细的实验队列
    """
    failure = analyze_failures(cfg, run_id=run_id)
    total_failures = failure.get("total_failures", 0)
    classes = failure.get("classes", {})

    suggestions: List[str] = []
    if total_failures > 0:
        suggestions.append("先修复失败任务，不要盲目扩大样本。")
        if classes.get("cli_argument"):
            suggestions.append("CLI 参数错误较多：运行 python3 cli.py process --help，更新 command_templates。")
        if classes.get("path_missing"):
            suggestions.append("路径错误较多：检查 project_root、input_dirs、output_root。")
        if classes.get("audio_format"):
            suggestions.append("音频格式问题较多：优先用 WAV 样本做 Night Run。")
        if classes.get("timeout"):
            suggestions.append("任务超时：降低 max_files 或延长 timeout_seconds_per_task。")
    else:
        suggestions.append("失败任务为 0：可以扩大样本数量，或增加新的 preset 组合。")
        suggestions.append("建议新增 10-30 首真实 AI 音乐样本，继续跑 warm_vocal / clean_master / wide_space。")

    return {
        "failure_analysis": failure,
        "suggestions": suggestions,
    }
