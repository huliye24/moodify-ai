# 08 — Schema Migration Report

**W01-P03 · 2026-08-17 · 状态：`SCHEMA_WRITE_BLOCKED`**

## 结论

- migration 文件已生成：`moodify-core-package/migrations/0001_data_plane_tables.sql`
- **未执行任何 DDL/DML**（PolarDB 凭据 BLOCKED E17 + 人类授权未确认）。
- 与 moodify_dev 既有 19 表的关系：**未对照**（需要只读凭据）；本文件设计为 CREATE IF NOT EXISTS，避免破坏既有表。

## 表设计核对（§2.6）

| 表 | 字段承载 | INV 对应 |
|---|---|---|
| tracks | track_id/source_hash/source_object_id/status_class 等 | INV-05/12 |
| jobs | 状态字段承载（current_state 等）——**P04 定义状态机** | 不造第二套 |
| objects | object_key UNIQUE/content_hash/immutable/retention | INV-01/02/03/06/11 |
| evidence | claim NOT NULL | INV-07 |
| versions | UNIQUE(kind,value) | INV-06 支持 |

## Gate 核对（§5 八项）

1. P02 明确 metadata DB ✓
2. 目标 dev/staging 或授权 production ✗（未确认）
3. migration 文件已生成 ✓
4. migration review ✗（待人类）
5. backup/rollback 明确 ✗（回滚路径已设计：DROP 5 表，未执行）
6. no destructive default ✓（IF NOT EXISTS）
7. dry-run/transaction ✗（未执行）
8. existing tables 对照 ✗（凭据阻塞）
9. 不创建第二套 authority ✓

**→ SCHEMA_WRITE_BLOCKED 保持，直到：人类授权 + 只读凭据 + review。**

## 变更清单（本包代码）

- `src/moodify/data_plane/`（新包 6 模块）
- `tests/test_data_plane.py`（9 测试）
- `migrations/0001_data_plane_tables.sql`
