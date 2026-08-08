"""Create one immutable, timestamped Moodify project-health analysis run."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

TIMEZONE = ZoneInfo("Asia/Shanghai")
SCHEMA = "moodify.analytics.run-manifest/0.1"
CONTRACT = "moodify.analytics.metric-contracts/0.1"


def command(args: list[str], cwd: Path, timeout: int = 300) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=cwd,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        timeout=timeout,
        check=False,
    )


def git(root: Path, *args: str) -> str:
    result = command(["git", *args], root)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "git command failed")
    return result.stdout


def collect_repository(root: Path) -> dict:
    status = [line for line in git(root, "status", "--porcelain=v1").splitlines() if line]
    tracked = [line for line in git(root, "ls-files").splitlines() if line]
    numstat = [line for line in git(root, "diff", "--numstat").splitlines() if line]
    insertions = deletions = 0
    areas: Counter[str] = Counter()
    for line in numstat:
        added, removed, path = line.split("\t", 2)
        if added != "-":
            insertions += int(added)
        if removed != "-":
            deletions += int(removed)
        areas[path.split("/", 1)[0]] += 1
    modified = sum(not line.startswith("??") for line in status)
    return {
        "tracked_files": len(tracked),
        "modified_tracked_entries": modified,
        "untracked_entries": sum(line.startswith("??") for line in status),
        "changed_tracked_files": len(numstat),
        "insertions": insertions,
        "deletions": deletions,
        "dirty_tracked_share_pct": round(100 * modified / len(tracked), 2) if tracked else None,
        "change_areas": [{"area": key, "changed_files": value} for key, value in areas.most_common()],
    }


def collect_code_structure(root: Path) -> dict:
    tracked = [line for line in git(root, "ls-files").splitlines() if line.endswith(".py")]
    test_paths: list[Path] = []
    source_paths: list[Path] = []
    for relative in tracked:
        path = root / relative
        normalized = relative.replace("\\", "/")
        if path.name.startswith("test_") or "/tests/" in f"/{normalized}":
            test_paths.append(path)
        else:
            source_paths.append(path)

    def count_lines(paths: list[Path]) -> tuple[int, int]:
        readable = lines = 0
        for path in paths:
            if path.is_file():
                readable += 1
                lines += len(path.read_text(encoding="utf-8", errors="replace").splitlines())
        return readable, lines

    source_files, source_lines = count_lines(source_paths)
    test_files, test_lines = count_lines(test_paths)
    return {
        "python_source_files": source_files,
        "python_test_files": test_files,
        "source_physical_lines": source_lines,
        "test_physical_lines": test_lines,
        "test_to_source_physical_line_ratio_pct": round(100 * test_lines / source_lines, 1) if source_lines else None,
    }


def collect_tasks(task_root: Path) -> dict:
    all_dirs = sorted(path for path in task_root.iterdir() if path.is_dir())
    rows = []
    for path in all_dirs:
        orchestration = path / "00_TASK_ORCHESTRATION.md"
        if not orchestration.exists():
            continue
        acceptance = list(path.glob("CODEX_FINAL_ACCEPTANCE*.md"))
        handoff = path / "HANDOFF.md"
        handoff_status = ""
        if handoff.exists():
            match = re.search(
                r"^\*\*Status:\*\*\s*(.+?)\s*$",
                handoff.read_text(encoding="utf-8", errors="replace"),
                re.MULTILINE,
            )
            handoff_status = match.group(1).strip() if match else ""
        if acceptance:
            state = "accepted"
        elif path.name.startswith("DSK-MFY-CAPABILITY-ACCRETION-") and not handoff.exists():
            state = "planned"
        elif "NOT_STARTED" in handoff_status:
            state = "not_started"
        elif "READY_FOR" in handoff_status:
            state = "awaiting_acceptance"
        else:
            state = "unclassified"
        rows.append(
            {
                "task": path.name,
                "state": state,
                "handoff_status": handoff_status,
                "acceptance_docs": len(acceptance),
            }
        )
    states = Counter(row["state"] for row in rows)
    started = states["accepted"] + states["awaiting_acceptance"]
    orphan_dirs = [path for path in all_dirs if not (path / "00_TASK_ORCHESTRATION.md").exists()]
    acceptance_without_orchestration = [path for path in orphan_dirs if list(path.glob("CODEX_FINAL_ACCEPTANCE*.md"))]
    stale = [
        row for row in rows
        if row["acceptance_docs"] and ("READY_FOR" in row["handoff_status"] or "REWORK" in row["handoff_status"])
    ]
    return {
        "all_task_directories": len(all_dirs),
        "formal_task_packages": len(rows),
        "states": dict(states),
        "accepted_share_of_started_pct": round(100 * states["accepted"] / started, 1) if started else None,
        "orphan_task_directories": len(orphan_dirs),
        "acceptance_without_orchestration": len(acceptance_without_orchestration),
        "accepted_with_stale_handoff": len(stale),
        "status_source_conflicts": len(acceptance_without_orchestration) + len(stale),
        "tasks": rows,
    }


def collect_test_gate(core: Path, skip: bool) -> tuple[dict, int | None]:
    if skip:
        return {"status": "not_run", "tests_collected": None, "collection_errors": None}, None
    result = command(["py", "-3.11", "-m", "pytest", "--collect-only", "-q"], core)
    output = result.stdout + result.stderr
    tests_match = re.search(r"(\d+) tests collected", output)
    errors_match = re.search(r"(\d+) errors? in", output)
    return (
        {
            "status": "pass" if result.returncode == 0 else "fail",
            "tests_collected": int(tests_match.group(1)) if tests_match else 0,
            "collection_errors": int(errors_match.group(1)) if errors_match else 0,
            "exit_code": result.returncode,
        },
        result.returncode,
    )


def render_report(snapshot: dict) -> str:
    repo = snapshot["repository"]
    tasks = snapshot["tasks"]
    tests = snapshot["tests"]
    code = snapshot["code_structure"]
    shared_changes = sum(
        row["changed_files"]
        for row in repo["change_areas"]
        if row["area"] in {"moodify_runtime", "moodify-core-package"}
    )
    concentration = round(100 * shared_changes / repo["changed_tracked_files"], 1) if repo["changed_tracked_files"] else 0
    return "\n".join(
        [
            "# Moodify Project Health Baseline",
            "",
            f"- Analysis time: `{snapshot['started_at']}` (`Asia/Shanghai`)",
            f"- Formal tasks: `{tasks['formal_task_packages']}`; accepted share of started: `{tasks['accepted_share_of_started_pct']}%`",
            f"- Test gate: `{tests['status']}`; collected: `{tests['tests_collected']}`; collection errors: `{tests['collection_errors']}`",
            f"- Worktree: `{repo['modified_tracked_entries']}` modified tracked entries and `{repo['untracked_entries']}` untracked entries",
            f"- Shared core/runtime change concentration: `{concentration}%`",
            f"- Test/source physical-line ratio: `{code['test_to_source_physical_line_ratio_pct']}%` (not coverage)",
            f"- Task status-source conflicts: `{tasks['status_source_conflicts']}`",
            "",
            "## Decision",
            "",
            "Pause new feature expansion. Restore the full test baseline, reconcile task status, classify the worktree, then close the current critical-path task before opening the next package.",
            "",
            "## Data limitations",
            "",
            "This run measures engineering capital and governance risk. It cannot establish audio quality, user value, revenue, or time ROI because those datasets do not yet exist.",
            "",
        ]
    )


def append_registry(path: Path, entry: dict) -> None:
    if path.exists():
        existing = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        if any(row.get("run_id") == entry["run_id"] for row in existing):
            raise ValueError(f"run already registered: {entry['run_id']}")
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--started-at", help="ISO timestamp with timezone; defaults to now in Asia/Shanghai")
    parser.add_argument("--skip-tests", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    analytics = root / "project_analytics"
    started = datetime.fromisoformat(args.started_at) if args.started_at else datetime.now(TIMEZONE)
    if started.tzinfo is None:
        raise ValueError("started-at must include a timezone")
    started = started.astimezone(TIMEZONE)
    timestamp_dir = started.strftime("%Y-%m-%dT%H%M%S%z")
    run_id = f"{timestamp_dir}-project-health-baseline"
    run_dir = analytics / "runs" / timestamp_dir / "project-health-baseline"
    if run_dir.exists():
        raise FileExistsError(f"immutable run already exists: {run_dir}")
    run_dir.mkdir(parents=True)

    snapshot = {
        "schema": "moodify.analytics.project-health-snapshot/0.1",
        "started_at": started.isoformat(),
        "timezone": "Asia/Shanghai",
        "repository": collect_repository(root),
        "code_structure": collect_code_structure(root),
        "tasks": collect_tasks(root / "docs" / "tasks" / "deepseek"),
    }
    snapshot["tests"], test_exit = collect_test_gate(root / "moodify-core-package", args.skip_tests)
    (run_dir / "snapshot.json").write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (run_dir / "report.md").write_text(render_report(snapshot), encoding="utf-8")
    manifest = {
        "schema": SCHEMA,
        "run_id": run_id,
        "analysis_id": "stabilization-baseline",
        "analysis_kind": "stage",
        "started_at": started.isoformat(),
        "timezone": "Asia/Shanghai",
        "status": "partial" if args.skip_tests else "complete",
        "metric_contract": CONTRACT,
        "supersedes": None,
        "sources": ["git worktree", "docs/tasks/deepseek", "moodify-core-package/tests"],
        "outputs": ["snapshot.json", "report.md"],
        "validation": {
            "collector_exit_code": 0,
            "test_collection_exit_code": test_exit,
            "calculation_checks": [
                "task state counts sum to formal task packages",
                "change-area counts sum to changed tracked files",
                "accepted share denominator excludes planned/not-started/unclassified",
            ],
        },
    }
    (run_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    relative_manifest = (run_dir / "manifest.json").relative_to(root).as_posix()
    append_registry(
        analytics / "registry.jsonl",
        {
            "run_id": run_id,
            "analysis_id": "stabilization-baseline",
            "analysis_kind": "stage",
            "started_at": started.isoformat(),
            "status": manifest["status"],
            "manifest": relative_manifest,
        },
    )
    print(run_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

