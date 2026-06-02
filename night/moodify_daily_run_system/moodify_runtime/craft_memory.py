from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import RuntimeConfig
from .utils import utc_now_iso


def _read_manifest(run_dir: Path) -> List[Dict[str, str]]:
    path = run_dir / "manifest.csv"
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _to_float(x: Any) -> Optional[float]:
    try:
        if x in ("", None):
            return None
        return float(x)
    except Exception:
        return None


def seed_craft_memory(cfg: RuntimeConfig, run_id: Optional[str] = None, top_k: int = 10) -> Dict[str, Any]:
    cfg = cfg.resolved()
    if run_id is None:
        runs = sorted([p for p in cfg.output_root.iterdir() if p.is_dir()]) if cfg.output_root.exists() else []
        if not runs:
            raise FileNotFoundError(f"No run directories in {cfg.output_root}")
        run_dir = runs[-1]
        run_id = run_dir.name
    else:
        run_dir = cfg.output_root / run_id

    rows = _read_manifest(run_dir)
    scored = []
    for row in rows:
        delta = _to_float(row.get("pseudo_delta_mrs"))
        if delta is None:
            continue
        scored.append((delta, row))

    scored.sort(key=lambda x: x[0], reverse=True)
    best = scored[:top_k]
    worst = scored[-top_k:] if scored else []

    cfg.craft_memory_dir.mkdir(parents=True, exist_ok=True)
    path = cfg.craft_memory_dir / f"craft_memory_seed_{run_id}.md"

    lines = [
        f"# Moodify Craft Memory Seed — {run_id}",
        "",
        f"生成时间：{utc_now_iso()}",
        "",
        "> 这是 Daily Run v0.1 自动生成的工艺记忆种子文件。它不是最终结论，而是第二天人工复盘的起点。",
        "",
        "## 1. 今日有效工艺候选",
        "",
    ]

    if best:
        for delta, row in best:
            lines += [
                f"### {row.get('preset')} / {row.get('sample_id')}",
                "",
                f"- task_id：`{row.get('task_id')}`",
                f"- pseudo ΔMRS：`{delta:.4f}`",
                f"- 输出目录：`{row.get('output_dir')}`",
                "- 初步判断：待人工听感复盘",
                "- 可沉淀方向：适用样本类型 / 参数边界 / 风险点",
                "",
            ]
    else:
        lines += ["暂无。", ""]

    lines += [
        "## 2. 今日失败/退化案例",
        "",
    ]

    if worst:
        for delta, row in worst:
            lines += [
                f"### {row.get('preset')} / {row.get('sample_id')}",
                "",
                f"- task_id：`{row.get('task_id')}`",
                f"- pseudo ΔMRS：`{delta:.4f}`",
                f"- error：`{row.get('error')}`",
                "- 可能原因：待复盘",
                "- 下一轮实验：降低处理强度 / 更换 preset / 检查源文件质量",
                "",
            ]
    else:
        lines += ["暂无。", ""]

    lines += [
        "## 3. 人工复盘区",
        "",
        "- 今日最值得保留的参数：",
        "- 今日最明显的问题：",
        "- 明晚应该扩大的样本类型：",
        "- 明晚应该缩小或停止的方向：",
        "",
    ]

    path.write_text("\n".join(lines), encoding="utf-8")
    return {"craft_memory_path": str(path), "best_count": len(best), "worst_count": len(worst)}
