#!/usr/bin/env python3
"""MVP baseline freeze script for Moodify Workspace v2.

Step 34: Tags the current commit as the MVP baseline, saves test evidence,
and registers next-phase requirements.

Usage:
  python scripts/freeze_mvp_baseline.py --tag v2.0.0-mvp --evidence-dir data/mvp_evidence/
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=True, text=True, capture_output=True, **kwargs)


def freeze_baseline(tag: str, evidence_dir: Path, next_phase_notes: str = "") -> dict:
    """Create MVP baseline tag and save evidence."""
    result: dict = {
        "baseline_tag": tag,
        "frozen_at": datetime.now(timezone.utc).isoformat(),
        "steps": [],
    }

    # 1. Check repo is clean
    status = run(["git", "status", "--porcelain"])
    if status.stdout.strip():
        result["steps"].append({
            "step": "check_clean",
            "status": "warning",
            "detail": "working tree has uncommitted changes",
        })

    # 2. Get current commit
    rev = run(["git", "rev-parse", "HEAD"])
    commit_hash = rev.stdout.strip()
    result["commit"] = commit_hash
    result["steps"].append({
        "step": "capture_commit",
        "status": "ok",
        "commit": commit_hash,
    })

    # 3. Create tag
    try:
        run(["git", "tag", "-a", tag, "-m", f"MVP baseline: {tag}"])
        result["steps"].append({
            "step": "create_tag",
            "status": "ok",
            "tag": tag,
        })
    except subprocess.CalledProcessError as e:
        if "already exists" in e.stderr:
            result["steps"].append({
                "step": "create_tag",
                "status": "skipped",
                "detail": f"tag {tag} already exists",
            })
        else:
            raise

    # 4. Collect test evidence
    evidence_dir.mkdir(parents=True, exist_ok=True)

    test_evidence = evidence_dir / "test_results.txt"
    try:
        test_run = run(
            ["python", "-m", "pytest", "tests/v2/", "-v", "--tb=short"],
            timeout=120,
        )
        test_evidence.write_text(test_run.stdout + "\n" + test_run.stderr)
        result["steps"].append({
            "step": "run_tests",
            "status": "ok" if test_run.returncode == 0 else "failed",
            "output": str(test_evidence),
        })
    except Exception as e:
        result["steps"].append({
            "step": "run_tests",
            "status": "error",
            "detail": str(e),
        })

    # 5. Save manifest
    manifest = evidence_dir / "baseline_manifest.json"
    manifest.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    manifest_sha256 = hashlib.sha256(manifest.read_bytes()).hexdigest()
    result["manifest_sha256"] = manifest_sha256

    # 6. Register next-phase requirements
    if next_phase_notes:
        next_phase_file = evidence_dir / "NEXT_PHASE_REQUIREMENTS.md"
        next_phase_file.write_text(
            f"# Next Phase Requirements (from MVP baseline {tag})\n\n"
            f"Frozen at: {result['frozen_at']}\n"
            f"Commit: {commit_hash}\n\n"
            f"{next_phase_notes}\n"
        )
        result["steps"].append({
            "step": "register_next_phase",
            "status": "ok",
            "file": str(next_phase_file),
        })

    return result


def verify_baseline(tag: str) -> dict:
    """Verify a baseline tag exists and is reachable."""
    try:
        run(["git", "rev-parse", "--verify", f"refs/tags/{tag}"])
        return {"verified": True, "tag": tag}
    except subprocess.CalledProcessError:
        return {"verified": False, "tag": tag, "reason": "tag not found"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Freeze MVP baseline")
    parser.add_argument("--tag", required=True, help="Git tag for the baseline (e.g. v2.0.0-mvp)")
    parser.add_argument("--evidence-dir", default="data/mvp_evidence", help="Directory for test evidence")
    parser.add_argument("--next-phase", default="", help="Next phase requirements notes")
    parser.add_argument("--verify-only", action="store_true", help="Only verify existing baseline")
    args = parser.parse_args()

    evidence = Path(args.evidence_dir)

    if args.verify_only:
        verification = verify_baseline(args.tag)
        print(json.dumps(verification, ensure_ascii=False, indent=2))
        sys.exit(0 if verification["verified"] else 1)

    result = freeze_baseline(args.tag, evidence, args.next_phase)
    print(json.dumps(result, ensure_ascii=False, indent=2))

    all_ok = all(s["status"] in ("ok", "skipped") for s in result["steps"])
    test_failed = any(s["status"] == "failed" for s in result["steps"])
    if test_failed:
        print("\nWarning: Some tests failed. Review before finalizing baseline.")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
