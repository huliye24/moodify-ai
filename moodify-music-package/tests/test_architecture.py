"""Architecture guard tests — Music must never import Ear internals.

MFY_PRODUCT_BOUNDARY_AND_SHARED_CONTRACTS_001: Music 与 Ear 边界守护。
"""

from __future__ import annotations

import ast
import os
import re
import sys

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
    assert not violations, f"boundary violations:\n" + "\n".join(violations)


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
    assert not violations, f"moodify (Ear) imports in Music package:\n" + "\n".join(violations)


def test_no_ear_database_credentials_in_music_config():
    # Music config must not carry Ear SQLite paths or Ear node state
    config = open(os.path.join(PACKAGE_ROOT, "moodify_music", "config.py"), encoding="utf-8").read()
    for token in ["node.sqlite3", "state_dir", "MOODIFY_NODE_STATE_DIR", "moodify-ear"]:
        assert token not in config, f"config.py references Ear storage: {token}"
