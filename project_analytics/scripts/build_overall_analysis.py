"""Build a timestamped, source-backed Moodify overall analysis dataset and charts."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import matplotlib.pyplot as plt


TIMEZONE = ZoneInfo("Asia/Shanghai")
STATE_LABELS = {
    "accepted": "已验收",
    "awaiting_acceptance": "待验收",
    "planned": "已规划",
    "not_started": "未开始",
    "unclassified": "未分类",
}
STATE_ORDER = ["accepted", "awaiting_acceptance", "planned", "not_started", "unclassified"]


def setup_chinese_font() -> None:
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS"]
    plt.rcParams["axes.unicode_minus"] = False


def save_bar(labels, values, title, xlabel, output, color="#2F6B8A", percent=False) -> None:
    fig, ax = plt.subplots(figsize=(9.2, 5.2))
    bars = ax.barh(labels, values, color=color, height=0.58)
    ax.invert_yaxis()
    ax.set_title(title, loc="left", fontsize=16, fontweight="bold", pad=16)
    ax.set_xlabel(xlabel)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.grid(axis="x", alpha=0.18)
    maximum = max(values) if values else 1
    for bar, value in zip(bars, values):
        label = f"{value:.1f}%" if percent else f"{value:g}"
        ax.text(value + maximum * 0.02, bar.get_y() + bar.get_height() / 2, label, va="center", fontsize=10)
    ax.set_xlim(0, maximum * 1.18 if maximum else 1)
    fig.tight_layout()
    fig.savefig(output, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--started-at")
    args = parser.parse_args()

    root = args.root.resolve()
    snapshot_path = args.snapshot.resolve()
    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    started = datetime.fromisoformat(args.started_at) if args.started_at else datetime.now(TIMEZONE)
    started = started.astimezone(TIMEZONE)
    timestamp = started.strftime("%Y-%m-%dT%H%M%S%z")
    run_dir = root / "project_analytics" / "runs" / timestamp / "overall-project-analysis"
    if run_dir.exists():
        raise FileExistsError(run_dir)
    charts_dir = run_dir / "charts"
    charts_dir.mkdir(parents=True)

    repo = snapshot["repository"]
    tasks = snapshot["tasks"]
    tests = snapshot["tests"]
    code = snapshot["code_structure"]
    states = {key: int(tasks["states"].get(key, 0)) for key in STATE_ORDER}
    change_areas = repo["change_areas"]
    core_runtime_files = sum(
        item["changed_files"] for item in change_areas
        if item["area"] in {"moodify_runtime", "moodify-core-package"}
    )
    concentration = round(100 * core_runtime_files / repo["changed_tracked_files"], 1) if repo["changed_tracked_files"] else 0.0

    risks = [
        {"risk": "全量测试无法完成收集", "evidence": f"{tests['collection_errors']} 个收集错误，退出码 {tests['exit_code']}", "probability": 5, "impact": 5, "score": 25, "owner": "工程", "treatment": "先恢复导入契约与测试依赖，再以全量绿灯作为合并门禁"},
        {"risk": "任务状态来源冲突", "evidence": f"{tasks['status_source_conflicts']} 处状态冲突", "probability": 4, "impact": 4, "score": 16, "owner": "项目治理", "treatment": "统一 orchestration / handoff / acceptance 的状态优先级"},
        {"risk": "工作区变更未分层", "evidence": f"{repo['modified_tracked_entries']} 个已跟踪修改、{repo['untracked_entries']} 个未跟踪条目", "probability": 4, "impact": 4, "score": 16, "owner": "工程", "treatment": "按产品、测试、文档、生成物分桶并建立可回滚批次"},
        {"risk": "核心改动集中导致回归面扩大", "evidence": f"核心/运行时占已跟踪改动 {concentration}%", "probability": 4, "impact": 5, "score": 20, "owner": "架构", "treatment": "先建立接口契约和回归门禁，再继续扩展核心能力"},
        {"risk": "缺少用户价值与时间投入数据", "evidence": "当前只有工程与治理数据，不能实证收入、留存或体验收益", "probability": 5, "impact": 3, "score": 15, "owner": "产品", "treatment": "建立工时、功能使用、任务成功率与音频质量基线"},
    ]
    investments = [
        {"priority": 1, "initiative": "恢复全量测试收集与基线", "hours_low": 6, "hours_high": 12, "impact_points": 95, "confidence": "中", "risk_reduced": "测试盲区、回归风险", "decision": "立即"},
        {"priority": 2, "initiative": "统一任务状态与验收账本", "hours_low": 2, "hours_high": 4, "impact_points": 55, "confidence": "高", "risk_reduced": "重复工作、错误排期", "decision": "立即"},
        {"priority": 3, "initiative": "工作区分桶与可回滚整理", "hours_low": 3, "hours_high": 6, "impact_points": 65, "confidence": "高", "risk_reduced": "丢失改动、混合提交", "decision": "立即"},
        {"priority": 4, "initiative": "关闭当前关键路径任务包", "hours_low": 4, "hours_high": 8, "impact_points": 70, "confidence": "中", "risk_reduced": "并行在制品、注意力稀释", "decision": "稳定后"},
        {"priority": 5, "initiative": "建立工时与用户价值遥测", "hours_low": 12, "hours_high": 24, "impact_points": 80, "confidence": "中低", "risk_reduced": "ROI 不可观测", "decision": "下一阶段"},
    ]
    for row in investments:
        row["hours_mid"] = (row["hours_low"] + row["hours_high"]) / 2
        row["modeled_roi"] = round(row["impact_points"] / row["hours_mid"], 2)

    metrics = [
        {"metric": "正式任务包", "value": tasks["formal_task_packages"], "unit": "个", "status": "信息", "source": "docs/tasks/deepseek"},
        {"metric": "已开始任务验收率", "value": tasks["accepted_share_of_started_pct"], "unit": "%", "status": "关注", "source": "任务状态文件"},
        {"metric": "测试收集错误", "value": tests["collection_errors"], "unit": "个", "status": "阻断", "source": "pytest --collect-only"},
        {"metric": "已跟踪修改条目", "value": repo["modified_tracked_entries"], "unit": "个", "status": "高", "source": "git status"},
        {"metric": "未跟踪条目", "value": repo["untracked_entries"], "unit": "个", "status": "高", "source": "git status"},
        {"metric": "核心/运行时改动集中度", "value": concentration, "unit": "%", "status": "高", "source": "git diff --numstat"},
        {"metric": "测试/源代码物理行比", "value": code["test_to_source_physical_line_ratio_pct"], "unit": "%", "status": "信息", "source": "tracked Python files"},
        {"metric": "任务状态冲突", "value": tasks["status_source_conflicts"], "unit": "处", "status": "高", "source": "任务治理文件"},
    ]

    analysis = {
        "schema": "moodify.analytics.overall-analysis/0.1",
        "analysis_started_at": started.isoformat(),
        "source_snapshot": snapshot_path.relative_to(root).as_posix(),
        "source_snapshot_started_at": snapshot["started_at"],
        "executive_conclusion": "Moodify 已形成较厚的工程资产，但当前收益受测试门禁失效、任务状态冲突和工作区混杂共同折损。最优策略是短暂停止新增功能，用约 11–22 小时完成前三项稳定化工作，再恢复关键路径开发。",
        "decision": "暂停扩张，先稳定；以全量测试可收集、状态零冲突、工作区完成分桶作为恢复新增功能的三个门槛。",
        "metrics": metrics,
        "task_states": [{"state": key, "label": STATE_LABELS[key], "count": states[key]} for key in STATE_ORDER],
        "tasks": tasks["tasks"],
        "change_areas": change_areas,
        "code_structure": code,
        "test_evidence": tests,
        "repository": repo,
        "risks": risks,
        "investments": investments,
        "limitations": [
            "测试/源代码物理行比不是覆盖率。",
            "未跟踪条目按 git status 条目计数，目录条目可能包含多个文件。",
            "投入工时、影响点与 ROI 为决策模型估算，不是历史实测。",
            "当前没有功能使用、用户留存、音频质量、收入或人工工时数据，因此不能计算财务 ROI。",
        ],
    }
    (run_dir / "analysis_data.json").write_text(json.dumps(analysis, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    setup_chinese_font()
    save_bar(
        [STATE_LABELS[key] for key in STATE_ORDER], [states[key] for key in STATE_ORDER],
        "任务组合：验收完成，但仍有较多待验收与规划项", "任务包数量", charts_dir / "01_task_portfolio.png", "#2F6B8A"
    )
    top_areas = change_areas[:8]
    save_bar(
        [item["area"] for item in top_areas], [item["changed_files"] for item in top_areas],
        "已跟踪改动集中在核心与运行时", "改动文件数", charts_dir / "02_change_concentration.png", "#C66A3D"
    )
    save_bar(
        ["Python 源文件", "Python 测试文件"], [code["python_source_files"], code["python_test_files"]],
        "代码结构：测试资产规模可观，但不等于可执行可信度", "文件数", charts_dir / "03_code_structure_files.png", "#4A8C74"
    )
    save_bar(
        ["收集到的测试", "收集错误", "任务状态冲突"],
        [tests["tests_collected"], tests["collection_errors"], tasks["status_source_conflicts"]],
        "可信度证据：测试资产大，但全量门禁被收集错误阻断", "数量（不同口径，仅作并列展示）", charts_dir / "04_trust_evidence.png", "#8A5A83"
    )
    save_bar(
        [row["initiative"] for row in investments], [row["modeled_roi"] for row in investments],
        "稳定化投入的模型回报：先治理，再扩张", "影响点 / 估算小时中位数（模型值）", charts_dir / "05_modeled_roi.png", "#B28B35"
    )
    print(run_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
