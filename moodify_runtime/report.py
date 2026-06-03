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

    # 鈹€鈹€ MRS Open v0.3.1 ranking 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
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
        f"# Moodify Daily Run Report 鈥?{run_id}",
        "",
        f"鐢熸垚鏃堕棿锛歿report['generated_at']}",
        "",
        "## 1. 浠婃棩杩愯鎬昏",
        "",
        f"- 鎬讳换鍔℃暟锛歿len(rows)}",
        f"- 鎴愬姛浠诲姟锛歿len(success)}",
        f"- 澶辫触浠诲姟锛歿len(failed)}",
        f"- 骞冲潎 pseudo 螖MRS锛歿avg_delta:.4f}" if avg_delta is not None else "- 骞冲潎 pseudo 螖MRS锛氭殏鏃?,
        f"- MRS Open v0.3.1 鍙敤锛歿len(mrs_open_scored)} 鏍锋湰" if mrs_open_scored else "- MRS Open v0.3.1锛氫笉鍙敤",
        "",
        "璇存槑锛?,
        "- `pseudo_mrs_v001` 鏄?Daily Run v0.1 鐨勫崰浣嶅伐绋嬫寚鏍囥€?,
        "- `mrs_open_v031` 鏄?MRS Open v0.3.1 瀹為獙鎸囨爣锛堝紑鏀惧紡璺戝垎锛屼笉璁句笂闄愶級銆?,
        "",
        "## 2. MRS Open v0.3.1 鈥?Top 10 鐪熷疄搴︽渶楂?,
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
        md_lines += ["MRS Open v0.3.1 涓嶅彲鐢紝璺宠繃銆?, ""]

    md_lines += [
        "## 3. MRS Open v0.3.1 鈥?Top 10 鎻愬崌鏈€澶?(螖MRS)",
        "",
    ]

    if mrs_open_delta_top:
        md_lines += [
            "| Rank | Sample | Preset | 螖 MRS Open | 螖 Pseudo | Before 鈫?After |",
            "|------|--------|--------|------------|----------|-----------------|",
        ]
        for i, r in enumerate(mrs_open_delta_top, 1):
            md_lines.append(
                f"| {i} | {r.get('sample_id')} | {r.get('preset')} | "
                f"{_fmt_float(r.get('delta_mrs_open_v031'))} | "
                f"{_fmt_float(r.get('pseudo_delta_mrs'))} | "
                f"{_fmt_float(r.get('mrs_open_v031_before'), 0)} 鈫?{_fmt_float(r.get('mrs_open_v031_after'), 0)} |"
            )
        md_lines += [""]
    else:
        md_lines += ["MRS Open v0.3.1 涓嶅彲鐢紝璺宠繃銆?, ""]

    md_lines += [
        "## 4. MRS Open v0.3.1 鈥?Bottom 10 (闇€澶嶇洏)",
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
        md_lines += ["MRS Open v0.3.1 涓嶅彲鐢紝璺宠繃銆?, ""]

    md_lines += [
        "## 5. MRS Open Penalty Flags 姹囨€?,
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
        md_lines += ["鏈Е鍙?penalty銆?, ""]

    md_lines += [
        "## 6. 鏈€浣虫彁鍗囦换鍔?(pseudo)",
        "",
    ]
    if best:
        md_lines += [
            f"- task_id锛歚{best.get('task_id')}`",
            f"- sample_id锛歚{best.get('sample_id')}`",
            f"- preset锛歚{best.get('preset')}`",
            f"- pseudo 螖MRS锛歚{best.get('pseudo_delta_mrs')}`",
            f"- output_dir锛歚{best.get('output_dir')}`",
            "",
        ]
    else:
        md_lines += ["鏆傛棤銆?, ""]

    md_lines += ["## 7. 鏈€宸?闇€澶嶇洏浠诲姟 (pseudo)", ""]
    if worst:
        md_lines += [
            f"- task_id锛歚{worst.get('task_id')}`",
            f"- sample_id锛歚{worst.get('sample_id')}`",
            f"- preset锛歚{worst.get('preset')}`",
            f"- pseudo 螖MRS锛歚{worst.get('pseudo_delta_mrs')}`",
            f"- error锛歚{worst.get('error')}`",
            "",
        ]
    else:
        md_lines += ["鏆傛棤銆?, ""]

    md_lines += [
        "## 8. 澶辫触浠诲姟鍒楄〃",
        "",
    ]
    if failed:
        for r in failed[:50]:
            md_lines += [
                f"- `{r.get('task_id')}` / preset `{r.get('preset')}` / error `{(r.get('error') or '')[:180]}`"
            ]
    else:
        md_lines += ["鏃犲け璐ヤ换鍔°€?]

    md_lines += [
        "",
        "## 9. 鏄庢棩寤鸿",
        "",
        "- 淇濈暀鎻愬崌绋冲畾鐨?preset锛岀户缁墿澶у悓绫绘牱鏈€?,
        "- 瀵?螖MRS 涓嬮檷鐨勬牱鏈缓绔嬪け璐ユ渚嬪崱銆?,
        "- 妫€鏌ュけ璐ヤ换鍔℃槸鍚︽潵鑷?CLI 鍙傛暟銆佽緭鍑鸿矾寰勬垨闊抽鏍煎紡銆?,
        "- 浼樺厛鍙傝€?MRS Open ranking 鍋氫汉宸ュ鐩樸€?,
        "- penalty_flags 鈮?'' 鐨勬牱鏈簲浼樺厛鏍囪涓哄緟妫€鏌ャ€?,
        "",
    ]

    cfg.report_dir.mkdir(parents=True, exist_ok=True)
    md_path = cfg.report_dir / f"daily_report_{run_id}.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")
    write_json(cfg.report_dir / f"daily_report_{run_id}.json", report)

    report["markdown_path"] = str(md_path)
    return report
