# MOOD LIBRARY 014 — Metadata Schema

**Version:** 1.0（MOOD LIBRARY 014, 2026-08-30）
**Authority:** root `AGENTS.md` → `docs/mood/CURRENT_CANON.md` → 本文件
**Related:** [014_DOCUMENT_INVENTORY.md](014_DOCUMENT_INVENTORY.md) · [014_VERSION_POLICY.md](014_VERSION_POLICY.md) · [014_PUBLICATION_POLICY.md](014_PUBLICATION_POLICY.md) · [014_HASH_POLICY.md](014_HASH_POLICY.md)

---

## 1. 类型（TypeScript，对应 `apps/web/lib/mood/library/types.ts`）

```ts
export type LibraryDocumentStatus =
  | "draft"
  | "active"
  | "superseded"
  | "archived";

export type LibraryDocumentCategory =
  | "foundation"
  | "protocol"
  | "governance"
  | "economics"
  | "security"
  | "research";

export type LibraryDocumentLanguage = "zh" | "en" | "bilingual";

export type LibraryDocument = {
  // stable identifier (lowercase-kebab, no version suffix)
  slug: string;

  // display
  title: string;
  summary: string;
  category: LibraryDocumentCategory;
  language: LibraryDocumentLanguage;

  // versioning
  version: string;            // semver-like; "0.1", "1.0"
  status: LibraryDocumentStatus;

  // source provenance
  sourcePath: string;         // repo path (e.g. "docs/mood/CURRENT_CANON.md")
  sourceSha?: string;         // git commit SHA at registration time

  // publication surfaces (optional; absent => not provided)
  pdfUrl?: string;            // /library/pdf/<slug>.pdf or external
  onlineUrl?: string;         // canonical online reader URL
  githubUrl?: string;         // GitHub source link (real only)
  ipfsCid?: string;           // only if real CID exists; NEVER fake

  // hash (optional; absent => "Hash unavailable", not a placeholder)
  sha256?: string;            // computed sha256 of registered content

  // timestamps (ISO 8601)
  publishedAt?: string;
  updatedAt?: string;
};
```

## 2. 规则

- **slug 不因版本变化而改变**。`mood-canon` 在 v1.0 / v1.1 之间保持同一 slug；版本通过 `version` 字段表达。
- **同一 doc family 同时只能有一个 `status = active`**。其他版本进入 `superseded`。
- **version 必显式**。`active` 文档禁止空 version。
- **status 必显式**。`active` 与 `draft` 视觉上严格区分（详见 [014_PUBLICATION_POLICY.md](014_PUBLICATION_POLICY.md)）。
- **sourceSha** 必须来自真实 git commit SHA。014 不允许伪造。
- **pdfUrl / githubUrl / ipfsCid / sha256** 缺失时**禁止伪造**。UI 必须显示 `not available` / `PROVENANCE_UNVERIFIED`，绝不展示假占位。
- **publishedAt / updatedAt** 必须来自文件 mtime 或 commit date；不可手动随机生成。

## 3. PDF / IPFS 缺失约束

- 没有真实 PDF：UI 不显示下载按钮，显示「PDF pending」或完全隐藏 CTA。
- 没有真实 IPFS CID：UI 不显示 IPFS 行；CID 字段在 metadata 中保持 `undefined`。
- 没有真实 SHA-256：UI 显示「Hash unavailable」，**禁止**生成 `0000...` 或重复旧 hash。

## 4. Draft vs Active 的字段强制

| 字段 | draft | active | superseded | archived |
|---|---|---|---|---|
| version | 必填 | 必填 | 必填 | 必填 |
| sourcePath | 必填 | 必填 | 必填 | 必填 |
| sourceSha | 推荐 | 必填 | 必填 | 推荐 |
| pdfUrl | 可选 | 可选 | 可选 | 可选 |
| githubUrl | 必填 | 必填 | 必填 | 必填 |
| sha256 | 可选 | 必填 | 必填 | 可选 |
| ipfsCid | 不可填（无 CID） | 可选 | 可选 | 不可填 |

## 5. 与 011 Canon 的对齐

- Tokenomics / Economics 类文档必须 `status = draft` 直到 G10 PASS（见 `docs/mood/TOKEN_LAUNCH_GATE.md`）。
- 历史 Genesis v1.0 安全文档必须 `status = superseded | archived` 且显式 `summary` 中标记 `HISTORICAL / LEGACY SCOPE`。
- 公共品牌 / Public Form 类由 [docs/brand/public/PUBLIC_BRAND_CONSTITUTION.md](../brand/public/PUBLIC_BRAND_CONSTITUTION.md) 管辖，本 Library 注册时**不修改**该宪法。