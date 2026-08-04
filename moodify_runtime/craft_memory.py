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
        from .utils import find_latest_run_dir
        run_dir = find_latest_run_dir(cfg.output_root)
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

    seed_dir = cfg.craft_memory_dir / "seed_proposals"
    seed_dir.mkdir(parents=True, exist_ok=True)
    path = seed_dir / f"craft_memory_seed_{run_id}.md"

    metric_label = "MRS Open v0.3.1" if mrs_open_used else "pseudo MRS v001"

    lines = [
        f"# [PROPOSAL] Moodify Craft Memory Seed — {run_id}",
        "",
        f"生成时间：{utc_now_iso()}",
        f"排序指标：{metric_label}",
        "",
        "> **状态：PROPOSAL** — 这是 Daily Run 自动生成的工艺记忆种子文件，存放在 `seed_proposals/` 提案命名空间。",
        "> 它不是最终结论，也不是已批准的工艺知识。必须经过人工复盘和显式 promotion 后才能进入正式 Craft Library。",
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


# ── MHP-037: Craft Library Writeback ────────────────────────────────
CRAFT_STATUSES = {"experimental", "candidate", "stable", "adopted"}


def writeback_delivery_to_craft_record(
    cfg: RuntimeConfig,
    job_id: str,
    candidate_id: str,
    adoption_status: str = "candidate",
    operator_notes: str = "",
) -> Dict[str, Any]:
    """Create a Craft Record from a delivered job's candidate.

    Records the processing chain, MRS statistics, risk conditions, and lineage.
    The adoption_status flows: experimental → candidate → stable → adopted.
    """
    import uuid

    from .operator_console import get_delivery_record, get_operator_job, get_operator_job_detail

    if adoption_status not in CRAFT_STATUSES:
        raise ValueError(f"adoption_status must be one of {sorted(CRAFT_STATUSES)}")

    cfg = cfg.resolved()
    job = get_operator_job(cfg, job_id)
    detail_data = get_operator_job_detail(cfg, job_id)
    detail = detail_data.get("detail", {})

    candidates = detail.get("candidate_versions", [])
    scores = detail.get("score_results", [])
    gates = detail.get("gate_decisions", [])

    candidate = next((c for c in candidates if c.get("candidate_id") == candidate_id), None)
    if not candidate:
        raise ValueError(f"candidate_id={candidate_id!r} not found in job detail")

    score = next((s for s in scores if s.get("candidate_id") == candidate_id), {})
    gate = next((g for g in gates if g.get("candidate_id") == candidate_id), {})
    if gate.get("decision") != "approve":
        raise ValueError("Craft writeback requires an approved technical gate decision")

    delivery = get_delivery_record(cfg, job_id)
    if not delivery or delivery.get("candidate_id") != candidate_id:
        raise ValueError("Craft writeback requires a matching delivery record")
    if not delivery.get("human_approved") or not delivery.get("approved_by"):
        raise ValueError("Craft writeback requires recorded human listening approval")
    if not delivery.get("rights_manifest") or not delivery.get("rights_asset_id"):
        raise ValueError("Craft writeback requires recorded rights evidence")

    craft_id = f"CRFT_{uuid.uuid4().hex[:12].upper()}"
    now = utc_now_iso()

    record = {
        "craft_id": craft_id,
        "source_job_id": job_id,
        "source_candidate_id": candidate_id,
        "audio_class": job.get("project_label", ""),
        "preset": candidate.get("preset", ""),
        "processing_chain": candidate.get("processing_chain", candidate.get("preset", "")),
        "expected_improvement": f"MRS Δ={score.get('mrs_score_delta')}",
        "mrs_score": score.get("mrs_score"),
        "mrs_score_delta": score.get("mrs_score_delta"),
        "risk_conditions": {
            "over_dark_triggered": score.get("over_dark_triggered", False),
            "transient_damage": score.get("transient_damage"),
            "loudness_penalty": score.get("loudness_penalty"),
        },
        "gate_decision": gate.get("decision", "unknown"),
        "failure_cases": [r for r in gate.get("reasons", []) if r != "all_gates_passed"],
        "operator_notes": operator_notes,
        "human_approval": {
            "approved_by": delivery["approved_by"],
            "delivery_id": delivery["delivery_id"],
        },
        "rights_evidence": {
            "manifest": delivery["rights_manifest"],
            "asset_id": delivery["rights_asset_id"],
        },
        "adoption_status": adoption_status,
        "version_history": [{"status": adoption_status, "at": now, "note": "initial writeback"}],
        "output_path": candidate.get("output_path", ""),
        "created_at": now,
        "updated_at": now,
    }

    craft_path = cfg.craft_memory_dir / "craft_records.jsonl"
    craft_path.parent.mkdir(parents=True, exist_ok=True)
    from .utils import append_jsonl

    append_jsonl(craft_path, record)

    return record


def list_craft_records(
    cfg: RuntimeConfig, adoption_status: Optional[str] = None, include_proposals: bool = False
) -> list[Dict[str, Any]]:
    """List craft records, optionally filtered by adoption status.

    Records with status ``proposal`` or ``pending`` are excluded by default.
    These statuses belong to the proposal namespace and must not appear as
    reusable approved Craft knowledge without explicit promotion.
    """
    from .utils import read_jsonl

    cfg = cfg.resolved()
    path = cfg.craft_memory_dir / "craft_records.jsonl"
    rows = read_jsonl(path)
    if not include_proposals:
        rows = [r for r in rows if r.get("adoption_status") not in ("proposal", "pending")]
    if adoption_status:
        rows = [r for r in rows if r.get("adoption_status") == adoption_status]
    return sorted(rows, key=lambda r: r.get("created_at", ""), reverse=True)
