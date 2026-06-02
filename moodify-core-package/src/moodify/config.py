"""Moodify central configuration.

Provides PROJECT_ROOT and output directory resolution.
All hardcoded paths should use these helpers instead.
"""

from __future__ import annotations

import os
from pathlib import Path


def get_project_root() -> Path:
    """Resolve project root.

    Priority:
        1. MOODIFY_ROOT env var
        2. Walk upward from this file until .git is found
        3. Fallback: parent of moodify package
    """
    env = os.environ.get("MOODIFY_ROOT", "").strip()
    if env:
        root = Path(env).expanduser().resolve()
        if root.exists():
            return root

    # Walk up from this file
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / ".git").exists():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent

    # Fallback: package parent
    return Path(__file__).resolve().parent.parent


def get_output_dir(default: str = "outputs") -> Path:
    """Resolve output directory."""
    env = os.environ.get("MOODIFY_OUTPUT", "").strip()
    if env:
        return Path(env).expanduser()
    return get_project_root() / default


def get_test_audio_dir() -> Path:
    """Resolve test audio directory."""
    env = os.environ.get("MOODIFY_TEST_AUDIO", "").strip()
    if env:
        return Path(env).expanduser()
    return get_project_root() / "tests" / "baseline" / "test_audio"


PROJECT_ROOT = get_project_root()
OUTPUT_ROOT = get_output_dir()
TEST_AUDIO_DIR = get_test_audio_dir()
