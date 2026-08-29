#!/usr/bin/env python3
"""Moodify Canon drift guard — W01-P01.

低成本权威守卫：防止高权威文件再次把 Ear 定义为对外一级产品，
或出现相互冲突的对外产品身份。只读检查，不修改任何文件。

用法:
    python scripts/canon_guard.py            # 检查仓库根（自动定位）
    python scripts/canon_guard.py <repo_root>
退出码: 0 = 通过; 1 = 失败
"""

from __future__ import annotations

import sys
from pathlib import Path

AUTHORITY_FILES = [
    "README.md",
    "AGENTS.md",
    "docs/canon/CURRENT_CANON.md",
    "docs/canon/PRODUCT_BOUNDARY.md",
    "docs/canon/INTERNAL_SYSTEMS.md",
    "docs/canon/AUTHORITY_ORDER.md",
    "docs/canon/CURRENT_ARCHITECTURE.md",
    "docs/REPOSITORY_STATUS.md",
]

REQUIRED_CANON_FILES = [
    "docs/canon/CURRENT_CANON.md",
    "docs/canon/PRODUCT_BOUNDARY.md",
    "docs/canon/INTERNAL_SYSTEMS.md",
    "docs/canon/AUTHORITY_ORDER.md",
    "docs/canon/CURRENT_ARCHITECTURE.md",
    "docs/canon/CANON_CHANGELOG.md",
]

# 对外一级产品身份允许的表述（首身份位置附近可接受的产品行）
ALLOWED_PRODUCT_LINES = [
    "Moodify Music",
    "Moodify Player",
    "Moodify Music / Player",
    "Moodify Music / Moodify Player",
]

# 高权威文件内禁止的"Ear 作为对外一级产品"表述模式
# （Ear 作为内部系统出现是合法的，这里只拦"产品身份/对外"语境）
FORBIDDEN_EAR_PRODUCT_PATTERNS = [
    "The Ear of AI is Moodify",
    "Moodify is The Ear of AI",
    "Moodify is an Auditory Intelligence System",
    "Moodify is The Ear of AI — an Auditory Intelligence System",
]


def load(root: Path) -> dict[str, str]:
    files: dict[str, str] = {}
    for rel in AUTHORITY_FILES:
        p = root / rel
        files[rel] = p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""
    return files


def check_files(files: dict[str, str]) -> list[str]:
    """纯文本检查（便于测试注入）: files 为相对路径 -> 内容。"""
    errors: list[str] = []

    # 2. README / AGENTS 顶部（前 60 行）必须出现对外产品身份，且禁止 Ear-as-product 模式
    for rel in ("README.md", "AGENTS.md"):
        head = "\n".join(files.get(rel, "").splitlines()[:60])
        if not any(pat in head for pat in ALLOWED_PRODUCT_LINES):
            errors.append(f"{rel}: no external product identity (Moodify Music/Player) in first 60 lines")
        for pat in FORBIDDEN_EAR_PRODUCT_PATTERNS:
            if pat in head:
                errors.append(f"{rel}: forbidden Ear-as-product pattern: {pat!r}")

    # 3. 高权威文件内不允许并列对外一级身份（README/AGENTS 首身份行）
    #    允许 "INTERNAL" 语境下的 Ear 表述；禁止把 Ear 放在"对外产品身份"位置。
    for rel in ("README.md", "AGENTS.md"):
        for line in files.get(rel, "").splitlines()[:60]:
            if "The Ear of AI" in line and "internal" not in line.lower() and "内部" not in line:
                errors.append(f"{rel}:{line!r} mentions The Ear of AI in first 60 lines without INTERNAL framing")

    # 4. CURRENT_CANON 必须声明唯一对外身份与 Canon change rule
    cc = files.get("docs/canon/CURRENT_CANON.md", "")
    if "Moodify Music" not in cc:
        errors.append("docs/canon/CURRENT_CANON.md: missing external identity Moodify Music")
    if "CANON_CHANGE = YES" not in cc:
        errors.append("docs/canon/CURRENT_CANON.md: missing CANON_CHANGE rule")

    # 5. 权威顺序文件必须包含 docs/canon 层级
    ao = files.get("docs/canon/AUTHORITY_ORDER.md", "")
    if "docs/canon" not in ao:
        errors.append("docs/canon/AUTHORITY_ORDER.md: missing docs/canon authority level")

    return errors


def check(root: Path) -> list[str]:
    errors: list[str] = []
    files = load(root)

    # 1. 必需的 canon 文件存在
    for rel in REQUIRED_CANON_FILES:
        if not (root / rel).exists():
            errors.append(f"missing canon file: {rel}")

    errors.extend(check_files(files))
    return errors


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
    errors = check(root)
    if errors:
        print("CANON GUARD FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("CANON GUARD PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
