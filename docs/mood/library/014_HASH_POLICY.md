# MOOD LIBRARY 014 — Hash / Provenance Policy

**Version:** 1.0（MOOD LIBRARY 014, 2026-08-30）
**Authority:** root `AGENTS.md` → `docs/mood/CURRENT_CANON.md` → 本文件
**Related:** [014_PUBLICATION_POLICY.md](014_PUBLICATION_POLICY.md) · [014_METADATA_SCHEMA.md](014_METADATA_SCHEMA.md)

---

## 1. 目标

证明：

```text
Source file
   ↓
Commit SHA
   ↓
Published file / PDF
   ↓
SHA-256
```

用户应该能够独立验证：

> 我现在看到的 PDF 与 GitHub 里的版本对应。

## 2. Active / Draft 文档必须记录

| 字段 | 必填 |
|---|---|
| sourcePath | ✓ |
| sourceSha | ✓（来自 `git rev-parse HEAD:<sourcePath>` 在 registration 时） |
| sha256（仅当文件存在且未变更） | 推荐 |
| publishedAt / updatedAt | ✓ |

## 3. Unverified

如果无法证明当前 published 内容与 source 对应（典型情况：PDF 与 source 不是同一 commit 生成），则必须：

- 在 UI 显示 `PROVENANCE_UNVERIFIED`
- 在 metadata 的 `summary` 末尾追加 `(Provenance unverified — see source for canonical content)`
- **不**显示假 hash

## 4. Hash 计算策略

- 仅对真实存在的文件计算 SHA-256。
- 计算命令：

  ```bash
  sha256sum <file>
  ```

  或在浏览器 / Node：

  ```js
  await crypto.subtle.digest("SHA-256", content);
  ```

- 014 bridge 实现：在 `apps/web/lib/mood/library/hashing.ts` 提供 `sha256OfText(text: string): Promise<string>`。

## 5. Hash 重新生成

内容变更后必须重新计算 SHA-256。

**禁止**手动复制旧 hash 到新文件。

## 6. PDF / source 不一致

如果 PDF 由 source markdown 转换而来但转换时 source 已变：

- 重新生成 PDF
- 重新计算 PDF 的 SHA-256
- 同时更新 sourceSha 与 updatedAt

## 7. 014 bridge 实施

- 对 docs/mood/* 八个 + docs/brand/public/PUBLIC_BRAND_CONSTITUTION.md + docs/canon/CURRENT_CANON.md 真实计算 SHA-256（在 registration 时静态嵌入）。
- 对 skeleton / Draft / 缺失文件 **不**计算也不嵌入 SHA-256；UI 显示 `Hash unavailable`。
- 验证脚本：`scripts/library_hash_check.mjs`（014 新建）跨验证 sourcePath + sha256。

## 8. 与 022 Security 的边界

- 022 阶段会引入 Security & Trust Layer；014 不与 022 冲突。
- 014 仅负责文档 hash；022 负责 API / wallet / smart contract 安全。
- 022 完成前 014 不外露任何 hash 相关 UI 之外的元素。