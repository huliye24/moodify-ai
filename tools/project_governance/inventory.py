"""Workspace change inventory — bucket every change without moving files.

Buckets (023 Stage B):
- product_code  : src/ changes (moodify-core-package, moodify_runtime, workers)
- tests         : test files
- documentation : docs/, README, CHANGELOG
- analytics     : project_analytics/, reports/
- generated     : outputs/, artifacts/, __pycache__, .pytest_cache
- unknown       : anything not classifiable — stays UNKNOWN, never deleted

Untracked directory entries are expanded to file counts so one entry does
not hide hundreds of files. The inventory is a timestamped snapshot; it never
rewrites history.
"""

from __future__ import annotations

import datetime
import json
import subprocess
from pathlib import Path

GIT = r"C:\Program Files\Git\cmd\git.exe"
ROOT = Path(__file__).resolve().parents[2]


def _git(args: list[str]) -> str:
    # core.quotepath=false: git outputs non-ASCII paths as raw UTF-8,
    # avoiding \NNN octal quoting entirely
    proc = subprocess.run(
        [GIT, "-C", str(ROOT), "-c", "core.quotepath=false", *args],
        capture_output=True,
    )
    return proc.stdout.decode("utf-8", errors="replace")


def _bucket_for(path: str, is_dir: bool) -> str:
    # strip quoting; quotepath=false already yields raw UTF-8
    p = path.strip().strip('"').replace("\\", "/")
    if p.startswith(("moodify-core-package/src/", "moodify_runtime/", "workers/", "moodify-bridge/",
                     "moodify-core-package/pyproject.toml", "scripts/", "tools/",
                     "moodify-core-package/capability_registry.json")):
        if "/tests/" in p or p.endswith(("test_", "tests/")) or "test_" in p.split("/")[-1] or "tests/" in p:
            return "tests"
        return "product_code"
    if p.startswith(("moodify-core-package/tests/", "tests/", "moodify-core-package/tools/")):
        return "tests"
    if p.startswith(("docs/", "README", "CHANGELOG", ".gitignore", "moodify-core-package/docs/",
                     "moodify-core-package/MOODIFY_INTENT.md", "PROJECT_ROADMAP.md")):
        return "documentation"
    if p.startswith(("project_analytics/", "reports/", "schemas/", "treatment_records/")):
        return "analytics"
    if p.startswith(("outputs/", "output/", "artifacts/", "tmp/", "scratch/", "moodify-core-package/src/moodify.egg-info/")) or is_dir and any(
        k in p for k in ("__pycache__", ".pytest_cache", ".idea", ".codex-work", "egg-info")
    ):
        return "generated"
    if p.startswith(".idea/"):
        return "generated"
    if p.startswith(("pre-music/", "local_audio_assets/")):
        return "audio_assets"
    if p.startswith(("apps/", "deliverables/", "video/", "RJWC_VideoPack_System/")):
        return "business_assets"
    if p.startswith(("science/", "研究论文/", "实验图库/", "投资ppt/")):
        return "research_assets"
    if p.startswith("configs/"):
        return "configuration"
    if p.startswith(("android-studio-quail2-windows.exe",)):
        return "tool_installer"
    return "UNKNOWN"


def _file_count(directory: Path) -> int:
    return sum(1 for _ in directory.rglob("*") if _.is_file())


def build_inventory(stamp: str | None = None) -> dict:
    stamp = stamp or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    status = _git(["status", "--porcelain"])
    entries = []
    for line in status.splitlines():
        if not line.strip():
            continue
        flag = line[:2]
        path = line[3:]
        is_dir = False
        if flag == "??" and (ROOT / path).is_dir():
            is_dir = True
            file_count = _file_count(ROOT / path)
        else:
            file_count = 1
        bucket = _bucket_for(path, is_dir)
        entries.append({
            "path": path,
            "flag": flag,
            "tracked": flag != "??",
            "is_dir": is_dir,
            "file_count": file_count,
            "bucket": bucket,
            "owner": "UNASSIGNED",
            "validation": "NOT_VALIDATED",
            "risk": "low" if bucket == "generated" else ("medium" if bucket != "UNKNOWN" else "high"),
            "recommended_action": "review" if bucket != "generated" else "keep-as-generated",
        })
    return {
        "schema": "moodify.workspace-inventory/0.1",
        "stamp": stamp,
        "entries": entries,
        "summary": {
            "total_entries": len(entries),
            "tracked": sum(1 for e in entries if e["tracked"]),
            "untracked": sum(1 for e in entries if not e["tracked"]),
            "buckets": {b: sum(1 for e in entries if e["bucket"] == b) for b in sorted({e["bucket"] for e in entries})},
            "unknown": sum(1 for e in entries if e["bucket"] == "UNKNOWN"),
        },
    }


def save_inventory(target: Path) -> dict:
    inventory = build_inventory()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(inventory, ensure_ascii=False, indent=2), encoding="utf-8")
    return inventory


def main() -> int:
    target = ROOT / "project_analytics" / "workspace_inventory.json"
    inventory = save_inventory(target)
    print(f"inventory: {target}")
    summary = inventory["summary"]
    print(f"  entries: {summary['total_entries']}  tracked: {summary['tracked']}  untracked: {summary['untracked']}")
    for bucket, count in summary["buckets"].items():
        print(f"  {bucket:15s} {count}")
    print(f"  UNKNOWN: {summary['unknown']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
