"""W01-P01 Canon drift guard tests — README/AGENTS/docs-canon authority checks."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(REPO_ROOT / "scripts"))

import canon_guard  # noqa: E402


def test_guard_passes_on_current_repo():
    errors = canon_guard.check(REPO_ROOT)
    assert errors == [], f"canon guard violations: {errors}"


def test_readme_and_agents_declare_external_product():
    for rel in ("README.md", "AGENTS.md"):
        text = (REPO_ROOT / rel).read_text(encoding="utf-8")
        head = "\n".join(text.splitlines()[:60])
        assert any(p in head for p in canon_guard.ALLOWED_PRODUCT_LINES), f"{rel} missing product identity"


def test_guard_catches_ear_as_product_regression():
    class FakeFiles(dict):
        pass

    fake = {
        "README.md": "# Moodify\n\n> Moodify is The Ear of AI — an Auditory Intelligence System.\n" + "\n" * 50,
        "AGENTS.md": "# AGENTS\n\nMoodify is The Ear of AI — an Auditory Intelligence System.\n" + "\n" * 50,
        "docs/canon/CURRENT_CANON.md": "Moodify Music\nCANON_CHANGE = YES\n",
        "docs/canon/AUTHORITY_ORDER.md": "docs/canon\n",
        "docs/canon/PRODUCT_BOUNDARY.md": "Moodify Music\n",
        "docs/canon/INTERNAL_SYSTEMS.md": "Moodify Ear\n",
        "docs/canon/CURRENT_ARCHITECTURE.md": "x\n",
        "docs/REPOSITORY_STATUS.md": "Moodify Music\n",
    }
    errors = canon_guard.check_files(fake)
    assert any("forbidden Ear-as-product" in e for e in errors)


def test_guard_accepts_one_core_two_interfaces_identity():
    """Canon v1.2 身份（One Core / Two Interfaces）必须通过守卫。"""
    fake = {
        "README.md": "# Moodify\n\n**One Core, Two Interfaces — Production CLI + Listening App**\n" + "\n" * 50,
        "AGENTS.md": "**External product:** Moodify — 一个 Core，两个接口（one Core, two interfaces）。\n" + "\n" * 50,
        "docs/canon/CURRENT_CANON.md": "One Core, Two Interfaces\nCANON_CHANGE = YES\n",
        "docs/canon/AUTHORITY_ORDER.md": "docs/canon\n",
    }
    assert canon_guard.check_files(fake) == []


def test_guard_fails_without_identity_marker():
    """高权威文件完全不含对外身份标记时必须报错。"""
    fake = {
        "README.md": "# Something else entirely\n" + "\n" * 50,
        "AGENTS.md": "# AGENTS\n" + "\n" * 50,
        "docs/canon/CURRENT_CANON.md": "CANON_CHANGE = YES\n",
        "docs/canon/AUTHORITY_ORDER.md": "docs/canon\n",
    }
    errors = canon_guard.check_files(fake)
    assert any("no external product identity" in e for e in errors)
