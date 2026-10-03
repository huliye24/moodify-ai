#!/usr/bin/env python3
"""Repository structure guard for Moodify.

Prevents the structural conditions that MOODIFY_NETWORK_RESTRUCTURE_001 removed
from reappearing. Every check here corresponds to a real defect documented in
docs/restructure/CLEANUP_MANIFEST.md — this is not a style linter.

Run locally:
    python scripts/check_repo_structure.py

Exit code 0 = clean, 1 = one or more violations.

Deliberately stdlib-only: it must run in CI before any dependency install, and it
must not be able to break because a package is missing.

Rationale for each rule is in RULES below and in GOVERNANCE.md, MAINTAINERS.md,
and protocol/schemas/README.md (the schema owner map).
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


# ── tracked-file helpers ────────────────────────────────────────────────


def tracked_files() -> list[str]:
    """Every path tracked by git, relative to the repo root.

    Uses `git ls-files` rather than walking the filesystem on purpose: the guard
    governs what is *in the repository*, and several retired directories are
    deliberately still present on disk but untracked.
    """
    # encoding is pinned to UTF-8, not text=True. This repository contains
    # non-ASCII paths, and `text=True` decodes with the *locale* codec — on a
    # Chinese Windows machine that is GBK, which raises UnicodeDecodeError and
    # takes the guard down locally while still passing in CI. This repo has hit
    # the same GBK trap before (see docs/REPOSITORY_STATUS.md history), so the
    # encoding is stated explicitly rather than left to the environment.
    out = subprocess.run(
        ["git", "-c", "core.quotepath=false", "ls-files"],
        cwd=REPO_ROOT,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )
    return [line for line in out.stdout.splitlines() if line.strip()]


# ── rules ───────────────────────────────────────────────────────────────

# Retired top-level paths. Each was removed for a documented reason; recreating
# one means a decision recorded in CLEANUP_MANIFEST.md is being silently undone.
# To intentionally bring one back, change this list in the same PR and cite the
# MIP or human decision that authorises it.
RETIRED_PATHS: dict[str, str] = {
    "web 3.0/": "MOOD/Web3 project line — untracked, kept on disk (see docs/ARCHIVE_INDEX.md)",
    "mood-web3-protocol/": "MOOD/Web3 protocol — untracked, kept on disk",
    "moodify-qa/": "retired second product identity; capability lives in Core auditory/",
    "moodify-qa-desktop/": "retired third desktop shell",
    "moodify-pulse/": "retired fourth product identity; superseded by moodify-desktop/",
    "windows版本开发/": "historical MFD work packages, superseded by moodify-desktop/",
    "审查包/": "audit corpus; authority evidence now in docs/evidence/",
    "products/": "empty product scaffolds — QA/Master/Rating/Supply are not products",
    "shared/": "empty migration-map shells; capabilities live in Core",
    "sdk/": "placeholder SDK superseded by Core's public surfaces",
    "plugins/": "unbuilt plugin surface with no live wiring",
    "engine/": "facade that reversed the dependency direction — second Core",
    "demo/": "duplicate pipeline; Core's `moodify analyze` is canonical",
    "phys-lab/": "launcher for Core's moodify.physics",
    "工程经验层/": "engineering constraints moved to docs/governance/constraints/",
    "moodify-app/": "untracked workspace copy",
}

# Top-level directories whose names are Chinese task-package labels. The
# repository's own task packages belong under docs/, not at the root.
CJK_TOP_LEVEL_RE = re.compile(r"^[^\x00-\x7F]")

# Generated artifacts must never be committed. Matches by extension or basename.
GENERATED_SUFFIXES = (
    ".pyc", ".pyo", ".class", ".jar", ".apk", ".aab", ".exe", ".msi",
    ".dll", ".so", ".dylib", ".o", ".a", ".zip", ".tar", ".gz", ".7z",
    ".whl", ".egg",
)
GENERATED_DIR_NAMES = {
    "node_modules", "__pycache__", ".pytest_cache", ".ruff_cache",
    ".mypy_cache", "dist", "dist-electron", "build", ".gradle", ".next",
}

# Committed build infrastructure that happens to use a generated-looking
# extension. The Gradle wrapper JAR is checked in by design — the build cannot
# bootstrap without it. Exempted by exact basename, not by loosening the rule.
BUILD_INFRASTRUCTURE_BASENAMES = {"gradle-wrapper.jar"}

# Only one package may claim the `moodify` console command.
MOODIFY_COMMAND = "moodify"

# The canonical Core.
CANONICAL_CORE = "moodify-core-package/"

# Top-level directories permitted to own Python source. Anything else with .py
# files is a candidate second Core and must be justified.
#
# Explicit list rather than a heuristic: "does this look like a Core?" is not a
# decidable question, and a fuzzy check either misses real duplicates or fails on
# legitimate ones. Each entry here is a tree the 2026-10-03 audit examined and
# deliberately kept, so adding a new entry is a decision, not a formality.
ALLOWED_PYTHON_TREES = {
    "moodify-core-package",     # the Core
    "moodify-music-package",    # music-domain API (schema authority, 19 tests)
    "moodify-desktop",          # Electron Studio shell (+ helper scripts)
    "moodify_runtime",          # commerce/private-audio — migration pending
    "apps",                     # clients; ear-workbench/dev_proxy.py is a dev proxy
    "ops",                      # deployment and node operation
    "scripts",                  # repository tooling
    "tools",                    # temporal-texture guard
    "tests",                    # root integration tests, run by CI
    "examples",
    "benchmark",
    "research",
    "docs",
    "data",
    "deployment",
    "security",
}


def _is_generated(path: str) -> str | None:
    """Return a reason string if the path looks like a generated artifact."""
    parts = path.split("/")
    for part in parts[:-1]:
        if part in GENERATED_DIR_NAMES:
            return f"inside generated directory '{part}/'"
    name = parts[-1]
    if name in BUILD_INFRASTRUCTURE_BASENAMES:
        return None
    for suffix in GENERATED_SUFFIXES:
        if name.endswith(suffix):
            return f"generated artifact extension '{suffix}'"
    return None


def _declared_scripts(pyproject: Path) -> dict[str, str]:
    """Parse [project.scripts] from a pyproject.toml without tomllib/tomli.

    Kept dependency-free and deliberately simple: this needs to read a handful of
    key = "value" lines, not implement TOML.
    """
    scripts: dict[str, str] = {}
    try:
        text = pyproject.read_text(encoding="utf-8")
    except OSError:
        return scripts

    in_section = False
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if line.lstrip().startswith("["):
            in_section = line.strip() == "[project.scripts]"
            continue
        if in_section and "=" in line:
            key, _, value = line.partition("=")
            scripts[key.strip().strip('"').strip("'")] = value.strip().strip('"').strip("'")
    return scripts


def check_retired_paths(files: list[str]) -> list[str]:
    problems = []
    for retired, reason in RETIRED_PATHS.items():
        hits = [f for f in files if f.startswith(retired) or f == retired.rstrip("/")]
        if hits:
            problems.append(
                f"retired path re-tracked: '{retired}' ({len(hits)} file(s)) — {reason}\n"
                f"    first: {hits[0]}\n"
                f"    If this is intentional, remove the entry from RETIRED_PATHS in "
                f"scripts/check_repo_structure.py and cite the authorising MIP or human decision."
            )
    return problems


def check_cjk_top_level(files: list[str]) -> list[str]:
    """Top-level task-package directories with non-ASCII names."""
    allow = {"docs"}
    tops = {f.split("/")[0] for f in files if "/" in f}
    problems = []
    for top in sorted(tops):
        if top in allow:
            continue
        if CJK_TOP_LEVEL_RE.match(top):
            problems.append(
                f"top-level directory with a non-ASCII task-package name: '{top}/'\n"
                f"    Moodify mainline task packages belong under docs/, not at the repository root."
            )
    return problems


def check_generated_artifacts(files: list[str]) -> list[str]:
    problems = []
    for path in files:
        reason = _is_generated(path)
        if reason:
            problems.append(
                f"generated artifact is tracked: '{path}' ({reason})\n"
                f"    Generated output must not enter git. See .gitignore."
            )
    return problems


def check_moodify_command(files: list[str]) -> list[str]:
    """Exactly one *tracked* package may declare the `moodify` console command.

    Restricted to tracked files on purpose. Several retired trees still exist on
    disk but are no longer in the repository; a filesystem walk would report the
    untracked stale fork `_github_moodify_ai/moodify-core-package/` as a live
    conflict, which it is not (and cannot be fixed by a git-tracked change).
    """
    tracked_pyprojects = [f for f in files if f.endswith("pyproject.toml")]

    claimants: list[str] = []
    for rel in sorted(tracked_pyprojects):
        scripts = _declared_scripts(REPO_ROOT / rel)
        if MOODIFY_COMMAND in scripts:
            claimants.append(f"{rel} -> {scripts[MOODIFY_COMMAND]}")

    if len(claimants) > 1:
        return [
            f"{len(claimants)} tracked packages declare the '{MOODIFY_COMMAND}' console command:\n"
            + "\n".join(f"    {c}" for c in claimants)
            + "\n    Installing more than one makes the command resolve by install order. "
            "This exact collision existed before (moodify-core-package vs demo)."
        ]
    if not claimants:
        return [
            f"no tracked package declares the '{MOODIFY_COMMAND}' console command.\n"
            f"    The canonical declaration is {CANONICAL_CORE}pyproject.toml."
        ]
    return []


def check_second_core(files: list[str]) -> list[str]:
    """No top-level Python source tree outside the explicit allowlist."""
    tops_with_python = {f.split("/")[0] for f in files if f.endswith(".py") and "/" in f}
    unexpected = sorted(tops_with_python - ALLOWED_PYTHON_TREES)
    if unexpected:
        return [
            "Python source at a top-level path that is not on the allowlist: "
            + ", ".join(f"'{c}/'" for c in unexpected)
            + f"\n    The canonical Core is {CANONICAL_CORE} (One Core, Multiple Interfaces)."
            + "\n    If this tree is legitimate, add it to ALLOWED_PYTHON_TREES in "
            "scripts/check_repo_structure.py and say why in the commit message."
        ]
    return []


# ── entry point ─────────────────────────────────────────────────────────


def main() -> int:
    # Console encoding is not guaranteed to be UTF-8 (Chinese Windows defaults to
    # GBK, which cannot encode the em-dashes below). Without this, the guard can
    # raise UnicodeEncodeError while *reporting* a failure — the same locale trap
    # that already bit this repository once.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    files = tracked_files()
    all_problems: list[str] = []

    checks = (
        ("retired paths", check_retired_paths(files)),
        ("top-level naming", check_cjk_top_level(files)),
        ("generated artifacts", check_generated_artifacts(files)),
        ("console entry points", check_moodify_command(files)),
        ("single Core", check_second_core(files)),
    )

    for label, problems in checks:
        if problems:
            all_problems.append(f"[{label}]")
            all_problems.extend(problems)

    if all_problems:
        print(f"Repository structure guard FAILED ({len(files)} tracked files)\n")
        print("\n".join(all_problems))
        print(
            "\nSee docs/restructure/CLEANUP_MANIFEST.md for why each rule exists, "
            "and GOVERNANCE.md for how to change them legitimately."
        )
        return 1

    print(f"Repository structure guard: OK ({len(files)} tracked files, {len(checks)} checks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
