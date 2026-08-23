# 12 — Migration & Deployment Plan

**W01-P04 · 2026-08-17 · 状态：`CONTROL_PLANE_DEPLOY_BLOCKED`（生产未授权）**

## Schema 变更（本包代码内）

- JobControlPlane 在现有 data_plane DB 上追加 4 表（CREATE TABLE IF NOT EXISTS）：
  `job_events` / `attempts` / `leases` / `idempotency_keys`
- 与 P03 migration（0001_data_plane_tables.sql）兼容：SQLite 侧由 control.py 自动建表；PolarDB 侧 migration 文件需补充（见下）。
- 非破坏性：不改动既有 tracks/jobs/objects/evidence/versions 表。

## 与现有系统迁移路径

| 现状 | 迁移 | 触发 |
|---|---|---|
| node/（4 态，SQLite 队列） | 映射到 8 态；新 worker 改用 JobControlPlane | P05 worker 重写时（人类授权） |
| reconstruction_job/（11 态，未提交） | stage 投影到 RUNNING 描述；状态映射（02 报告表） | 并行会话合并后评估 |
| data_factory（无状态机） | 不迁移（LEGACY，同步 runner） | 无需 |

## 部署计划（未执行）

1. dev/test 通过（本包 12 测试）。
2. 本地集成模拟：SQLite 全流程（已做）。
3. 生产部署：需要人类授权 + PolarDB write gate 解除 → CONTROL_PLANE_DEPLOY_BLOCKED。

## Rollback

- 新增表可 DROP（job_events/attempts/leases/idempotency_keys），不影响既有数据平面表。
- 状态机无破坏性迁移 → 回滚 = 停止使用 JobControlPlane，回归 node/ 现状。

## Gate 核对（§17）

- [ ] P03 metadata DB write 已授权 —— 否（BLOCKED）
- [x] 当前 control authority 已发现（01 报告）
- [x] migration 不创建第二套 authority
- [x] transition matrix 已 review（02 CSV，脚本校验通过）
- [x] rollback plan 已明确
- [x] dev/test 先通过（12 测试）
- [ ] production deploy 授权 —— 否（BLOCKED）
