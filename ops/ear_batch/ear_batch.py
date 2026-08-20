"""File-backed task packs for the Moodify Ear v1 knowledge-engineering batch."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATES = {
    "PENDING", "READY", "RUNNING", "VERIFYING", "PASSED",
    "FAILED_RETRYABLE", "BLOCKED_HUMAN", "SKIPPED",
}
TERMINAL = {"PASSED", "BLOCKED_HUMAN", "SKIPPED"}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name, suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


class RunLock:
    def __init__(self, run_dir: Path):
        self.path = run_dir / ".ledger.lock"

    def __enter__(self) -> "RunLock":
        try:
            fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError as exc:
            raise SystemExit(f"run ledger is locked: {self.path}") from exc
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(f"pid={os.getpid()} at={now()}\n")
        return self

    def __exit__(self, *_: object) -> None:
        self.path.unlink(missing_ok=True)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def source_files(source: Path) -> list[Path]:
    files = []
    for path in source.rglob("*"):
        if not path.is_file():
            continue
        rel_parts = path.relative_to(source).parts
        if rel_parts and rel_parts[0].casefold() == "moodify ear 2.0":
            continue
        files.append(path)
    return sorted(files, key=lambda item: str(item).casefold())


def refresh_ready(ledger: dict[str, Any]) -> None:
    states = {item["id"]: item["state"] for item in ledger["tasks"]}
    for item in ledger["tasks"]:
        if item["state"] in {"PENDING", "FAILED_RETRYABLE"}:
            if all(states.get(dep) == "PASSED" for dep in item["deps"]):
                item["state"] = "READY"
                item["updated_at"] = now()


def task_markdown(task: dict[str, Any], source: Path, run_dir: Path) -> str:
    outputs = "\n".join(f"- `{name}`" for name in task["outputs"])
    deps = ", ".join(task["deps"]) or "none"
    return f"""# {task['id']} — {task['title']}

Status is authoritative only in `TASK_LEDGER.json`.

## Purpose

{task['instructions']}

## Context

- Source corpus: `{source}` (read-only)
- Run directory: `{run_dir}`
- Dependencies: {deps}
- Risk: `{task['risk']}`
- Maximum attempts: 3

## Required outputs

{outputs}

## Acceptance

- Every required output exists below the run directory and is non-empty.
- Claims identify their source path and distinguish proposal from verified behavior.
- No source corpus file is changed.
- No product authority is changed without explicit human approval.
- Verification evidence is written to `evidence/{task['id']}.json`.

## Failure behavior

Retry deterministic/transient failures up to the attempt limit. For listening
judgment, architecture authority, deletion, publishing, credentials, or other
human decisions, record the issue and use `BLOCKED_HUMAN`; continue independent
tasks.
"""


def cmd_init(args: argparse.Namespace) -> None:
    source = Path(args.source).resolve()
    run_dir = Path(args.run_dir).resolve()
    if not source.is_dir():
        raise SystemExit(f"source directory not found: {source}")
    if run_dir.exists() and any(run_dir.iterdir()) and not args.force:
        raise SystemExit(f"run directory is not empty: {run_dir} (use --force to replace generated state)")
    if args.force and run_dir.exists():
        resolved = run_dir.resolve()
        if resolved == source or source in resolved.parents:
            raise SystemExit("refusing to replace the source tree or its parent")
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    catalog = read_json(Path(__file__).with_name("task_catalog.json"))
    created = now()
    tasks = []
    for spec in catalog["tasks"]:
        task_dir = run_dir / "task-packs" / f"{spec['id']}-{spec['slug']}"
        task_dir.mkdir(parents=True, exist_ok=True)
        (task_dir / "TASK.md").write_text(task_markdown(spec, source, run_dir), encoding="utf-8", newline="\n")
        atomic_json(task_dir / "inputs.json", {"source": str(source), "dependencies": spec["deps"]})
        atomic_json(task_dir / "acceptance.json", {"required_outputs": spec["outputs"], "non_empty": True})
        tasks.append({**spec, "state": "PENDING", "attempts": 0, "max_attempts": 3,
                      "created_at": created, "updated_at": created, "last_error": None})
    ledger = {"schema_version": 1, "run_id": f"ear-v1-{created}", "source": str(source),
              "source_policy": "read-only", "created_at": created, "updated_at": created, "tasks": tasks}
    refresh_ready(ledger)
    atomic_json(run_dir / "TASK_LEDGER.json", ledger)
    inventory = [{"path": str(p.relative_to(source)).replace("\\", "/"), "bytes": p.stat().st_size,
                  "sha256": sha256(p), "extension": p.suffix.lower()} for p in source_files(source)]
    atomic_json(run_dir / "SOURCE_SNAPSHOT.json", {"source": str(source), "created_at": created,
                                                    "v2_excluded": True, "files": inventory})
    print(f"initialized {len(tasks)} task packs and hashed {len(inventory)} v1 source files in {run_dir}")


def ledger_path(run_dir: Path) -> Path:
    path = run_dir / "TASK_LEDGER.json"
    if not path.is_file():
        raise SystemExit(f"ledger not found: {path}")
    return path


def find_task(ledger: dict[str, Any], task_id: str) -> dict[str, Any]:
    for task in ledger["tasks"]:
        if task["id"] == task_id:
            return task
    raise SystemExit(f"unknown task: {task_id}")


def verify_outputs(run_dir: Path, task: dict[str, Any]) -> tuple[bool, list[dict[str, Any]]]:
    evidence = []
    passed = True
    output_root = run_dir.parents[2] if task.get("output_root") == "workspace" else run_dir
    for relative in task["outputs"]:
        path = output_root / relative
        ok = path.is_file() and path.stat().st_size > 0
        evidence.append({"path": relative, "exists": path.is_file(),
                         "bytes": path.stat().st_size if path.is_file() else 0,
                         "sha256": sha256(path) if ok else None, "passed": ok})
        passed = passed and ok
    return passed, evidence


def cmd_promote(args: argparse.Namespace) -> None:
    """Promote the reviewed unattended batch into executable implementation packs."""
    run_dir = Path(args.run_dir).resolve()
    batch_path = run_dir / "planning" / "unattended_batch.json"
    if not batch_path.is_file():
        raise SystemExit(f"unattended batch not found: {batch_path}")
    selected = read_json(batch_path).get("selected", [])
    with RunLock(run_dir):
        path = ledger_path(run_dir)
        ledger = read_json(path)
        existing = {task["id"] for task in ledger["tasks"]}
        mapping = {item["id"]: f"IMP-{int(item['id'].split('-')[1]):03d}" for item in selected}
        added = 0
        for item in selected:
            task_id = mapping[item["id"]]
            if task_id in existing:
                continue
            deps = [mapping[dep] for dep in item["deps"] if dep in mapping] or ["TP-305"]
            slug = re_slug(item["title"])
            task = {"id": task_id, "work_item_id": item["id"], "slug": slug,
                    "title": item["title"], "deps": deps, "risk": "safe",
                    "allowed_paths": item["allowed_paths"], "outputs": item["outputs"],
                    "output_root": "workspace", "instructions": item["acceptance"],
                    "state": "PENDING", "attempts": 0, "max_attempts": 3,
                    "created_at": now(), "updated_at": now(), "last_error": None}
            task_dir = run_dir / "task-packs" / f"{task_id}-{slug}"
            task_dir.mkdir(parents=True, exist_ok=True)
            allowed = "\n".join(f"- `{value}`" for value in item["allowed_paths"])
            outputs = "\n".join(f"- `{value}`" for value in item["outputs"])
            content = f"""# {task_id} — {item['title']}

Promoted from `{item['id']}` after `TP-305` unattended-safety selection.

## Objective

{item['acceptance']}

## Allowed paths

{allowed}

## Required workspace outputs

{outputs}

## Safety and acceptance

- Follow the root `AGENTS.md` authority and product identity.
- Modify only the allowed paths and their necessary package initializers.
- Do not process private audio, publish, deploy, change credentials, change Git
  remotes, delete legacy code, or promote experimental capability.
- Use JSON Schema Draft 2020-12 unless an existing repository convention proves
  another draft authoritative.
- Add focused tests and run the complete `tests/ear_v1_contracts` suite.
- Preserve failure evidence. Do not edit `TASK_LEDGER.json`; the wrapper owns it.
"""
            (task_dir / "TASK.md").write_text(content, encoding="utf-8", newline="\n")
            atomic_json(task_dir / "inputs.json", {"work_item": item, "dependencies": deps})
            atomic_json(task_dir / "acceptance.json", {"output_root": "workspace",
                                                        "required_outputs": item["outputs"], "non_empty": True})
            ledger["tasks"].append(task)
            existing.add(task_id)
            added += 1
        refresh_ready(ledger)
        ledger["updated_at"] = now()
        ledger["phase"] = "implementation"
        atomic_json(path, ledger)
        atomic_json(run_dir / "evidence" / "PROMOTION.json",
                    {"promoted_at": now(), "source": "planning/unattended_batch.json",
                     "selected": len(selected), "added": added, "passed": True})
    print(f"promoted {added} implementation tasks ({len(selected)} selected)")


def re_slug(value: str) -> str:
    import re
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")[:60]


def cmd_validate(args: argparse.Namespace) -> None:
    run_dir = Path(args.run_dir).resolve()
    ledger = read_json(ledger_path(run_dir))
    errors: list[str] = []
    ids = [task["id"] for task in ledger["tasks"]]
    if len(ids) != len(set(ids)):
        errors.append("duplicate task ids")
    known = set(ids)
    for task in ledger["tasks"]:
        if task["state"] not in STATES:
            errors.append(f"{task['id']}: invalid state {task['state']}")
        for dep in task["deps"]:
            if dep not in known:
                errors.append(f"{task['id']}: unknown dependency {dep}")
        if task["id"] in task["deps"]:
            errors.append(f"{task['id']}: self dependency")
    visiting: set[str] = set()
    visited: set[str] = set()
    graph = {task["id"]: task["deps"] for task in ledger["tasks"]}
    def visit(node: str) -> None:
        if node in visiting:
            errors.append(f"dependency cycle at {node}")
            return
        if node in visited:
            return
        visiting.add(node)
        for dep in graph[node]:
            visit(dep)
        visiting.remove(node)
        visited.add(node)
    for node in graph:
        visit(node)
    snapshot = read_json(run_dir / "SOURCE_SNAPSHOT.json")
    source = Path(snapshot["source"])
    for item in snapshot["files"]:
        path = source / Path(item["path"])
        if not path.is_file() or sha256(path) != item["sha256"]:
            errors.append(f"source changed or missing: {item['path']}")
    result = {"checked_at": now(), "passed": not errors, "errors": errors,
              "task_count": len(ids), "source_file_count": len(snapshot["files"])}
    atomic_json(run_dir / "evidence" / "PRECHECK.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(1)


def cmd_claim(args: argparse.Namespace) -> None:
    run_dir = Path(args.run_dir).resolve()
    with RunLock(run_dir):
        path = ledger_path(run_dir)
        ledger = read_json(path)
        refresh_ready(ledger)
        candidates = [task for task in ledger["tasks"] if task["state"] == "READY"]
        if args.task:
            candidates = [task for task in candidates if task["id"] == args.task]
        if not candidates:
            print("NO_READY_TASK")
            return
        task = candidates[0]
        task["state"] = "RUNNING"
        task["attempts"] += 1
        task["updated_at"] = now()
        ledger["updated_at"] = now()
        atomic_json(path, ledger)
    pack = next((run_dir / "task-packs").glob(f"{task['id']}-*"))
    print(json.dumps({"id": task["id"], "title": task["title"], "task_file": str(pack / "TASK.md"),
                      "outputs": task["outputs"], "attempt": task["attempts"]}, ensure_ascii=False, indent=2))


def cmd_complete(args: argparse.Namespace) -> None:
    run_dir = Path(args.run_dir).resolve()
    with RunLock(run_dir):
        path = ledger_path(run_dir)
        ledger = read_json(path)
        task = find_task(ledger, args.task)
        if task["state"] not in {"RUNNING", "VERIFYING"}:
            raise SystemExit(f"{args.task} cannot complete from {task['state']}")
        task["state"] = "VERIFYING"
        passed, checks = verify_outputs(run_dir, task)
        evidence = {"task": task["id"], "verified_at": now(), "passed": passed, "checks": checks}
        atomic_json(run_dir / "evidence" / f"{task['id']}.json", evidence)
        if passed:
            task["state"] = "PASSED"
            task["last_error"] = None
        elif task["attempts"] < task["max_attempts"]:
            task["state"] = "FAILED_RETRYABLE"
            task["last_error"] = "required output verification failed"
        else:
            task["state"] = "BLOCKED_HUMAN"
            task["last_error"] = "verification failed at attempt limit"
        task["updated_at"] = now()
        refresh_ready(ledger)
        ledger["updated_at"] = now()
        atomic_json(path, ledger)
    print(f"{task['id']} -> {task['state']}")


def cmd_builtin(args: argparse.Namespace) -> None:
    """Execute deterministic bootstrap tasks without making scholarly judgments."""
    run_dir = Path(args.run_dir).resolve()
    ledger = read_json(ledger_path(run_dir))
    task = find_task(ledger, args.task)
    if task["state"] == "READY":
        claim_args = argparse.Namespace(run_dir=str(run_dir), task=args.task)
        cmd_claim(claim_args)
        ledger = read_json(ledger_path(run_dir))
        task = find_task(ledger, args.task)
    if task["state"] != "RUNNING":
        raise SystemExit(f"{args.task} is not runnable from {task['state']}")
    snapshot = read_json(run_dir / "SOURCE_SNAPSHOT.json")
    if args.task == "TP-001":
        output = run_dir / "corpus"
        atomic_json(output / "inventory.json", snapshot)
        counts: dict[str, int] = {}
        total = 0
        for item in snapshot["files"]:
            counts[item["extension"] or "<none>"] = counts.get(item["extension"] or "<none>", 0) + 1
            total += item["bytes"]
        lines = ["# Moodify Ear v1 Corpus Inventory", "", f"- Source: `{snapshot['source']}`",
                 f"- Files: **{len(snapshot['files'])}**", f"- Bytes: **{total}**",
                 "- Moodify Ear v2 excluded: **yes**", "", "## Formats", "",
                 "| Extension | Files |", "|---|---:|"]
        lines.extend(f"| `{ext}` | {count} |" for ext, count in sorted(counts.items()))
        lines.extend(["", "Every file path, size, and SHA-256 digest is stored in `inventory.json`.", ""])
        (output / "inventory.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")
    elif args.task == "TP-003":
        output = run_dir / "corpus" / "version_boundaries.md"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            "# Moodify Ear Version Boundaries\n\n"
            "This run is strictly Moodify Ear v1. The top-level directory "
            "`moodify ear 2.0` and every descendant are excluded before hashing, "
            "inventory, extraction, and planning. A v1 file must be present in "
            "`SOURCE_SNAPSHOT.json`; paths not in that immutable snapshot are not "
            "valid inputs. ZIP files are distribution artifacts, not an additional "
            "authority. Duplicate extracted trees remain evidence until TP-002 "
            "resolves source authority. No file is moved, rewritten, or deleted.\n",
            encoding="utf-8", newline="\n")
    else:
        raise SystemExit(f"no deterministic built-in for {args.task}")
    cmd_complete(argparse.Namespace(run_dir=str(run_dir), task=args.task))


def cmd_fail(args: argparse.Namespace) -> None:
    run_dir = Path(args.run_dir).resolve()
    with RunLock(run_dir):
        path = ledger_path(run_dir)
        ledger = read_json(path)
        task = find_task(ledger, args.task)
        if task["state"] != "RUNNING":
            raise SystemExit(f"{args.task} cannot fail from {task['state']}")
        human = args.human or task["risk"] == "human-review"
        task["state"] = "BLOCKED_HUMAN" if human or task["attempts"] >= task["max_attempts"] else "FAILED_RETRYABLE"
        task["last_error"] = args.reason
        task["updated_at"] = now()
        refresh_ready(ledger)
        ledger["updated_at"] = now()
        atomic_json(path, ledger)
    print(f"{task['id']} -> {task['state']}")


def cmd_status(args: argparse.Namespace) -> None:
    run_dir = Path(args.run_dir).resolve()
    ledger = read_json(ledger_path(run_dir))
    counts = {state: 0 for state in sorted(STATES)}
    for task in ledger["tasks"]:
        counts[task["state"]] += 1
    print(json.dumps({"run_id": ledger["run_id"], "updated_at": ledger["updated_at"], "counts": counts,
                      "next_ready": [t["id"] for t in ledger["tasks"] if t["state"] == "READY"]},
                     ensure_ascii=False, indent=2))


def cmd_report(args: argparse.Namespace) -> None:
    run_dir = Path(args.run_dir).resolve()
    ledger = read_json(ledger_path(run_dir))
    lines = ["# Moodify Ear v1 Batch Run Summary", "", f"- Run: `{ledger['run_id']}`",
             f"- Source: `{ledger['source']}`", f"- Updated: `{ledger['updated_at']}`", "", "## Tasks", "",
             "| Task | State | Attempts | Title |", "|---|---:|---:|---|"]
    for task in ledger["tasks"]:
        lines.append(f"| {task['id']} | {task['state']} | {task['attempts']} | {task['title']} |")
    blocked = [task for task in ledger["tasks"] if task["state"] == "BLOCKED_HUMAN"]
    lines.extend(["", "## Human decisions", ""])
    lines.extend([f"- **{task['id']}**: {task['last_error'] or task['title']}" for task in blocked] or ["None."])
    (run_dir / "RUN_SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(run_dir / "RUN_SUMMARY.md")


def cmd_rebase_source(args: argparse.Namespace) -> None:
    """Move a run to another host only when every immutable source hash matches."""
    run_dir = Path(args.run_dir).resolve()
    new_source = Path(args.new_source).resolve()
    if not new_source.is_dir():
        raise SystemExit(f"new source directory not found: {new_source}")
    with RunLock(run_dir):
        snapshot_path = run_dir / "SOURCE_SNAPSHOT.json"
        snapshot = read_json(snapshot_path)
        errors = []
        for item in snapshot["files"]:
            candidate = new_source / Path(item["path"])
            if not candidate.is_file():
                errors.append(f"missing: {item['path']}")
            elif candidate.stat().st_size != item["bytes"] or sha256(candidate) != item["sha256"]:
                errors.append(f"hash mismatch: {item['path']}")
        if errors:
            raise SystemExit("source rebase rejected:\n" + "\n".join(errors[:50]))
        old_source = snapshot["source"]
        snapshot["source"] = str(new_source)
        snapshot["rebased_at"] = now()
        snapshot["rebased_from"] = old_source
        ledger_file = ledger_path(run_dir)
        ledger = read_json(ledger_file)
        ledger["source"] = str(new_source)
        ledger["updated_at"] = now()
        for pack in (run_dir / "task-packs").glob("TP-*"):
            task_file = pack / "TASK.md"
            if task_file.is_file():
                text = task_file.read_text(encoding="utf-8").replace(old_source, str(new_source))
                task_file.write_text(text, encoding="utf-8", newline="\n")
            inputs_file = pack / "inputs.json"
            if inputs_file.is_file():
                inputs = read_json(inputs_file)
                inputs["source"] = str(new_source)
                atomic_json(inputs_file, inputs)
        atomic_json(snapshot_path, snapshot)
        atomic_json(ledger_file, ledger)
        atomic_json(run_dir / "evidence" / "SOURCE_REBASE.json",
                    {"verified_at": now(), "from": old_source, "to": str(new_source),
                     "files_verified": len(snapshot["files"]), "passed": True})
    print(f"rebased source after verifying {len(snapshot['files'])} files: {new_source}")


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init")
    init.add_argument("--source", required=True)
    init.add_argument("--run-dir", required=True)
    init.add_argument("--force", action="store_true")
    init.set_defaults(func=cmd_init)
    for name, func in (("validate", cmd_validate), ("status", cmd_status), ("report", cmd_report)):
        item = commands.add_parser(name)
        item.add_argument("--run-dir", required=True)
        item.set_defaults(func=func)
    claim = commands.add_parser("claim")
    claim.add_argument("--run-dir", required=True)
    claim.add_argument("--task")
    claim.set_defaults(func=cmd_claim)
    complete = commands.add_parser("complete")
    complete.add_argument("--run-dir", required=True)
    complete.add_argument("--task", required=True)
    complete.set_defaults(func=cmd_complete)
    builtin = commands.add_parser("builtin")
    builtin.add_argument("--run-dir", required=True)
    builtin.add_argument("--task", required=True, choices=["TP-001", "TP-003"])
    builtin.set_defaults(func=cmd_builtin)
    fail = commands.add_parser("fail")
    fail.add_argument("--run-dir", required=True)
    fail.add_argument("--task", required=True)
    fail.add_argument("--reason", required=True)
    fail.add_argument("--human", action="store_true")
    fail.set_defaults(func=cmd_fail)
    rebase = commands.add_parser("rebase-source")
    rebase.add_argument("--run-dir", required=True)
    rebase.add_argument("--new-source", required=True)
    rebase.set_defaults(func=cmd_rebase_source)
    promote = commands.add_parser("promote")
    promote.add_argument("--run-dir", required=True)
    promote.set_defaults(func=cmd_promote)
    return root


def main() -> None:
    args = parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
