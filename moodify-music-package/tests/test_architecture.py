"""Architecture guard tests — Music must never import Ear internals.

MFY_PRODUCT_BOUNDARY_AND_SHARED_CONTRACTS_001: Music 与 Ear 边界守护。
"""

from __future__ import annotations

import ast
import os
import re

PACKAGE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))


def _iter_py_files(root: str):
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in filenames:
            if name.endswith(".py"):
                yield os.path.join(dirpath, name)


FORBIDDEN_IMPORTS = [
    "moodify.auditory",
    "moodify.orchestration",
    "moodify.intervention",
    "moodify.node.db",
    "moodify.node.queue",
]
ALLOWED_MOODIFY_REFS = [
    "moodify_music",  # self
]


def test_music_never_imports_ear_internals():
    violations = []
    for path in _iter_py_files(PACKAGE_ROOT):
        src = open(path, encoding="utf-8").read()
        for node in ast.walk(ast.parse(src)):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    for forbidden in FORBIDDEN_IMPORTS:
                        if alias.name == forbidden or alias.name.startswith(forbidden + "."):
                            violations.append(f"{os.path.relpath(path, PACKAGE_ROOT)}: imports {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    for forbidden in FORBIDDEN_IMPORTS:
                        if node.module == forbidden or node.module.startswith(forbidden + "."):
                            violations.append(f"{os.path.relpath(path, PACKAGE_ROOT)}: from {node.module} import")
    assert not violations, "boundary violations:\n" + "\n".join(violations)


def test_music_does_not_import_ear_package_at_all():
    # moodify_music must not import the `moodify` top-level package (Ear) anywhere
    violations = []
    for path in _iter_py_files(PACKAGE_ROOT):
        src = open(path, encoding="utf-8").read()
        for node in ast.walk(ast.parse(src)):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "moodify" or alias.name.startswith("moodify."):
                        violations.append(f"{os.path.relpath(path, PACKAGE_ROOT)}: imports {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                if node.module and (node.module == "moodify" or node.module.startswith("moodify.")):
                    violations.append(f"{os.path.relpath(path, PACKAGE_ROOT)}: from {node.module} import")
    assert not violations, "moodify (Ear) imports in Music package:\n" + "\n".join(violations)


def test_no_ear_database_credentials_in_music_config():
    # Music config must not carry Ear SQLite paths or Ear node state
    config = open(os.path.join(PACKAGE_ROOT, "moodify_music", "config.py"), encoding="utf-8").read()
    for token in ["node.sqlite3", "state_dir", "MOODIFY_NODE_STATE_DIR", "moodify-ear"]:
        assert token not in config, f"config.py references Ear storage: {token}"


# --- MFY_PRODUCT_GOVERNANCE_FREEZE_001: identity regression guard ---

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
# Forbidden identity claims, matched per line. Each entry may carry a list of
# negation anchors: a line that contains a negation anchor is accepted.
FORBIDDEN_CLAIMS = [
    # "Moodify is an automatic-mastering product" (identity claim)
    (r"automatic\s+mastering", ["not", "no", "never", "不得", "不是", "退化"]),
    (r"自动母带", ["不是", "不得", "退化", "禁止", "永不"]),
    # "the loop is fully machine-operated / machine has unlimited final authority"
    (r"fully\s+machine[- ]operated", ["not", "no"]),
    (r"machine\s+(has|holds)\s+unlimited\s+(final\s+)?authority", ["not", "no", "never"]),
]
AUTHORITY_ENTRIES = [
    os.path.join(REPO_ROOT, "README.md"),
    os.path.join(REPO_ROOT, "AGENTS.md"),
    os.path.join(REPO_ROOT, "docs", "PHASE1_CONSTITUTION.md"),
]


def test_no_forbidden_product_identity_claims():
    # Governance freeze: authority entries must never claim Moodify is an
    # automatic-mastering product or that machines hold unlimited authority.
    violations = []
    for path in AUTHORITY_ENTRIES:
        if not os.path.isfile(path):
            violations.append(f"missing authority entry: {os.path.relpath(path, REPO_ROOT)}")
            continue
        for lineno, line in enumerate(
            open(path, encoding="utf-8", errors="replace").read().splitlines(), 1
        ):
            lowered = line.lower()
            for pattern, negations in FORBIDDEN_CLAIMS:
                if re.search(pattern, lowered):
                    if not any(neg in lowered for neg in negations):
                        violations.append(
                            f"{os.path.relpath(path, REPO_ROOT)}:{lineno}: {line.strip()}"
                        )
    assert not violations, "forbidden identity claims in authority entries:\n" + "\n".join(violations)
