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


def _fmt_float(x: Any, digits: int = 1) -> str:
    value = _to_float(x)
    if value is None:
        return "-"
    return f"{value:.{digits}f}"


def generate_daily_report(cfg: RuntimeConfig, run_id: Optional[str] = None) -> Dict[str, Any]:
    cfg = cfg.resolved()
    if run_id is None:
        from .utils import find_latest_run_dir
        run_dir = find_latest_run_dir(cfg.output_root)
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

    # ── MRS Open v0.3.1 ranking ─────────────────────────
    mrs_open_scored = [
        r for r in rows
        if _to_float(r.get("mrs_open_v031_after")) is not None
    ]
    mrs_open_top = sorted(mrs_open_scored,
                          key=lambda r: _to_float(r.get("mrs_open_v031_after")),
                          reverse=True)[:10]
    mrs_open_delta_top = sorted(mrs_open_scored,
                                 key=lambda r: _to_float(r.get("delta_mrs_open_v031")),
                                 reverse=True)[:10]
    mrs_open_bottom = sorted(mrs_open_scored,
                              key=lambda r: _to_float(r.get("mrs_open_v031_after")))[:10]

    # Penalty flags summary
    penalty_counts: Dict[str, int] = {}
    for r in rows:
        flags_str = r.get("mrs_open_flags", "") or ""
        for flag in flags_str.split(","):
            flag = flag.strip()
            if flag:
                penalty_counts[flag] = penalty_counts.get(flag, 0) + 1

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
        "mrs_open_available": len(mrs_open_scored) > 0,
        "mrs_open_penalty_summary": penalty_counts,
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
        f"- MRS Open v0.3.1 可用：{len(mrs_open_scored)} 样本" if mrs_open_scored else "- MRS Open v0.3.1：不可用",
        "",
        "说明：",
        "- `pseudo_mrs_v001` 是 Daily Run v0.1 的占位工程指标。",
        "- `mrs_open_v031` 是 MRS Open v0.3.1 实验指标（开放式跑分，不设上限）。",
        "",
        "## 2. MRS Open v0.3.1 — Top 10 真实度最高",
        "",
    ]

    if mrs_open_top:
        md_lines += [
            "| Rank | Sample | Preset | MRS Open After | Pseudo After | Flags |",
            "|------|--------|--------|----------------|--------------|-------|",
        ]
        for i, r in enumerate(mrs_open_top, 1):
            flags = (r.get("mrs_open_flags") or "-")[:30]
            md_lines.append(
                f"| {i} | {r.get('sample_id')} | {r.get('preset')} | "
                f"{_fmt_float(r.get('mrs_open_v031_after'))} | "
                f"{_fmt_float(r.get('pseudo_mrs_after'))} | "
                f"{flags} |"
            )
        md_lines += [""]
    else:
        md_lines += ["MRS Open v0.3.1 不可用，跳过。", ""]

    md_lines += [
        "## 3. MRS Open v0.3.1 — Top 10 提升最大 (ΔMRS)",
        "",
    ]

    if mrs_open_delta_top:
        md_lines += [
            "| Rank | Sample | Preset | Δ MRS Open | Δ Pseudo | Before → After |",
            "|------|--------|--------|------------|----------|-----------------|",
        ]
        for i, r in enumerate(mrs_open_delta_top, 1):
            md_lines.append(
                f"| {i} | {r.get('sample_id')} | {r.get('preset')} | "
                f"{_fmt_float(r.get('delta_mrs_open_v031'))} | "
                f"{_fmt_float(r.get('pseudo_delta_mrs'))} | "
                f"{_fmt_float(r.get('mrs_open_v031_before'), 0)} → {_fmt_float(r.get('mrs_open_v031_after'), 0)} |"
            )
        md_lines += [""]
    else:
        md_lines += ["MRS Open v0.3.1 不可用，跳过。", ""]

    md_lines += [
        "## 4. MRS Open v0.3.1 — Bottom 10 (需复盘)",
        "",
    ]

    if mrs_open_bottom:
        md_lines += [
            "| Rank | Sample | Preset | MRS Open After | Pseudo After | Flags |",
            "|------|--------|--------|----------------|--------------|-------|",
        ]
        for i, r in enumerate(mrs_open_bottom, 1):
            flags = (r.get("mrs_open_flags") or "-")[:40]
            md_lines.append(
                f"| {i} | {r.get('sample_id')} | {r.get('preset')} | "
                f"{_fmt_float(r.get('mrs_open_v031_after'))} | "
                f"{_fmt_float(r.get('pseudo_mrs_after'))} | "
                f"{flags} |"
            )
        md_lines += [""]
    else:
        md_lines += ["MRS Open v0.3.1 不可用，跳过。", ""]

    md_lines += [
        "## 5. MRS Open Penalty Flags 汇总",
        "",
    ]
    if penalty_counts:
        md_lines += [
            "| Penalty Flag | Count |",
            "|-------------|-------|",
        ]
        for flag, count in sorted(penalty_counts.items(), key=lambda x: x[1], reverse=True):
            md_lines.append(f"| {flag} | {count} |")
        md_lines += [""]
    else:
        md_lines += ["未触发 penalty。", ""]

    md_lines += [
        "## 6. 最佳提升任务 (pseudo)",
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

    md_lines += ["## 7. 最差/需复盘任务 (pseudo)", ""]
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
        "## 8. 失败任务列表",
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
        "## 9. 明日建议",
        "",
        "- 保留提升稳定的 preset，继续扩大同类样本。",
        "- 对 ΔMRS 下降的样本建立失败案例卡。",
        "- 检查失败任务是否来自 CLI 参数、输出路径或音频格式。",
        "- 优先参考 MRS Open ranking 做人工复盘。",
        "- penalty_flags ≠ '' 的样本应优先标记为待检查。",
        "",
    ]

    cfg.report_dir.mkdir(parents=True, exist_ok=True)
    md_path = cfg.report_dir / f"daily_report_{run_id}.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")
    write_json(cfg.report_dir / f"daily_report_{run_id}.json", report)

    report["markdown_path"] = str(md_path)
    return report
