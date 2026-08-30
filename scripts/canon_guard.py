#!/usr/bin/env python3
"""Moodify Canon drift guard — W01-P01 + MOOD FOUNDATION 011.

低成本权威守卫：
1. W01-P01：防止高权威文件再次把 Ear 定义为对外一级产品，
   或出现相互冲突的对外产品身份。
2. MOOD FOUNDATION 011：防止 MOOD 总体身份被错误描述为「单一 Token」，
   或在公共文件中出现未经批准的 Buy / Trade MOOD CTA。

只读检查，不修改任何文件。

用法:
    python scripts/canon_guard.py            # 检查仓库根（自动定位）
    python scripts/canon_guard.py <repo_root>
退出码: 0 = 通过; 1 = 失败
"""

from __future__ import annotations

import re
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
    "docs/canon/CANON_CHANGELOG.md",
    "docs/REPOSITORY_STATUS.md",
    # MOOD FOUNDATION 011 — MOOD 总体身份文档
    "docs/mood/CURRENT_CANON.md",
    "docs/mood/SYSTEM_ARCHITECTURE.md",
    "docs/mood/PRODUCT_RELATIONSHIP.md",
    "docs/mood/ASSET_CLASSIFICATION.md",
    "docs/mood/IN_FLIGHT_CHANGE_REGISTER.md",
    "docs/mood/TOKEN_LAUNCH_GATE.md",
    "docs/mood/SEPTEMBER_BUILD_ROADMAP.md",
    "docs/mood/DECISION_LOG.md",
]

REQUIRED_CANON_FILES = [
    "docs/canon/CURRENT_CANON.md",
    "docs/canon/PRODUCT_BOUNDARY.md",
    "docs/canon/INTERNAL_SYSTEMS.md",
    "docs/canon/AUTHORITY_ORDER.md",
    "docs/canon/CURRENT_ARCHITECTURE.md",
    "docs/canon/CANON_CHANGELOG.md",
]

REQUIRED_MOOD_FILES = [
    "docs/mood/CURRENT_CANON.md",
    "docs/mood/SYSTEM_ARCHITECTURE.md",
    "docs/mood/PRODUCT_RELATIONSHIP.md",
    "docs/mood/ASSET_CLASSIFICATION.md",
    "docs/mood/IN_FLIGHT_CHANGE_REGISTER.md",
    "docs/mood/TOKEN_LAUNCH_GATE.md",
    "docs/mood/SEPTEMBER_BUILD_ROADMAP.md",
    "docs/mood/DECISION_LOG.md",
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

# MOOD FOUNDATION 011 — MOOD 反 Token 反模式
# 高权威文件不应把 MOOD 描述为「单一 Token / 已发币产品」
# （MOOD = WORLD + PROTOCOL + PORTAL；Token 是 future economic layer）
FORBIDDEN_MOOD_AS_TOKEN_PATTERNS = [
    "MOOD is a token",
    "MOOD is the token",
    "MOOD is a single token",
    "MOOD Token is the product",
    "MOOD Token is Moodify",
    "Moodify is MOOD Token",
    "the MOOD product is the token",
]

# 公共文件位置（UI / marketing / public docs）出现未经批准的 Buy / Trade CTA
# 仅检测 README/AGENTS / 公共 brand / mood docs；具体 UI 检测留待后续 canon-guard-ui。
FORBIDDEN_BUY_TRADE_CTA_PATTERNS = [
    "Buy MOOD",
    "Trade MOOD",
    "Buy MOOD Token",
    "Trade MOOD Token",
    "Purchase MOOD",
]

# 公共文件路径前缀：默认仅在 README/AGENTS/canon/brand/mood 中检查
PUBLIC_PATH_PREFIXES = (
    "README.md",
    "AGENTS.md",
    "docs/canon/",
    "docs/brand/",
    "docs/mood/",
    "docs/REPOSITORY_STATUS.md",
)

# Buy/Trade MOOD CTA 检测：允许在描述禁止上下文中出现（如「禁止 Buy MOOD」）
# 只在非 docs/mood/ 路径中严格检查（mood 文档本身会描述禁令）
# 在 docs/mood/ 中，仅检测未加禁令标记的裸 CTA


def is_forbidden_cta(line: str) -> bool:
    """判断一行是否包含禁止的 Buy/Trade MOOD CTA（非描述）。"""
    line_lower = line.lower()
    cta_markers = ["buy mood", "trade mood", "purchase mood"]
    for marker in cta_markers:
        if marker in line_lower:
            # 如果行中包含禁令关键词（中文或英文），认为是描述不是 CTA
            forbid_markers = [
                "禁止", "禁", "❌", "✗", "freez", "gate", "pending",
                "not ", "do not", "don't", "must not", "never",
                "should not", "not_activated", "not activated",
                "不允许", "不展示", "不出现", "不暴露",
                "无", "none", "no ", "without",
                "blocked",
                "检测",  # 描述检测功能，不是真实 CTA
                "human_decision", "h.d.",
                "humen", "cta 的", "cta的",
                "cta 应", "cta should", "cta must",
                "是否存在", "should detect",
                # bullet 下的禁止列表项（如 "- 任何...Buy MOOD CTA 的提交"）
                "任何引入", "任何把", "任何将",
                "禁止 cherry-pick",
                "提交的", "声明的",
            ]
            # 检查行中是否存在任何禁令标记
            if any(fm in line_lower for fm in forbid_markers):
                return False
            # 检查行中是否存在中文禁令标记（不转小写）
            forbid_cn = [
                "禁止", "禁", "❌", "✗", "不允许", "不展示", "不出现", "不暴露",
                "待", "待定", "CTA 的", "是否存在",
                "任何引入", "任何把", "任何将",
                "的提交", "提交的", "的处置",
            ]
            if any(fm in line for fm in forbid_cn):
                return False
            # 描述 Token Launch Gate 的语境（G0-G11）是允许的
            if "gate" in line_lower or any(f"g{i}" in line_lower for i in range(12)):
                return False
            return True
    return False


def check_buy_trade_cta(rel: str, content: str) -> list[str]:
    """检查公共路径前缀文件中的 Buy/Trade MOOD CTA。"""
    errors = []
    if not any(rel.startswith(prefix) or rel == prefix for prefix in PUBLIC_PATH_PREFIXES):
        return errors
    for i, line in enumerate(content.splitlines(), 1):
        if is_forbidden_cta(line):
            errors.append(f"{rel}:{i}: forbidden Buy/Trade MOOD CTA in public file: {line.strip()!r}")
    return errors


def load(root: Path, files_to_load: list[str]) -> dict[str, str]:
    files: dict[str, str] = {}
    for rel in files_to_load:
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

    # ---- MOOD FOUNDATION 011 ----

    # 6. MOOD CURRENT_CANON 必须声明 WORLD + PROTOCOL + PORTAL
    mood_cc = files.get("docs/mood/CURRENT_CANON.md", "")
    if mood_cc:
        if "WORLD" not in mood_cc or "PROTOCOL" not in mood_cc or "PORTAL" not in mood_cc:
            errors.append("docs/mood/CURRENT_CANON.md: missing WORLD + PROTOCOL + PORTAL declaration")
        if "Token is not the product" not in mood_cc:
            errors.append("docs/mood/CURRENT_CANON.md: missing 'Token is not the product' invariant")
        if "011" not in mood_cc or "G11" not in mood_cc:
            errors.append("docs/mood/CURRENT_CANON.md: missing 011 / G11 references")

    # 7. TOKEN_LAUNCH_GATE 必须存在并定义 G0–G11
    tlg = files.get("docs/mood/TOKEN_LAUNCH_GATE.md", "")
    if tlg:
        for gate in (f"G{i}" for i in range(12)):
            if gate not in tlg:
                errors.append(f"docs/mood/TOKEN_LAUNCH_GATE.md: missing gate {gate}")

    # 8. MOOD 反 Token 反模式检测（高权威文件）
    for rel, content in files.items():
        if rel not in AUTHORITY_FILES:
            continue
        for pat in FORBIDDEN_MOOD_AS_TOKEN_PATTERNS:
            if pat in content:
                errors.append(f"{rel}: forbidden MOOD-as-token pattern: {pat!r}")

    # 9. 公共文件不应出现 Buy / Trade MOOD CTA（描述禁令的除外）
    for rel, content in files.items():
        errors.extend(check_buy_trade_cta(rel, content))

    return errors


def check(root: Path) -> list[str]:
    errors: list[str] = []
    files = load(root, AUTHORITY_FILES)

    # 1. 必需的 canon 文件存在
    for rel in REQUIRED_CANON_FILES:
        if not (root / rel).exists():
            errors.append(f"missing canon file: {rel}")

    # 1b. 必需的 MOOD 文件存在
    for rel in REQUIRED_MOOD_FILES:
        if not (root / rel).exists():
            errors.append(f"missing mood file: {rel}")

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
