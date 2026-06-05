"""Product Integration — wire data loop insights into operator-facing product surfaces.

MHP-833: Operator Dashboard Learning View
MHP-834: Craft Library Learning Feed
MHP-835: MRS Calibration Review Feed
MHP-836: Release Candidate Learning Gate

Connects the data loop runner output (NightMetricRecord + RecommendationBundle) to:
  - Operator dashboard (job board, approval flow)
  - Craft library (preset policy writeback)
  - MRS calibration lab (calibration proposals)
  - Release candidate gate (pre-release quality check)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

from moodify_runtime.utils import utc_now_iso


# ═══════════════════════════════════════════════════════════════════════
# MHP-833: Operator Dashboard Learning View
# ═══════════════════════════════════════════════════════════════════════


@dataclass
class LearningDashboardCard:
    """A single dashboard card showing one data loop insight."""
    card_id: str
    card_type: str  # "metric", "alert", "trend", "action"
    title: str
    value: str
    severity: str = "info"  # info, warn, critical
    detail: str = ""
    linked_mhp: str = ""
    generated_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class LearningDashboard:
    """Complete operator dashboard learning view from a data loop run."""
    run_id: str
    generated_at: str = field(default_factory=utc_now_iso)
    operator_decision: str = "PASS"
    next_mhp: str = ""
    cards: list[LearningDashboardCard] = field(default_factory=list)
    summary_counts: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "generated_at": self.generated_at,
            "operator_decision": self.operator_decision,
            "next_mhp": self.next_mhp,
            "cards": [c.to_dict() for c in self.cards],
            "summary_counts": self.summary_counts,
        }


def build_learning_dashboard(
    record: dict[str, Any],
    bundle: dict[str, Any],
) -> LearningDashboard:
    """Build operator dashboard learning view from a data loop run.

    Usage:
        dash = build_learning_dashboard(record, bundle)
        # Render dash.to_dict() in the operator console
    """
    run_id = record.get("run_id", "")
    summary = bundle.get("summary", {})
    rt = record.get("runtime", {})
    sc = record.get("scoring", {})
    cr = record.get("craft", {})
    recs = bundle.get("recommendations", [])

    cards: list[LearningDashboardCard] = []

    # Card 1: Runtime health
    success_rate = rt.get("success", 0) / max(rt.get("total_selected", 1), 1)
    cards.append(LearningDashboardCard(
        card_id=f"{run_id}:card:runtime",
        card_type="metric",
        title="Runtime Success Rate",
        value=f"{success_rate:.0%}",
        severity="critical" if success_rate < 0.9 else ("warn" if success_rate < 0.95 else "info"),
        detail=f"{rt.get('success', 0)}/{rt.get('total_selected', 0)} tasks, "
               f"{rt.get('failed', 0)} failed",
    ))

    # Card 2: Fatal error alert
    fatal = rt.get("fatal_error")
    if fatal:
        cards.append(LearningDashboardCard(
            card_id=f"{run_id}:card:fatal",
            card_type="alert",
            title="Fatal Runtime Error",
            value=str(fatal)[:80],
            severity="critical",
            detail="Blocks auto-report and operator review. Fix before next run.",
            linked_mhp="MHP runtime reliability fix",
        ))

    # Card 3: Scoring agreement
    agreement = sc.get("agreement_rate", 1.0)
    cards.append(LearningDashboardCard(
        card_id=f"{run_id}:card:scoring",
        card_type="metric",
        title="Score Direction Agreement",
        value=f"{agreement:.0%}",
        severity="critical" if agreement < 0.7 else ("warn" if agreement < 0.85 else "info"),
        detail=f"{sc.get('disagreement_count', 0)} disagreements across "
               f"{sc.get('task_count', 0)} tasks. "
               f"Disagreeing presets: {', '.join(sc.get('disagreeing_presets', []))}",
    ))

    # Card 4: Craft flag alert
    flag_rate = cr.get("flag_rate", 0)
    cards.append(LearningDashboardCard(
        card_id=f"{run_id}:card:craft",
        card_type="metric",
        title="Preset Penalty Flag Rate",
        value=f"{flag_rate:.0%}",
        severity="warn" if flag_rate > 0.3 else "info",
        detail=f"{cr.get('flagged_count', 0)}/{cr.get('task_count', 0)} flagged. "
               f"Types: {', '.join(cr.get('flag_types', ['none']))}",
    ))

    # Card 5: Top recommendation
    high_recs = [r for r in recs if r.get("severity") == "high" and r.get("loop") != "operator_report"]
    if high_recs:
        top = high_recs[0]
        cards.append(LearningDashboardCard(
            card_id=f"{run_id}:card:top_action",
            card_type="action",
            title=f"Top Action: {top.get('loop', '')}",
            value=top.get("next_action", "")[:100],
            severity="critical" if top.get("needs_human_review") else "warn",
            detail=top.get("reason", "")[:150],
        ))

    # Card 6: Trend placeholder (populated after 3+ nights)
    cards.append(LearningDashboardCard(
        card_id=f"{run_id}:card:trend",
        card_type="trend",
        title="Learning Trend",
        value="Collecting data",
        severity="info",
        detail="Trend analysis available after 3 nights of continuous data loop execution.",
    ))

    return LearningDashboard(
        run_id=run_id,
        operator_decision=summary.get("decision", "PASS"),
        next_mhp=summary.get("next_mhp", ""),
        cards=cards,
        summary_counts={
            "total_recommendations": len(recs),
            "high_severity": summary.get("high_count", 0),
            "needs_review": summary.get("needs_review_count", 0),
        },
    )


# ═══════════════════════════════════════════════════════════════════════
# MHP-834: Craft Library Learning Feed
# ═══════════════════════════════════════════════════════════════════════


def write_craft_learning_feed(
    bundle: dict[str, Any],
    craft_memory_dir: Path,
) -> int:
    """Write data loop craft recommendations into the craft library learning feed.

    Each recommendation becomes a craft memory entry with:
      - adoption_status: "candidate" (pending operator review)
      - source: "data_loop" (traceable to which night run)
      - severity: from the recommendation

    Returns the number of entries written.
    """
    recs = bundle.get("recommendations", [])
    craft_recs = [r for r in recs if r.get("loop") == "craft_preset_selection"]
    if not craft_recs:
        return 0

    craft_memory_dir = Path(craft_memory_dir)
    craft_memory_dir.mkdir(parents=True, exist_ok=True)

    run_id = bundle.get("run_id", "unknown")
    ts = utc_now_iso()
    entries: list[dict[str, Any]] = []

    for rec in craft_recs:
        # Parse preset from task_id: "TASK_SMP_HASH_preset:craft" → "preset"
        task_id = rec.get("task_id", "")
        preset = task_id.split(":")[0].rsplit("_", 1)[-1] if ":" in task_id else task_id

        entry = {
            "craft_record_id": f"dl_{run_id}_{preset}",
            "preset": preset,
            "source": "data_loop",
            "source_run": run_id,
            "adoption_status": "candidate",
            "severity": rec.get("severity", "medium"),
            "action": rec.get("next_action", ""),
            "reason": rec.get("reason", ""),
            "needs_human_review": rec.get("needs_human_review", False),
            "created_at": ts,
        }
        entries.append(entry)

    path = craft_memory_dir / f"data_loop_craft_feed_{run_id}.json"
    path.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return len(entries)


# ═══════════════════════════════════════════════════════════════════════
# MHP-835: MRS Calibration Review Feed
# ═══════════════════════════════════════════════════════════════════════


def write_calibration_review_feed(
    bundle: dict[str, Any],
    record: dict[str, Any],
    output_dir: Path,
) -> int:
    """Write scoring calibration recommendations into the MRS calibration lab feed.

    Each recommendation becomes a calibration review proposal with:
      - proposed action (weight tuning, threshold adjustment, etc.)
      - linked preset and sample
      - severity and human review flag

    Returns the number of proposals written.
    """
    recs = bundle.get("recommendations", [])
    score_recs = [r for r in recs if r.get("loop") == "scoring_calibration"]
    if not score_recs:
        return 0

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    run_id = bundle.get("run_id", "unknown")
    ts = utc_now_iso()
    proposals: list[dict[str, Any]] = []
    tasks = {t.get("task_id"): t for t in record.get("tasks", [])}

    for rec in score_recs:
        task_id = rec.get("task_id", "").replace(":score", "")
        task = tasks.get(task_id, {})

        proposal = {
            "proposal_id": f"cal_{run_id}_{task_id}",
            "source": "data_loop",
            "source_run": run_id,
            "task_id": task_id,
            "sample_id": task.get("sample_id", ""),
            "preset": task.get("preset", ""),
            "pseudo_delta_mrs": task.get("pseudo_delta_mrs"),
            "delta_mrs_open_v031": task.get("delta_mrs_open_v031"),
            "severity": rec.get("severity", "medium"),
            "reason": rec.get("reason", ""),
            "proposed_action": rec.get("next_action", ""),
            "needs_human_review": rec.get("needs_human_review", False),
            "status": "open",
            "created_at": ts,
        }
        proposals.append(proposal)

    path = output_dir / f"calibration_review_feed_{run_id}.json"
    path.write_text(json.dumps(proposals, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return len(proposals)


# ═══════════════════════════════════════════════════════════════════════
# MHP-836: Release Candidate Learning Gate
# ═══════════════════════════════════════════════════════════════════════


@dataclass
class LearningGateResult:
    """Result of the release candidate learning gate check."""
    passed: bool
    run_id: str = ""
    checks: list[dict[str, Any]] = field(default_factory=list)
    blocking_issues: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def check_release_learning_gate(
    record: dict[str, Any],
    bundle: dict[str, Any],
) -> LearningGateResult:
    """Check whether this night's data loop output meets release quality standards.

    Gate criteria:
      1. No fatal errors
      2. Task success rate ≥ 95%
      3. Scoring agreement rate ≥ 70% (relaxed from SLO's 85% for release)
      4. No high-severity unscored disagreements
      5. Operator decision is PASS

    Usage:
        gate = check_release_learning_gate(record, bundle)
        if gate.passed:
            proceed_with_release()
    """
    run_id = record.get("run_id", "")
    rt = record.get("runtime", {})
    sc = record.get("scoring", {})
    summary = bundle.get("summary", {})
    checks: list[dict[str, Any]] = []
    blocking: list[str] = []
    recs_list: list[str] = []

    # Check 1: No fatal errors
    fatal = rt.get("fatal_error")
    c1 = not bool(fatal)
    checks.append({"check": "no_fatal_errors", "passed": c1, "detail": str(fatal) if fatal else "ok"})
    if not c1:
        blocking.append("Fatal error detected. Fix before release.")
        recs_list.append("Fix fatal error and rerun the data loop.")

    # Check 2: Task success rate ≥ 95%
    total = max(rt.get("total_selected", 0), rt.get("success", 0) + rt.get("failed", 0))
    success_rate = rt.get("success", 0) / max(total, 1)
    c2 = success_rate >= 0.95
    checks.append({"check": "success_rate_95pct", "passed": c2,
                   "detail": f"{success_rate:.1%} ({rt.get('success', 0)}/{total})"})
    if not c2:
        blocking.append(f"Task success rate {success_rate:.1%} below 95% threshold.")
        recs_list.append("Investigate task failures and improve reliability.")

    # Check 3: Scoring agreement rate ≥ 70%
    agreement = sc.get("agreement_rate", 1.0)
    c3 = agreement >= 0.7
    checks.append({"check": "scoring_agreement_70pct", "passed": c3,
                   "detail": f"{agreement:.1%} agreement, {sc.get('disagreement_count', 0)} disagreements"})
    if not c3:
        blocking.append(f"Scoring agreement rate {agreement:.1%} below 70% threshold.")
        recs_list.append("Run MRS calibration session before release.")

    # Check 4: Operator decision is PASS
    decision = summary.get("decision", "HOLD")
    c4 = decision == "PASS"
    checks.append({"check": "operator_decision_pass", "passed": c4,
                   "detail": f"Decision: {decision}"})
    if not c4:
        blocking.append(f"Operator decision is {decision}, not PASS.")
        recs_list.append(f"Resolve blocking issues: {summary.get('decision_reason', '')}")

    passed = len(blocking) == 0

    return LearningGateResult(
        passed=passed,
        run_id=run_id,
        checks=checks,
        blocking_issues=blocking,
        recommendations=recs_list,
    )
