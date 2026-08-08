"""CLI handlers for knowledge feedback (moodify capability history/propose/policy)."""

from __future__ import annotations

import datetime
import json
from pathlib import Path

from moodify.capability_registry.knowledge.policy import (
    PolicyLedger,
    meets_sample_threshold,
    propose_rule_change,
)
from moodify.capability_registry.knowledge.records import (
    KnowledgeStore,
)


def _utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def cmd_capability_history(args) -> int:
    store = KnowledgeStore(Path(args.store_dir))
    case_id = args.case_id
    print(f"\nKnowledge history (case: {case_id or 'all'})")
    for m in store.measurements(case_id):
        print(f"  M {m.record_id}  case={m.case_id}  cap={m.capability_id}  provider={m.provider_id}"
              f"  exec={m.execution_record_id}")
    for j in store.judgments(case_id):
        print(f"  J {j.record_id}  case={j.case_id}  {j.judgment}  {j.reason}")
    for n in store.negative(case_id):
        print(f"  N {n.record_id}  case={n.case_id}  kind={n.kind}  rule={n.linked_rule_id or '-'}")
    print(f"\n  totals: {store.count('measurements')} measurements / "
          f"{store.count('judgments')} judgments / {store.count('negative')} negative")
    if args.json:
        print(json.dumps({
            "measurements": [m.to_dict() for m in store.measurements(case_id)],
            "judgments": [j.to_dict() for j in store.judgments(case_id)],
            "negative": [n.to_dict() for n in store.negative(case_id)],
        }, ensure_ascii=False, indent=2))
    return 0


def cmd_capability_propose(args) -> int:
    """Generate a rule-change proposal from a case (never auto-applies)."""
    store = KnowledgeStore(Path(args.store_dir))
    measurements = store.measurements(args.case_id)
    if not meets_sample_threshold(len(measurements)):
        print(f"ERROR: minimum sample threshold not met: {len(measurements)} < 3")
        print("  Single/anomalous cases cannot trigger proposals (anti-pollution).")
        return 2

    capability_id = args.capability_id
    # derive proposal from aggregated measurements (simple: majority provider)
    provider_counts: dict[str, int] = {}
    for m in measurements:
        provider_counts[m.provider_id] = provider_counts.get(m.provider_id, 0) + 1
    preferred = max(provider_counts, key=provider_counts.get) if provider_counts else ""

    evidence_ids = tuple(m.record_id for m in measurements)
    negative_ids = tuple(n.record_id for n in store.negative(args.case_id))
    proposal = propose_rule_change(
        case_ids=(args.case_id,),
        change_type="provider_preference",
        target=capability_id,
        proposed_value={"preferred_provider": preferred, "samples": len(measurements)},
        rationale=f"Majority provider preference from {len(measurements)} measured cases",
        evidence_record_ids=evidence_ids,
        negative_knowledge_ids=negative_ids,
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proposal.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Proposal drafted (NOT applied): {out}")
    print(f"  {proposal.proposal_id}  type={proposal.change_type}  target={capability_id}")
    print(f"  preferred_provider={preferred or 'unknown'}  samples={len(measurements)}")
    print(f"  evidence: {len(evidence_ids)}  negative_knowledge: {len(negative_ids)}")
    print("  Requires human confirmation before entering policy ledger.")
    return 0


def cmd_capability_policy(args) -> int:
    ledger = PolicyLedger(Path(args.store_dir))
    entries = ledger.entries()
    print(f"\nProduction policy ledger (current: {ledger.current_version()})")
    for entry in entries:
        print(f"  {entry.policy_version:12s} {entry.change_type:22s} {entry.target:24s} "
              f"value={entry.value}")
        if entry.superseded_rule:
            print(f"    supersedes: {entry.superseded_rule}  (source: {entry.superseded_rule_source})")
    print(f"\n  total entries: {len(entries)}")
    if args.json:
        print(json.dumps([e.to_dict() for e in entries], ensure_ascii=False, indent=2))
    return 0


def register_knowledge_subparsers(subparsers) -> None:
    p_history = subparsers.add_parser("history", help="List measurement/judgment/negative records")
    p_history.add_argument("--store-dir", default="knowledge")
    p_history.add_argument("--case-id", default=None)
    p_history.add_argument("--json", action="store_true")

    p_propose = subparsers.add_parser("propose", help="Draft a rule-change proposal (never auto-applies)")
    p_propose.add_argument("--store-dir", default="knowledge")
    p_propose.add_argument("--case-id", required=True)
    p_propose.add_argument("--capability-id", required=True)
    p_propose.add_argument("--out", required=True, help="proposal JSON path")

    p_policy = subparsers.add_parser("policy", help="View the versioned production policy ledger")
    p_policy.add_argument("--store-dir", default="knowledge")
    p_policy.add_argument("--json", action="store_true")
