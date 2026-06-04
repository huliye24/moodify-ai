"""Tidal Intelligence — adaptive cycle decision engine.

ECHAIN-MOODIFY-TIDAL-INTELLIGENCE-009 / NEM-027/028/029.
MHP-539: Evidence Scorer
MHP-540: Task Priority Model
MHP-541: Adaptive Queue Planner
MHP-542: Gate Decision Writer
MHP-543: Morning Brief Generator
MHP-546: Anti-Loop Guardrail
MHP-547: Craft Feedback Selector
MHP-548: MRS/CT Evidence Synthesizer
MHP-549: Config Profiles
MHP-550: Integration Smoke
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ═══════════════════════════════════════════════════════════════════════════
# MHP-539: Evidence Scorer — per-source scoring with weighted confidence
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class EvidenceScore:
    """A scored piece of evidence from one E-Chain source."""
    source: str
    weight: float = 1.0
    score: float = 0.0
    confidence: float = 0.5
    fresh: bool = True
    details: Dict[str, Any] = field(default_factory=dict)

    @property
    def weighted_score(self) -> float:
        return self.score * self.weight * self.confidence

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def score_mrs_evidence(data: Optional[Dict[str, Any]] = None) -> EvidenceScore:
    if data is None:
        return EvidenceScore(source="mrs", weight=1.0, score=0.0, confidence=0.0,
                             details={"status": "no_data"})
    ga = data.get("gate_accuracy", 0.0)
    od = data.get("over_dark_level", "none")
    sc = min(1.0, ga * 0.8 + (0.2 if od == "none" else 0.05))
    return EvidenceScore(source="mrs", weight=1.0, score=sc,
                         confidence=min(1.0, data.get("sample_count", 0) / 50),
                         details=data)


def score_ct_evidence(findings: Optional[List[Dict[str, Any]]] = None) -> EvidenceScore:
    if not findings:
        return EvidenceScore(source="ct", weight=0.8, score=0.0, confidence=0.0,
                             details={"status": "no_data"})
    issues = sum(1 for f in findings if f.get("severity", "info") in ("critical", "warn"))
    total = len(findings)
    sc = max(0.0, 1.0 - (issues / max(total, 1)) * 0.8)
    return EvidenceScore(source="ct", weight=0.8, score=sc,
                         confidence=min(1.0, total / 10),
                         details={"findings": total, "issues": issues})


def score_runtime_evidence(record: Optional[Dict[str, Any]] = None) -> EvidenceScore:
    if record is None:
        return EvidenceScore(source="runtime", weight=0.6, score=0.0, confidence=0.0,
                             details={"status": "no_data"})
    ok = record.get("tasks_succeeded", 0)
    total = record.get("tasks_processed", 1)
    rate = ok / max(total, 1)
    crashed = record.get("crashed", False)
    sc = rate * (0.3 if crashed else 1.0)
    return EvidenceScore(source="runtime", weight=0.6, score=sc,
                         confidence=min(1.0, total / 20),
                         details={"success_rate": round(rate, 3), "total": total})


def score_listening_evidence(data: Optional[Dict[str, Any]] = None) -> EvidenceScore:
    if data is None:
        return EvidenceScore(source="listening", weight=0.7, score=0.0, confidence=0.0,
                             details={"status": "no_data"})
    ag = data.get("reviewer_agreement", 0.0)
    return EvidenceScore(source="listening", weight=0.7, score=min(1.0, ag * 1.2),
                         confidence=min(1.0, data.get("samples_reviewed", 0) / 20),
                         details=data)


def score_craft_evidence(data: Optional[Dict[str, Any]] = None) -> EvidenceScore:
    if data is None:
        return EvidenceScore(source="craft", weight=0.5, score=0.0, confidence=0.0,
                             details={"status": "no_data"})
    adopted = data.get("adopted_count", 0)
    total = data.get("total_count", 1)
    return EvidenceScore(source="craft", weight=0.5, score=min(1.0, adopted / max(total, 1)),
                         confidence=min(1.0, total / 30), details=data)


def score_all_evidence(
    mrs: Optional[Dict] = None, ct: Optional[List[Dict]] = None,
    runtime: Optional[Dict] = None, listening: Optional[Dict] = None,
    craft: Optional[Dict] = None,
) -> List[EvidenceScore]:
    scores = [score_mrs_evidence(mrs), score_ct_evidence(ct),
              score_runtime_evidence(runtime), score_listening_evidence(listening),
              score_craft_evidence(craft)]
    scores.sort(key=lambda s: s.weighted_score, reverse=True)
    return scores


# ═══════════════════════════════════════════════════════════════════════════
# MHP-540: Task Priority Model
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class TaskPriority:
    task_id: str
    base_priority: float = 0.5
    value_score: float = 0.5
    urgency: float = 0.5
    evidence_boost: float = 0.0
    risk_penalty: float = 0.0
    final_priority: float = 0.5
    depends_on: List[str] = field(default_factory=list)
    blocks: List[str] = field(default_factory=list)
    estimated_cost_s: float = 60.0
    genre: str = ""
    preset: str = ""

    def compute(self, evidence: Optional[List[EvidenceScore]] = None) -> float:
        eb = 0.0
        if evidence:
            eb = sum(e.weighted_score for e in evidence) / max(len(evidence), 1)
        self.evidence_boost = eb * 0.15
        self.final_priority = round(min(1.0, max(0.0,
            self.base_priority * 0.30 + self.value_score * 0.25 +
            self.urgency * 0.25 + self.evidence_boost - self.risk_penalty)), 3)
        return self.final_priority

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def rank_tasks(
    tasks: List[Dict[str, Any]],
    evidence: Optional[List[EvidenceScore]] = None,
) -> List[TaskPriority]:
    ranked = []
    for t in tasks:
        tp = TaskPriority(
            task_id=t.get("id", f"task-{len(ranked)}"),
            base_priority=t.get("base_priority", 0.5),
            value_score=t.get("value_score", 0.5),
            urgency=t.get("urgency", 0.5),
            risk_penalty=t.get("risk_penalty", 0.0),
            depends_on=t.get("depends_on", []),
            blocks=t.get("blocks", []),
            estimated_cost_s=t.get("estimated_cost_s", 60.0),
            genre=t.get("genre", ""), preset=t.get("preset", ""))
        tp.compute(evidence)
        ranked.append(tp)
    ranked.sort(key=lambda r: r.final_priority, reverse=True)
    return ranked


# ═══════════════════════════════════════════════════════════════════════════
# MHP-541: Adaptive Queue Planner
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class AdaptivePlan:
    plan_id: str = ""
    created_at: str = field(default_factory=_utc_now)
    tasks: List[TaskPriority] = field(default_factory=list)
    max_concurrent: int = 3
    estimated_total_s: float = 0.0
    evidence_summary: str = ""
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def plan_adaptive_queue(
    tasks: List[Dict[str, Any]],
    evidence: Optional[List[EvidenceScore]] = None,
    max_concurrent: int = 3,
    budget_s: float = 3600.0,
    dry_run: bool = False,
) -> AdaptivePlan:
    plan = AdaptivePlan(plan_id=f"ADAPT_{_utc_now().replace(':','-')}",
                        max_concurrent=max_concurrent)
    if evidence is None:
        evidence = []
    parts = [f"{e.source}={e.score:.2f}" for e in evidence if e.score > 0]
    plan.evidence_summary = ", ".join(parts) if parts else "no evidence"

    ranked = rank_tasks(tasks, evidence)
    elapsed = 0.0
    selected: set = set()
    for r in ranked:
        if elapsed + r.estimated_cost_s > budget_s:
            plan.warnings.append(f"Budget exceeded: {r.task_id}")
            continue
        blocked = [d for d in r.depends_on if d not in selected]
        if blocked:
            plan.warnings.append(f"Blocked {r.task_id}: waiting on {blocked}")
            continue
        plan.tasks.append(r)
        selected.add(r.task_id)
        elapsed += r.estimated_cost_s
    plan.estimated_total_s = round(elapsed, 1)
    if dry_run:
        plan.warnings.insert(0, "DRY-RUN: no tasks executed")
    return plan


# ═══════════════════════════════════════════════════════════════════════════
# MHP-542: Gate Decision Writer
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class GateDecision:
    gate_id: str
    target: str
    decision: str = "HOLD"
    confidence: float = 0.0
    evidence_scores: List[EvidenceScore] = field(default_factory=list)
    conditions: List[str] = field(default_factory=list)
    reopen_criteria: List[str] = field(default_factory=list)
    reviewer: str = "tidal-intelligence"
    decided_at: str = field(default_factory=_utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_report(self) -> str:
        lines = [f"# Gate Decision: {self.gate_id}",
                 f"**Target**: {self.target}",
                 f"**Decision**: {self.decision}  (confidence: {self.confidence:.2f})",
                 f"**Reviewer**: {self.reviewer}",
                 f"**Decided**: {self.decided_at}", "", "## Evidence"]
        for e in self.evidence_scores:
            lines.append(f"- {e.source}: score={e.score:.2f} conf={e.confidence:.2f}")
        if self.conditions:
            lines.append(""); lines.append("## Conditions")
            for c in self.conditions:
                lines.append(f"- [ ] {c}")
        if self.reopen_criteria:
            lines.append(""); lines.append("## Reopen Criteria")
            for r in self.reopen_criteria:
                lines.append(f"- {r}")
        return "\n".join(lines)


def decide_gate(
    target: str, evidence: Optional[List[EvidenceScore]] = None,
    required_sources: Optional[List[str]] = None, min_confidence: float = 0.3,
) -> GateDecision:
    gid = f"GATE-TIDAL-{_utc_now().replace(':','-')[:16]}"
    d = GateDecision(gate_id=gid, target=target,
                     evidence_scores=evidence or [])
    if not evidence:
        d.decision = "HOLD"
        d.conditions.append("No evidence — run at least one cycle")
        return d
    if required_sources:
        present = {e.source for e in evidence}
        missing = [s for s in required_sources if s not in present]
        if missing:
            d.decision = "HOLD"
            d.conditions.append(f"Missing: {missing}")
            return d
    avg = sum(e.weighted_score for e in evidence) / max(len(evidence), 1)
    avg_conf = sum(e.confidence for e in evidence) / max(len(evidence), 1)
    d.confidence = round(avg_conf, 2)
    high = sum(1 for e in evidence if e.weighted_score >= 0.5)
    low = sum(1 for e in evidence if e.weighted_score < 0.2)
    if high == len(evidence) and avg_conf >= min_confidence:
        d.decision = "ADOPT"
    elif high >= len(evidence) / 2:
        d.decision = "PASS"
    elif low >= len(evidence) / 2:
        d.decision = "FAIL"
        d.conditions.append("Evidence scores consistently low")
    else:
        d.decision = "HOLD"
        d.conditions.append("Mixed or insufficient evidence")
    if avg_conf < min_confidence:
        d.conditions.append(f"Confidence {avg_conf:.2f} < {min_confidence}")
    return d


# ═══════════════════════════════════════════════════════════════════════════
# MHP-543: Morning Brief Generator
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class MorningBrief:
    brief_id: str = ""
    generated_at: str = field(default_factory=_utc_now)
    date: str = ""
    cycles_completed: int = 0
    tasks_total: int = 0
    tasks_succeeded: int = 0
    tasks_failed: int = 0
    gate_decisions: List[str] = field(default_factory=list)
    top_priorities: List[Dict[str, Any]] = field(default_factory=list)
    evidence_health: Dict[str, float] = field(default_factory=dict)
    alerts: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    next_actions: List[str] = field(default_factory=list)
    raw_markdown: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def generate_morning_brief(
    cycle_results: List[Dict[str, Any]],
    ranked_tasks: Optional[List[TaskPriority]] = None,
    gate_decisions: Optional[List[GateDecision]] = None,
    evidence: Optional[List[EvidenceScore]] = None,
) -> MorningBrief:
    now = datetime.now(timezone.utc)
    brief = MorningBrief(
        brief_id=f"BRIEF-{now.strftime('%Y%m%d')}-{now.strftime('%H%M')}",
        date=now.strftime("%Y-%m-%d"))

    for r in cycle_results:
        brief.cycles_completed += 1
        brief.tasks_total += r.get("tasks_processed", r.get("total_tasks", 0))
        brief.tasks_succeeded += r.get("tasks_succeeded", 0)
        brief.tasks_failed += r.get("tasks_failed", 0)
        for err in r.get("errors", []):
            brief.alerts.append(str(err)[:200])

    if evidence:
        for e in evidence:
            brief.evidence_health[e.source] = round(e.weighted_score, 3)
            if e.weighted_score < 0.2 and e.confidence > 0.3:
                brief.alerts.append(f"Low {e.source}: {e.weighted_score:.2f}")

    if ranked_tasks:
        for r in ranked_tasks[:5]:
            brief.top_priorities.append({
                "task_id": r.task_id, "priority": r.final_priority,
                "value": r.value_score, "urgency": r.urgency,
                "genre": r.genre, "preset": r.preset})

    if gate_decisions:
        for gd in gate_decisions:
            brief.gate_decisions.append(f"{gd.target}: {gd.decision} (conf={gd.confidence:.2f})")
            if gd.decision == "FAIL":
                brief.alerts.append(f"GATE FAIL: {gd.target}")

    if brief.tasks_failed > 0:
        brief.recommendations.append(f"Review {brief.tasks_failed} failed tasks")
    if brief.tasks_succeeded > 0:
        brief.recommendations.append(f"{brief.tasks_succeeded} tasks OK — verify quality")
    if evidence:
        weak = [s.source for s in evidence if s.weighted_score < 0.3]
        if weak:
            brief.recommendations.append(f"Strengthen: {weak}")
    if ranked_tasks:
        brief.next_actions.append(f"Next: {ranked_tasks[0].task_id}")
    if brief.alerts:
        brief.next_actions.append("Address alerts before next cycle")

    # Build markdown
    md = [f"# 🌅 Moodify Morning Brief — {brief.date}", "",
          "## Summary", f"- Cycles: {brief.cycles_completed}",
          f"- Tasks: {brief.tasks_succeeded}/{brief.tasks_total} succeeded",
          f"- Failed: {brief.tasks_failed}", ""]
    if brief.top_priorities:
        md.append("## Top Priorities")
        md.append("| Task | Prio | Value | Urgency | Genre |")
        md.append("|------|------|-------|---------|-------|")
        for t in brief.top_priorities:
            md.append(f"| {t['task_id']} | {t['priority']:.2f} | {t['value']:.2f} | {t['urgency']:.2f} | {t.get('genre','')} |")
        md.append("")
    if brief.evidence_health:
        md.append("## Evidence Health")
        for src, sc in brief.evidence_health.items():
            icon = "🟢" if sc >= 0.7 else "🟡" if sc >= 0.4 else "🔴"
            md.append(f"- {icon} {src}: {sc:.3f}")
        md.append("")
    if brief.gate_decisions:
        md.append("## Gate Decisions")
        for gd in brief.gate_decisions:
            md.append(f"- {gd}")
        md.append("")
    if brief.alerts:
        md.append("## ⚠️ Alerts")
        for a in brief.alerts[:10]:
            md.append(f"- {a}")
        md.append("")
    if brief.recommendations:
        md.append("## Recommendations")
        for r in brief.recommendations:
            md.append(f"- {r}")
        md.append("")
    if brief.next_actions:
        md.append("## Next Actions")
        for a in brief.next_actions:
            md.append(f"- [ ] {a}")
        md.append("")
    brief.raw_markdown = "\n".join(md)
    return brief


# ═══════════════════════════════════════════════════════════════════════════
# MHP-546: Anti-Loop Guardrail Engine
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class LoopCheckResult:
    safe: bool = True
    loop_detected: bool = False
    pattern: str = ""
    stuck_tasks: List[str] = field(default_factory=list)
    recommendation: str = ""
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def anti_loop_check(
    task_history: List[Dict[str, Any]],
    max_repeats: int = 3, window_size: int = 10,
) -> LoopCheckResult:
    result = LoopCheckResult()
    if len(task_history) < max_repeats:
        return result
    recent = task_history[-window_size:]
    ids = [h.get("task_id", h.get("id", "?")) for h in recent]
    # Same task repeating
    last_n = ids[-max_repeats:]
    if len(set(last_n)) == 1 and len(last_n) >= max_repeats:
        result.loop_detected = True; result.safe = False
        result.pattern = "repeat"; result.stuck_tasks = [last_n[0]]
        result.recommendation = f"Task {last_n[0]} repeated {max_repeats}x — pause"
    # Alternating pair
    if len(ids) >= 4:
        l4 = ids[-4:]
        if l4[0] == l4[2] and l4[1] == l4[3] and l4[0] != l4[1]:
            result.loop_detected = True; result.safe = False
            result.pattern = "alternating"
            result.stuck_tasks = [l4[0], l4[1]]
            result.recommendation = f"Alternating {l4[0]}↔{l4[1]} — break"
    # Always-failing
    failing = [h for h in recent[-max_repeats:] if not h.get("ok", h.get("success", True))]
    if len(failing) >= max_repeats:
        result.loop_detected = True; result.safe = False
        if not result.pattern:
            result.pattern = "always-failing"
        result.stuck_tasks = list({h.get("task_id", "?") for h in failing})
        result.recommendation = f"{len(failing)} consecutive failures — HOLD"
    result.details = {"history_size": len(task_history), "window": window_size,
                      "recent_tasks": ids[-5:]}
    return result


# ═══════════════════════════════════════════════════════════════════════════
# MHP-547: Craft Feedback Selector
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class CraftFeedbackSelection:
    task_id: str = ""
    selected_operations: List[str] = field(default_factory=list)
    risk_level: str = "medium"
    justification: str = ""
    ct_findings_used: int = 0
    mrs_score_used: float = 0.0
    timestamp: str = field(default_factory=_utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


_OPS_SAFE = {"input_normalize", "silence_trim", "loudness_normalize"}
_OPS_MODERATE = {"warmth_adjust", "clarity_boost", "stereo_width", "compressor"}
_OPS_RISKY = {"overdark_fix", "transient_repair", "spectral_carve", "de_ess"}

_FINDING_MAP: Dict[str, List[str]] = {
    "over_dark": ["clarity_boost", "overdark_fix"],
    "over_bright": ["warmth_adjust", "compressor"],
    "narrow_stereo": ["stereo_width"],
    "transient_damage": ["transient_repair"],
    "sibilance": ["de_ess"],
    "harshness": ["compressor", "spectral_carve"],
    "dynamics_flat": ["compressor"],
    "low_loudness": ["loudness_normalize"],
}


def select_craft_operations(
    ct_findings: List[Dict[str, Any]],
    mrs_score: float = 0.0,
    max_risk: str = "medium",
    max_ops: int = 5,
) -> CraftFeedbackSelection:
    sel = CraftFeedbackSelection(
        task_id=f"craft-{_utc_now().replace(':','-')[:16]}",
        ct_findings_used=len(ct_findings), mrs_score_used=mrs_score)
    risk_ceiling = {"low": _OPS_SAFE, "medium": _OPS_SAFE | _OPS_MODERATE,
                    "high": _OPS_SAFE | _OPS_MODERATE | _OPS_RISKY}
    allowed = risk_ceiling.get(max_risk, risk_ceiling["medium"])
    reasons: List[str] = []
    for f in ct_findings:
        issue = f.get("issue", f.get("type", ""))
        sev = f.get("severity", "info")
        for op in _FINDING_MAP.get(issue, []):
            if op not in sel.selected_operations and op in allowed:
                sel.selected_operations.append(op)
                reasons.append(f"{issue}({sev})→{op}")
    for op in ["input_normalize", "silence_trim"]:
        if op not in sel.selected_operations:
            sel.selected_operations.insert(0, op)
    sel.selected_operations = sel.selected_operations[:max_ops]
    risky = [op for op in sel.selected_operations if op in _OPS_RISKY]
    if risky:
        sel.risk_level = "high"
    elif any(op in _OPS_MODERATE for op in sel.selected_operations):
        sel.risk_level = "medium"
    else:
        sel.risk_level = "low"
    if mrs_score > 0.7:
        sel.justification = f"MRS {mrs_score:.2f} high — minimal processing"
    elif mrs_score < 0.3:
        sel.justification = f"MRS {mrs_score:.2f} low — aggressive processing"
    else:
        sel.justification = f"{len(sel.selected_operations)} ops from {len(ct_findings)} CT findings"
    sel.justification += f". Risk: {sel.risk_level}. {'; '.join(reasons[:3])}"
    return sel


# ═══════════════════════════════════════════════════════════════════════════
# MHP-548: MRS/CT Evidence Synthesizer
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class SynthesizedEvidence:
    sample_id: str = ""
    mrs_score: float = 0.0
    mrs_delta: float = 0.0
    over_dark_level: str = "none"
    ct_issues: int = 0
    ct_critical: int = 0
    agreement_score: float = 0.0
    recommendation: str = ""
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def synthesize_mrs_ct(
    mrs_result: Dict[str, Any],
    ct_findings: List[Dict[str, Any]],
) -> SynthesizedEvidence:
    synth = SynthesizedEvidence(
        sample_id=mrs_result.get("sample_id", ""),
        mrs_score=mrs_result.get("mrs_score", 0.0),
        mrs_delta=mrs_result.get("mrs_delta", 0.0),
        over_dark_level=mrs_result.get("over_dark_level", "none"),
        ct_issues=len(ct_findings),
        ct_critical=sum(1 for f in ct_findings if f.get("severity") == "critical"))
    mrs_ok = synth.mrs_score >= 0.6
    ct_clean = synth.ct_critical == 0 and synth.ct_issues <= 2
    if mrs_ok and ct_clean:
        synth.agreement_score = 1.0
        synth.recommendation = "Both agree: quality good."
    elif mrs_ok and not ct_clean:
        synth.agreement_score = 0.3
        synth.recommendation = "MRS says OK but CT shows issues — investigate."
    elif not mrs_ok and ct_clean:
        synth.agreement_score = 0.4
        synth.recommendation = "MRS says bad but CT looks clean — calibration check."
    else:
        synth.agreement_score = 0.0
        synth.recommendation = "Both indicate problems — priority fix."
    synth.details = {"mrs_source": mrs_result.get("source", "unknown"),
                     "ct_findings": synth.ct_issues}
    return synth


# ═══════════════════════════════════════════════════════════════════════════
# MHP-549: Config Profiles
# ═══════════════════════════════════════════════════════════════════════════

_TIDAL_INTEL_PROFILES = {
    "default": {"min_evidence_confidence": 0.3, "max_concurrent_tasks": 3,
                "budget_s": 3600, "anti_loop_max_repeats": 3,
                "anti_loop_window": 10, "morning_brief": True,
                "sources": ["mrs", "ct", "runtime", "listening", "craft"]},
    "aggressive": {"min_evidence_confidence": 0.2, "max_concurrent_tasks": 5,
                   "budget_s": 7200, "anti_loop_max_repeats": 5,
                   "anti_loop_window": 20, "morning_brief": True,
                   "sources": ["mrs", "ct", "runtime", "listening", "craft"]},
    "conservative": {"min_evidence_confidence": 0.5, "max_concurrent_tasks": 2,
                     "budget_s": 1800, "anti_loop_max_repeats": 2,
                     "anti_loop_window": 6, "morning_brief": True,
                     "sources": ["mrs", "ct", "runtime"]},
    "overnight": {"min_evidence_confidence": 0.3, "max_concurrent_tasks": 4,
                  "budget_s": 28800, "anti_loop_max_repeats": 3,
                  "anti_loop_window": 10, "morning_brief": True,
                  "sources": ["mrs", "ct", "runtime", "listening", "craft"]},
}


def load_tidal_intelligence_config(profile: str = "default") -> Dict[str, Any]:
    return _TIDAL_INTEL_PROFILES.get(profile, _TIDAL_INTEL_PROFILES["default"])


# ═══════════════════════════════════════════════════════════════════════════
# MHP-550: Integration Smoke — end-to-end synthetic pipeline
# ═══════════════════════════════════════════════════════════════════════════

def run_intelligence_smoke() -> Dict[str, Any]:
    mrs_d = {"gate_accuracy": 0.85, "over_dark_level": "none", "sample_count": 50}
    ct_d = [{"severity": "info", "issue": "dynamics_flat"},
            {"severity": "warn", "issue": "over_dark"}]
    rt_d = {"tasks_succeeded": 45, "tasks_processed": 50, "crashed": False}

    evidence = [score_mrs_evidence(mrs_d), score_ct_evidence(ct_d), score_runtime_evidence(rt_d)]

    tasks = [
        {"id": "fix-overdark-pop", "base_priority": 0.7, "value_score": 0.8, "urgency": 0.6, "genre": "pop"},
        {"id": "calibrate-rock", "base_priority": 0.5, "value_score": 0.6, "urgency": 0.3, "genre": "rock"},
        {"id": "listen-batch", "base_priority": 0.9, "value_score": 0.9, "urgency": 0.8, "genre": "all"},
    ]
    ranked = rank_tasks(tasks, evidence)
    plan = plan_adaptive_queue(tasks, evidence, budget_s=600)
    gate = decide_gate("NEM-TIDAL-CORE-BUILD-025", evidence, required_sources=["mrs", "runtime"])
    brief = generate_morning_brief(
        [{"tasks_succeeded": 45, "tasks_processed": 50, "tasks_failed": 5, "errors": []}],
        ranked, [gate], evidence)
    craft = select_craft_operations(ct_d, mrs_score=0.72)
    synth = synthesize_mrs_ct(
        {"sample_id": "smoke-001", "mrs_score": 0.72, "mrs_delta": 0.15,
         "over_dark_level": "none", "source": "calibrated"}, ct_d)
    loop = anti_loop_check([
        {"task_id": "A", "ok": True}, {"task_id": "B", "ok": True},
        {"task_id": "C", "ok": True}, {"task_id": "A", "ok": True}])

    return {
        "evidence_scores": {e.source: round(e.weighted_score, 3) for e in evidence},
        "ranked": [(r.task_id, r.final_priority) for r in ranked],
        "plan_tasks": len(plan.tasks), "plan_warnings": plan.warnings,
        "gate": gate.decision, "gate_confidence": gate.confidence,
        "brief_summary": f"{brief.tasks_succeeded}/{brief.tasks_total}",
        "craft_ops": craft.selected_operations, "craft_risk": craft.risk_level,
        "synthesis_agreement": synth.agreement_score,
        "anti_loop_safe": loop.safe,
        "smoke_ok": all([len(ranked) == 3, gate.decision in ("PASS", "ADOPT"),
                         loop.safe, len(plan.tasks) > 0, brief.tasks_total > 0,
                         len(craft.selected_operations) > 0,
                         0 <= synth.agreement_score <= 1.0]),
    }


def cli_intelligence_report(run_id: str = "") -> Dict[str, Any]:
    return run_intelligence_smoke()


def cli_morning_brief(run_id: str = "") -> str:
    evidence = score_all_evidence(
        mrs={"gate_accuracy": 0.85, "over_dark_level": "none", "sample_count": 50},
        ct=[{"severity": "info", "issue": "dynamics_flat"}],
        runtime={"tasks_succeeded": 45, "tasks_processed": 50, "crashed": False})
    tasks = [{"id": "run-listen-batch", "base_priority": 0.9, "value_score": 0.9, "urgency": 0.8}]
    ranked = rank_tasks(tasks, evidence)
    gate = decide_gate("NEM-TIDAL", evidence)
    brief = generate_morning_brief(
        [{"tasks_succeeded": 45, "tasks_processed": 50, "tasks_failed": 5, "errors": []}],
        ranked, [gate], evidence)
    return brief.raw_markdown
