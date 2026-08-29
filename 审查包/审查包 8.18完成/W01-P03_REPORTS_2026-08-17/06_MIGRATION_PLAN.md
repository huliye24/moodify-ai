# 06 — Migration Plan

**W01-P03 · 2026-08-17 · 状态：`SCHEMA_WRITE_BLOCKED`（未执行任何写入）**

## Schema Migration（PolarDB moodify_dev）

- 文件：`moodify-core-package/migrations/0001_data_plane_tables.sql`
- 性质：**非破坏性**（全部 CREATE TABLE IF NOT EXISTS；不改动既有 19 表）
- 目标：tracks / jobs / objects / evidence / versions 5 张数据平面表
- 前置门（§5 Schema Migration Gate）逐项：
  - [x] P02 已明确 metadata DB（ADR-003 → moodify_dev）
  - [ ] 目标环境 dev/staging 或人类授权 production —— **未确认**
  - [x] migration 文件已生成（0001）
  - [ ] migration review —— **未做（需人类/后续）**
  - [ ] backup / rollback 路径明确 —— **未做**
  - [x] no destructive default（IF NOT EXISTS）
  - [ ] dry-run / transaction —— **未执行**
  - [x] existing tables 已对照（05 mapping）
  - [x] 不创建第二套 authority
  - **结论：SCHEMA_WRITE_BLOCKED（凭据 + 授权双阻塞）**

## 数据迁移阶段（不执行）

| 阶段 | 内容 | 触发条件 |
|---|---|---|
| M0 | 只读对照 moodify_dev 既有 19 表（tracks/track_versions 等）与数据平面模型 | 获得只读凭据（P00 E17 解除） |
| M1 | 注册真实曲目（pre-music ~7 首）hash + tracks 行 | OSS 开通（OSS gate） |
| M2 | golden_run_out 注册为 evidence 对象 | M1 后 |
| M3 | 杭州 /var/lib/moodify 历史产物处置（LEGACY/清理） | 人工决策 |
| M4 | LA music-media/releases 迁移评估 | 人工决策（P06 播放面） |

## 禁止（§4）

- 本包不批量删除旧产物（05 mapping 只分类不删除）。
- 不执行任何 DDL/DML（Gate 未过）。

## 回滚

- 0001 为纯新增表：回滚 = DROP TABLE 数据平面 5 表（不影响既有表）；本包不执行。
