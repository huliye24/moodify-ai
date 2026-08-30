"""Command-line interface for the contribution core."""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

from .core import ContributionCore
from .evidence import EvidenceBundle
from .scorer import Scorer


def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load JSON data from file.

    Args:
        file_path: Path to JSON file

    Returns:
        Loaded JSON data
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File {file_path} not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {file_path}: {e}")
        sys.exit(1)


def save_json_file(data: Dict[str, Any], file_path: str) -> None:
    """Save JSON data to file.

    Args:
        data: JSON data to save
        file_path: Path to output file
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error: Failed to save {file_path}: {e}")
        sys.exit(1)


def create_contribution_command(args) -> None:
    """Handle create contribution command."""
    core = ContributionCore(storage_path=args.storage)

    # Load contributor info
    contributor = load_json_file(args.contributor)

    # Load content
    content = load_json_file(args.content)

    # Load evidence if provided
    evidence = None
    if args.evidence:
        evidence = load_json_file(args.evidence)

    # Create contribution
    contribution, errors = core.create_contribution(
        contributor=contributor,
        category=args.category,
        content=content,
        evidence=evidence,
        schema_version=args.schema_version
    )

    if errors:
        print("Failed to create contribution:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

    print("Contribution created successfully:")
    print(json.dumps(contribution, indent=2))

    # Save if requested
    if args.output:
        save_json_file(contribution, args.output)


def submit_contribution_command(args) -> None:
    """Handle submit contribution command."""
    core = ContributionCore(storage_path=args.storage)

    # Load review data if provided
    review_data = None
    if args.review:
        review_data = load_json_file(args.review)

    # Submit contribution
    contribution, errors = core.submit_contribution(
        contribution_id=args.contribution_id,
        review_data=review_data
    )

    if errors:
        print("Failed to submit contribution:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

    print("Contribution submitted successfully:")
    print(json.dumps(contribution, indent=2))

    # Save if requested
    if args.output:
        save_json_file(contribution, args.output)


def review_contribution_command(args) -> None:
    """Handle review contribution command."""
    core = ContributionCore(storage_path=args.storage)

    # Load review data
    review_data = load_json_file(args.review)

    # Review contribution
    contribution, errors = core.review_contribution(
        contribution_id=args.contribution_id,
        decision=args.decision,
        review_data=review_data
    )

    if errors:
        print("Failed to review contribution:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

    print("Contribution reviewed successfully:")
    print(json.dumps(contribution, indent=2))

    # Save if requested
    if args.output:
        save_json_file(contribution, args.output)


def add_evidence_command(args) -> None:
    """Handle add evidence command."""
    core = ContributionCore(storage_path=args.storage)

    # Load evidence
    evidence = load_json_file(args.evidence)

    # Add evidence
    contribution, errors = core.add_evidence(
        contribution_id=args.contribution_id,
        evidence=evidence
    )

    if errors:
        print("Failed to add evidence:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

    print("Evidence added successfully:")
    print(json.dumps(contribution, indent=2))

    # Save if requested
    if args.output:
        save_json_file(contribution, args.output)


def score_contribution_command(args) -> None:
    """Handle score contribution command."""
    core = ContributionCore(storage_path=args.storage)

    # Load reputation evidence
    reputation_evidence = load_json_file(args.reputation_evidence)

    # Score contribution
    contribution, errors = core.score_contribution(
        contribution_id=args.contribution_id,
        reputation_evidence=reputation_evidence
    )

    if errors:
        print("Failed to score contribution:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

    print("Contribution scored successfully:")
    print(json.dumps(contribution, indent=2))

    # Save if requested
    if args.output:
        save_json_file(contribution, args.output)


def finalize_contribution_command(args) -> None:
    """Handle finalize contribution command."""
    core = ContributionCore(storage_path=args.storage)

    # Load review data if provided
    review_data = None
    if args.review:
        review_data = load_json_file(args.review)

    # Finalize contribution
    contribution, errors = core.finalize_contribution(
        contribution_id=args.contribution_id,
        review_data=review_data
    )

    if errors:
        print("Failed to finalize contribution:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

    print("Contribution finalized successfully:")
    print(json.dumps(contribution, indent=2))

    # Save if requested
    if args.output:
        save_json_file(contribution, args.output)


def get_contribution_command(args) -> None:
    """Handle get contribution command."""
    core = ContributionCore(storage_path=args.storage)

    # Get contribution
    contribution = core.get_contribution(args.contribution_id)

    if not contribution:
        print(f"Contribution {args.contribution_id} not found")
        sys.exit(1)

    print("Contribution:")
    print(json.dumps(contribution, indent=2))


def get_status_command(args) -> None:
    """Handle get status command."""
    core = ContributionCore(storage_path=args.storage)

    # Get status
    status = core.get_contribution_status(args.contribution_id)

    if not status:
        print(f"Contribution {args.contribution_id} not found")
        sys.exit(1)

    print(f"Status: {status}")


def get_history_command(args) -> None:
    """Handle get history command."""
    core = ContributionCore(storage_path=args.storage)

    # Get history
    history = core.get_contribution_history(args.contribution_id)

    if not history:
        print(f"No history found for contribution {args.contribution_id}")
        sys.exit(1)

    print("Contribution history:")
    for entry in history:
        print(f"  {entry['timestamp']}: {entry['status']}")
        if entry['metadata'].get('action'):
            print(f"    Action: {entry['metadata']['action']}")


def detect_duplicates_command(args) -> None:
    """Handle detect duplicates command."""
    core = ContributionCore(storage_path=args.storage)

    # Detect duplicates
    duplicates = core.detect_duplicate_evidence(args.contribution_id)

    if not duplicates:
        print("No duplicate evidence found")
        return

    print("Duplicate evidence detected:")
    for evidence_id, duplicates_list in duplicates.items():
        print(f"  {evidence_id} duplicates: {', '.join(duplicates_list)}")


def get_allowed_transitions_command(args) -> None:
    """Handle get allowed transitions command."""
    core = ContributionCore(storage_path=args.storage)

    # Get allowed transitions
    transitions = core.get_allowed_transitions(args.contribution_id)

    if not transitions:
        print(f"No allowed transitions for contribution {args.contribution_id}")
        sys.exit(1)

    print(f"Allowed transitions from current status:")
    for transition in transitions:
        print(f"  - {transition}")


def validate_contribution_command(args) -> None:
    """Handle validate contribution command."""
    core = ContributionCore(storage_path=args.storage)

    # Load contribution
    contribution = load_json_file(args.contribution)

    # Validate
    is_valid, errors = core.validator.validate_contribution(contribution)

    if is_valid:
        print("Contribution is valid")
    else:
        print("Contribution validation failed:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        description='MOOD Protocol Contribution Core CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--storage',
        type=str,
        help='Path to storage directory'
    )

    subparsers = parser.add_subparsers(dest='command', required=True)

    # Create contribution command
    create_parser = subparsers.add_parser('create', help='Create a new contribution')
    create_parser.add_argument('--contributor', required=True, help='Path to contributor JSON file')
    create_parser.add_argument('--category', required=True, help='Contribution category')
    create_parser.add_argument('--content', required=True, help='Path to content JSON file')
    create_parser.add_argument('--evidence', help='Path to evidence JSON file (optional)')
    create_parser.add_argument('--schema-version', default='1.0.0', help='Schema version')
    create_parser.add_argument('--output', help='Output file path')
    create_parser.set_defaults(func=create_contribution_command)

    # Submit contribution command
    submit_parser = subparsers.add_parser('submit', help='Submit a draft contribution')
    submit_parser.add_argument('contribution_id', help='ID of contribution to submit')
    submit_parser.add_argument('--review', help='Path to review data JSON file')
    submit_parser.add_argument('--output', help='Output file path')
    submit_parser.set_defaults(func=submit_contribution_command)

    # Review contribution command
    review_parser = subparsers.add_parser('review', help='Review a submitted contribution')
    review_parser.add_argument('contribution_id', help='ID of contribution to review')
    review_parser.add_argument('decision', choices=['verified', 'rejected', 'needs_more_evidence'], help='Review decision')
    review_parser.add_argument('--review', required=True, help='Path to review data JSON file')
    review_parser.add_argument('--output', help='Output file path')
    review_parser.set_defaults(func=review_contribution_command)

    # Add evidence command
    evidence_parser = subparsers.add_parser('evidence', help='Add evidence to a contribution')
    evidence_parser.add_argument('contribution_id', help='ID of contribution to add evidence to')
    evidence_parser.add_argument('evidence', help='Path to evidence JSON file')
    evidence_parser.add_argument('--output', help='Output file path')
    evidence_parser.set_defaults(func=add_evidence_command)

    # Score contribution command
    score_parser = subparsers.add_parser('score', help='Score a verified contribution')
    score_parser.add_argument('contribution_id', help='ID of contribution to score')
    score_parser.add_argument('reputation_evidence', help='Path to reputation evidence JSON file')
    score_parser.add_argument('--output', help='Output file path')
    score_parser.set_defaults(func=score_contribution_command)

    # Finalize contribution command
    finalize_parser = subparsers.add_parser('finalize', help='Finalize a scored contribution')
    finalize_parser.add_argument('contribution_id', help='ID of contribution to finalize')
    finalize_parser.add_argument('--review', help='Path to review data JSON file')
    finalize_parser.add_argument('--output', help='Output file path')
    finalize_parser.set_defaults(func=finalize_contribution_command)

    # Get contribution command
    get_parser = subparsers.add_parser('get', help='Get a contribution by ID')
    get_parser.add_argument('contribution_id', help='ID of contribution to get')
    get_parser.set_defaults(func=get_contribution_command)

    # Get status command
    status_parser = subparsers.add_parser('status', help='Get contribution status')
    status_parser.add_argument('contribution_id', help='ID of contribution')
    status_parser.set_defaults(func=get_status_command)

    # Get history command
    history_parser = subparsers.add_parser('history', help='Get contribution history')
    history_parser.add_argument('contribution_id', help='ID of contribution')
    history_parser.set_defaults(func=get_history_command)

    # Detect duplicates command
    duplicates_parser = subparsers.add_parser('duplicates', help='Detect duplicate evidence')
    duplicates_parser.add_argument('contribution_id', help='ID of contribution')
    duplicates_parser.set_defaults(func=detect_duplicates_command)

    # Get allowed transitions command
    transitions_parser = subparsers.add_parser('transitions', help='Get allowed state transitions')
    transitions_parser.add_argument('contribution_id', help='ID of contribution')
    transitions_parser.set_defaults(func=get_allowed_transitions_command)

    # Validate contribution command
    validate_parser = subparsers.add_parser('validate', help='Validate a contribution')
    validate_parser.add_argument('contribution', help='Path to contribution JSON file')
    validate_parser.set_defaults(func=validate_contribution_command)

    return parser


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()