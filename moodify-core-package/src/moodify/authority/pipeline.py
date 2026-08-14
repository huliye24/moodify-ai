"""Scoped review pipeline — the single gate between "case completed" and
"machine may decide".

MFY_EAR_SCOPED_JUDGMENT_AND_HUMAN_ESCALATION_001 §4: the canonical runner must
be able to produce escalation/uncertain states; an unattended node stops the
authoritative follow-up when escalation is required while retaining safe
artifacts; timeout never becomes automatic machine approval.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from moodify.authority.escalation import EscalationRecord, evaluate_scope, evaluate_verification
from moodify.authority.review_store import ReviewStore


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def run_scoped_review(
    case_dir: Path,
    store: ReviewStore,
    case_id: str | None = None,
    *,
    write_review: bool = True,
) -> dict:
    """Gate for the canonical runner.

    Returns an escalation-style record:
      - outcome MACHINE_DECIDED → review.json written (algorithm decided)
      - outcome HUMAN_REQUIRED / INCONCLUSIVE / FAILED → review task enqueued;
        review.json is NOT written as a verdict (fail closed)
    """
    case_dir = Path(case_dir)
    manifest = _read_json(case_dir / "case_manifest.json") if (case_dir / "case_manifest.json").is_file() else None
    case_id = case_id or (manifest or {}).get("case_id")

    # 1. scope contract check (profile/format/duration/channels/evidence/rule)
    scope_record = evaluate_scope(manifest)
    if scope_record is not None:
        return _escalate(case_dir, store, case_id, scope_record, manifest)

    # 2. verification invariants (fail closed on invariant failure)
    invariant_failures: list[str] = []
    compare_dir = case_dir / "05_comparison"
    if compare_dir.is_dir():
        for report in sorted(compare_dir.glob("*/comparison_report.json")):
            try:
                data = _read_json(report)
            except (json.JSONDecodeError, OSError):
                invariant_failures.append(f"{report.parent.name}:unreadable")
                continue
            guardrails = data.get("guardrail_failures") or []
            if guardrails:
                invariant_failures.extend(f"{report.parent.name}:{g}" for g in guardrails)
    verify_record = evaluate_verification(invariant_failures=invariant_failures)
    if verify_record is not None:
        return _escalate(case_dir, store, case_id, verify_record, manifest)

    # 3. machine may decide inside the approved scope
    if write_review:
        from moodify.data_factory.algorithmic_review import write_algorithmic_review

        write_algorithmic_review(case_dir, case_id=case_id)
    return {
        "outcome": "MACHINE_DECIDED",
        "reasons": [],
        "details": {"contract": "MFY-ALGORITHMIC-REVIEW-001 v1.0"},
        "created_at": _now(),
    }


def _escalate(case_dir: Path, store: ReviewStore, case_id: str | None, record: EscalationRecord, manifest: dict | None) -> dict:
    """Enqueue a review task; never write a machine verdict for this case."""
    case_id = case_id or "unknown"
    snapshot_ref = str(case_dir.resolve())
    store.enqueue(
        case_id=case_id,
        reason=record.reasons[0] if record.reasons else "ESCALATED",
        escalation=record.as_dict(),
        snapshot_ref=snapshot_ref,
        created_at=_now(),
    )
    # mark the authority state on the case record (AWAITING_HUMAN)
    case_record = case_dir / "production_case.json"
    if case_record.is_file():
        try:
            data = _read_json(case_record)
        except json.JSONDecodeError:
            data = {}
        data["authority_state"] = "HUMAN_REQUIRED"
        data["lifecycle_state"] = "AWAITING_HUMAN"
        data["escalation"] = record.as_dict()
        case_record.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return record.as_dict()
