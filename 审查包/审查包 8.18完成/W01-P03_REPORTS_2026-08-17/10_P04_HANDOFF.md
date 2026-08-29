# 10 — P04 Handoff

**From:** W01-P03（Data Plane — OSS + PolarDB）→ **To:** W01-P04（Control Plane & Job State Authority）

## 已固定（P04 不再重新定义）

- Track / Job / Object / Evidence / Version ID 方案（UUIDv7 + 前缀：trk_/job_/obj_/ev_/ver_）
- Object key convention（01 报告 + `moodify.data_plane.object_key`）
- 元数据模型（02 报告 + `migrations/0001_data_plane_tables.sql`，未执行）
- Data Identity Contract（03 报告：Track→Source / Job→Track / Object→Track / Produced→Job / Evidence→Claim / Version→Production / Provenance Chain）
- Data Plane Invariants INV-01..14（04 报告，12 项有测试）
- Current→Target mapping（05）与 Migration Plan（06）
- OSS 配置意图与 retention（07）
- 代码：`moodify.data_plane` 包（ids/object_key/manifest/adapter/repository）+ 9 测试

## P04 必须回答的唯一问题

> 一条已经拥有稳定数据身份的 Job，如何在唯一 authoritative state machine 中被调度、租约、重试、恢复和观测？

## P04 输入

1. `moodify.data_plane.repository.DataPlaneRepository`（jobs 表字段承载：current_state/current_attempt/failure_code 等）
2. Data Identity Contract（provenance 链）
3. 02_NETWORK_MATRIX（NW-10/16 target）
4. 09_P03 报告 + 06_CAPACITY（P02）——队列现状 SQLite（ADR-005：P04 评估 DB-backed 迁移）
5. Secret Ownership（P02 S-01/S-02）

## P04 必答清单（P02/P03 遗留）

| # | 问题 | 前置约束 |
|---|---|---|
| 1 | 唯一 Job authority：SQLite 队列 vs PolarDB-backed（ADR-005 revisit trigger 已触发条件：任务量增长/多 worker） | 不创建第二套 authority |
| 2 | state machine 状态集与迁移（jobs.current_state 语义） | P03 只建字段，P04 定义语义 |
| 3 | 租约/重试/恢复（recover_interrupted_jobs 升级为权威语义） | 24x7 包已验证基础 |
| 4 | 幂等 worker 消费与 object 注册联动 | INV-11/Test E |
| 5 | 杭州 :8000 收紧为 LA 白名单（NW-16 target）实施 | 需人类授权网络修改 |

## 阻塞项（P04 前置）

- PolarDB 只读凭据（E17 BLOCKED）→ 决定 SQLite 保留期或 DB-backed 前必须先解除。
- Schema migration 未执行（08 报告）→ P04 若需 DB-backed 队列，需先过 Schema Write Gate。
