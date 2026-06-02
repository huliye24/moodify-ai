from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import RuntimeConfig
from .utils import utc_now_iso, write_json


def _read_manifest(path: Path) -> List[Dict[str, str]]:
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


def generate_daily_report(cfg: RuntimeConfig, run_id: Optional[str] = None) -> Dict[str, Any]:
    cfg = cfg.resolved()
    if run_id is None:
        runs = sorted([p for p in cfg.output_root.iterdir() if p.is_dir()]) if cfg.output_root.exists() else []
        if not runs:
            raise FileNotFoundError(f"No run directories in {cfg.output_root}")
        run_dir = runs[-1]
        run_id = run_dir.name
    else:
        run_dir = cfg.output_root / run_id

    rows = _read_manifest(run_dir / "manifest.csv")
    success = [r for r in rows if r.get("status") == "done"]
    failed = [r for r in rows if r.get("status") == "failed"]
    deltas = [_to_float(r.get("pseudo_delta_mrs")) for r in rows]
    deltas = [d for d in deltas if d is not None]

    avg_delta = sum(deltas) / len(deltas) if deltas else None
    best = None
    worst = None
    if deltas:
        best = max(rows, key=lambda r: _to_float(r.get("pseudo_delta_mrs")) if _to_float(r.get("pseudo_delta_mrs")) is not None else -1e9)
        worst = min(rows, key=lambda r: _to_float(r.get("pseudo_delta_mrs")) if _to_float(r.get("pseudo_delta_mrs")) is not None else 1e9)

    report = {
        "run_id": run_id,
        "generated_at": utc_now_iso(),
        "run_dir": str(run_dir),
        "total_tasks": len(rows),
        "success": len(success),
        "failed": len(failed),
        "avg_pseudo_delta_mrs": avg_delta,
        "best_task": best,
        "worst_task": worst,
    }

    md_lines = [
        f"# Moodify Daily Run Report — {run_id}",
        "",
        f"生成时间：{report['generated_at']}",
        "",
        "## 1. 今日运行总览",
        "",
        f"- 总任务数：{len(rows)}",
        f"- 成功任务：{len(success)}",
        f"- 失败任务：{len(failed)}",
        f"- 平均 pseudo ΔMRS：{avg_delta:.4f}" if avg_delta is not None else "- 平均 pseudo ΔMRS：暂无",
        "",
        "说明：`pseudo_mrs_v001` 是 Daily Run v0.1 的占位工程指标，不是正式 MRS。",
        "",
        "## 2. 最佳提升任务",
        "",
    ]

    if best:
        md_lines += [
            f"- task_id：`{best.get('task_id')}`",
            f"- sample_id：`{best.get('sample_id')}`",
            f"- preset：`{best.get('preset')}`",
            f"- pseudo ΔMRS：`{best.get('pseudo_delta_mrs')}`",
            f"- output_dir：`{best.get('output_dir')}`",
            "",
        ]
    else:
        md_lines += ["暂无。", ""]

    md_lines += ["## 3. 最差/需复盘任务", ""]
    if worst:
        md_lines += [
            f"- task_id：`{worst.get('task_id')}`",
            f"- sample_id：`{worst.get('sample_id')}`",
            f"- preset：`{worst.get('preset')}`",
            f"- pseudo ΔMRS：`{worst.get('pseudo_delta_mrs')}`",
            f"- error：`{worst.get('error')}`",
            "",
        ]
    else:
        md_lines += ["暂无。", ""]

    md_lines += [
        "## 4. 失败任务列表",
        "",
    ]
    if failed:
        for r in failed[:50]:
            md_lines += [
                f"- `{r.get('task_id')}` / preset `{r.get('preset')}` / error `{(r.get('error') or '')[:180]}`"
            ]
    else:
        md_lines += ["无失败任务。"]

    md_lines += [
        "",
        "## 5. 明日建议",
        "",
        "- 保留提升稳定的 preset，继续扩大同类样本。",
        "- 对 ΔMRS 下降的样本建立失败案例卡。",
        "- 检查失败任务是否来自 CLI 参数、输出路径或音频格式。",
        "- 用正式 MRS 公式替换 pseudo_mrs_v001。",
        "",
    ]

    cfg.report_dir.mkdir(parents=True, exist_ok=True)
    md_path = cfg.report_dir / f"daily_report_{run_id}.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")
    write_json(cfg.report_dir / f"daily_report_{run_id}.json", report)

    report["markdown_path"] = str(md_path)
    return report
