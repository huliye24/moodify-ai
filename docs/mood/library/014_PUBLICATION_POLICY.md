# MOOD LIBRARY 014 — Publication Policy

**Version:** 1.0（MOOD LIBRARY 014, 2026-08-30）
**Authority:** root `AGENTS.md` → `docs/mood/CURRENT_CANON.md` → 本文件
**Related:** [014_DOCUMENT_INVENTORY.md](014_DOCUMENT_INVENTORY.md) · [014_METADATA_SCHEMA.md](014_METADATA_SCHEMA.md) · [014_HASH_POLICY.md](014_HASH_POLICY.md)

---

## 1. 公共文档必须回答

每个被注册为 `active` 或 `draft` 的 LibraryDocument 在 `/library/[slug]` 必须展示：

1. 这是什么文档？
2. 当前版本是什么？
3. 当前状态是什么？
4. 谁 / 什么流程决定它成为权威？
5. 源文件在哪里？
6. PDF 在哪里？（若真实存在）
7. Hash 是什么？（若真实计算）
8. 是否有后继版本？（superseded 链接）

## 2. 视觉状态徽章

| Status | 视觉 |
|---|---|
| `active` | 绿色徽章 `ACTIVE`，大字 |
| `draft` | 灰色徽章 `DRAFT`，必须附 `Parameters UNFROZEN` 提示（Economics 类强制） |
| `superseded` | 棕色徽章 `SUPERSEDED`，显示 `superseded by vX.Y` 链接 |
| `archived` | 灰色徽章 `ARCHIVED`，仅供历史阅读 |

## 3. Draft Economics 强制文案

任何 `category = economics` 且 `status = draft` 的文档，文档顶部必须显示：

```text
> Parameters are not frozen and do not represent an active token configuration.
```

并且在 `/library` 列表显示时不能放在 Foundation / Protocol 默认视图，必须显式在「Draft / Archived」视图。

## 4. Historical Security 强制文案

任何 `category = security` 且来自 `codex/moodify-classic-reconstruction-001` 或类似历史实现的文档，必须显式 `summary` 包含：

```text
HISTORICAL / SUPERSEDED / LEGACY SCOPE — Not an audit of any future MOOD Token contract.
```

并且 UI 不放在 Security 默认视图顶部，必须放在 `Archive`。

## 5. Token 安全

UI 任何路径不得出现：

- `Buy MOOD` / `Trade MOOD` / `Claim MOOD`
- `Official Contract: <未来 CA>`
- `Mainnet Active` / `Live Token`
- 任何与 `MOOD Token` 相关的最终承诺

Library UI 与 Moodify Player UI / Public Brand UI 同等遵守 `docs/mood/CURRENT_CANON.md` 与 `docs/brand/public/PUBLIC_BRAND_CONSTITUTION.md`。

## 6. Error states

- 未知 slug → `404`，**不** fallback 到随机文档
- 缺失 PDF → 隐藏 PDF CTA；显示「PDF not available yet」
- 缺失 hash → 显示「Hash unavailable」，**不**生成假占位
- 缺失 IPFS CID → 不显示 IPFS 行
- 缺失 sourceSha → UI 显示「Source commit SHA pending」

## 7. 与 Public Form 的边界

- 公共品牌语言由 `docs/brand/public/PUBLIC_BRAND_CONSTITUTION.md` 最高主题权威规定。
- Library UI 文案遵守该宪法。
- Library **不**创建第二套品牌语言权威。

## 8. 与未来 packages 的边界

- Library 不外露 FREEZE 集合资产（Token UI / 历史 Genesis v1.0 部署脚本）。
- Library 不外露 KEEP BUT DARK 集合资产在 G0–G11 PASS 前（reward / treasury panels）。
- Library 不替代 015 Passport、020 MIP、021 Treasury 等的专门 UX；Library 只是文档馆。