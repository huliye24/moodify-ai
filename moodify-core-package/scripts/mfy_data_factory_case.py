#!/usr/bin/env python3
"""Operator CLI for MFY-DATA-FACTORY-001."""

from __future__ import annotations

import argparse
from pathlib import Path

from moodify.data_factory.dataset_builder import aggregate_dataset, build_case_dataset
from moodify.data_factory.runner import run_production_case


def main() -> int:
    parser = argparse.ArgumentParser(description="Moodify Phase-I auditory data factory")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="create one SOURCE→ABC machine evidence case")
    run.add_argument("source", type=Path)
    run.add_argument("--output-root", type=Path, default=Path("outputs/data_factory"))
    run.add_argument("--case-id", default=None)
    run.add_argument("--scan-profile", default="MFY-WSE-SCAN-PROFILE-001")

    finalize = sub.add_parser("finalize", help="materialize learning rows after human review")
    finalize.add_argument("case_dir", type=Path)

    aggregate = sub.add_parser("aggregate", help="aggregate completed cases")
    aggregate.add_argument("cases_root", type=Path)
    aggregate.add_argument("--output-dir", type=Path, required=True)

    args = parser.parse_args()
    if args.command == "run":
        case_dir = run_production_case(
            args.source,
            args.output_root,
            case_id=args.case_id,
            scan_profile_id=args.scan_profile,
        )
        print(f"CASE_CREATED={case_dir}")
        print(f"HUMAN_REVIEW={case_dir / '06_human_review' / 'review.json'}")
        return 0

    if args.command == "finalize":
        record = build_case_dataset(args.case_dir)
        print(f"CASE_FINALIZED={record['case_id']}")
        print("PAIRWISE_PREFERENCES=6")
        return 0

    summary = aggregate_dataset(args.cases_root, args.output_dir)
    print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
