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
    mrs_open_used = False

    for row in rows:
        # Prefer delta_mrs_open_v031, fallback to pseudo_delta_mrs
        delta_open = _to_float(row.get("delta_mrs_open_v031"))
        delta_pseudo = _to_float(row.get("pseudo_delta_mrs"))

        if delta_open is not None:
            scored.append((delta_open, row, "mrs_open_v031"))
            mrs_open_used = True
        elif delta_pseudo is not None:
            scored.append((delta_pseudo, row, "pseudo_mrs_v001"))

    scored.sort(key=lambda x: x[0], reverse=True)
    best = scored[:top_k]
    worst = scored[-top_k:] if scored else []

    cfg.craft_memory_dir.mkdir(parents=True, exist_ok=True)
    path = cfg.craft_memory_dir / f"craft_memory_seed_{run_id}.md"

    metric_label = "MRS Open v0.3.1" if mrs_open_used else "pseudo MRS v001"

    lines = [
        f"# Moodify Craft Memory Seed — {run_id}",
        "",
        f"生成时间：{utc_now_iso()}",
        f"排序指标：{metric_label}",
        "",
        "> 这是 Daily Run 自动生成的工艺记忆种子文件。它不是最终结论，而是第二天人工复盘的起点。",
        "",
        "## 1. 今日有效工艺候选",
        "",
    ]

    if best:
        for delta, row, src in best:
            mrs_before = _to_float(row.get("mrs_open_v031_before"))
            mrs_after = _to_float(row.get("mrs_open_v031_after"))
            pseudo_d = _to_float(row.get("pseudo_delta_mrs"))
            flags = row.get("mrs_open_flags", "") or ""

            lines += [
                f"### {row.get('preset')} / {row.get('sample_id')}",
                "",
                f"- task_id：`{row.get('task_id')}`",
                f"- ΔMRS (open)：`{delta:.1f}` (source: {src})",
                f"- ΔMRS (pseudo)：`{pseudo_d:.1f}`" if pseudo_d is not None else "- ΔMRS (pseudo)：N/A",
                f"- MRS Open：`{mrs_before:.0f}` → `{mrs_after:.0f}`" if mrs_before and mrs_after else "- MRS Open：N/A",
                f"- penalty_flags：`{flags}`" if flags else "",
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
        for delta, row, src in worst:
            mrs_before = _to_float(row.get("mrs_open_v031_before"))
            mrs_after = _to_float(row.get("mrs_open_v031_after"))
            pseudo_d = _to_float(row.get("pseudo_delta_mrs"))
            flags = row.get("mrs_open_flags", "") or ""

            lines += [
                f"### {row.get('preset')} / {row.get('sample_id')}",
                "",
                f"- task_id：`{row.get('task_id')}`",
                f"- ΔMRS (open)：`{delta:.1f}` (source: {src})",
                f"- ΔMRS (pseudo)：`{pseudo_d:.1f}`" if pseudo_d is not None else "- ΔMRS (pseudo)：N/A",
                f"- MRS Open：`{mrs_before:.0f}` → `{mrs_after:.0f}`" if mrs_before and mrs_after else "- MRS Open：N/A",
                f"- penalty_flags：`{flags}`" if flags else "",
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
