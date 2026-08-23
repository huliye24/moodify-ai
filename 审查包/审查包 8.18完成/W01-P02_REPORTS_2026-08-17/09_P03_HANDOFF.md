# 09 — P03 Handoff

**From:** W01-P02（Cloud Topology & Node Responsibility）→ **To:** W01-P03（Data Plane — OSS + PolarDB）

## 已固定（P03 不再讨论）

- 节点职责（01_NODE_ROLE_ASSIGNMENT）：LA=CONTROL_API+PLAYBACK_DELIVERY（共置）；杭州=CPU_WORKER+CONTROL_API（共置）；PolarDB moodify_dev=METADATA_DB（目标）；OSS=OBJECT_STORAGE（PLANNED）；audiolla=EXTERNAL_AUDIO_SERVICE；Android=PLAYBACK_DELIVERY；SQLite=JOB_ORCHESTRATION（现状）。
- 网络边界（02_NETWORK_MATRIX）：杭州 :8000 目标仅 LA；DB 私网；LA→PolarDB 不经跨地域直连。
- Secret 所有权（03_SECRET_OWNERSHIP_MATRIX）：目标 Secret Manager；OSS 凭据不落服务器长期 env/Android。
- 部署边界（04_DEPLOYMENT_BOUNDARY）：时间戳 tar 发布为现状；目标带 commit 身份。
- 失败域（05_FAILURE_DOMAIN_MATRIX）与容量契约（06_CAPACITY_AND_SCALING_CONTRACT）。
- 架构决策（08_ARCHITECTURE_DECISION_REGISTER ADR-001..010）。

## P03 必须回答的唯一问题

> 在 P02 已固定的云端职责下，OSS 与 PolarDB 如何形成唯一、可追溯、可恢复的数据平面？

## P03 输入

1. P00 Reality（审查包/W01-P00_REPORTS_2026-08-17）
2. P01 Canon（docs/canon/*）
3. 02_NETWORK_MATRIX.md（NW-10/11/12/16 目标边界）
4. 04_DEPLOYMENT_BOUNDARY.md
5. 07_TARGET_ONE_SONG_TOPOLOGY.mmd
6. 08_ARCHITECTURE_DECISION_REGISTER.md

## P03 必答清单（来自 P02 决策）

| # | 问题 | P02 给定约束 |
|---|---|---|
| 1 | OSS bucket/prefix 设计 | source / render / evidence 对象；元数据进 PolarDB（R4）；客户端不持长期凭据（R7） |
| 2 | PolarDB schema 设计 | moodify_dev 现有 19 表为起点（tracks/track_versions/audit/idempotency/creation_passports）；job/track 元数据权威 |
| 3 | OSS 凭据方案 | RAM 角色/STS；不落服务器长期 env；不落 Android |
| 4 | VPC/网络 | 杭州→PolarDB 私网（VPC 对等）；杭州 :8000 收紧为 LA 白名单；PolarDB 公网端口保持关闭 |
| 5 | 数据可恢复 | 备份/生命周期/恢复演练（P00 技术债 #P0/#P3） |
| 6 | 直接核验 | P00 对 PolarDB 直接核验 BLOCKED（凭据）→ P03 需先解决只读凭据再设计 |
| 7 | 3-song pilot 前置 | OSS 未开通是 3-song pilot 阻塞条件之一（容量契约） |

## 提醒（事实边界）

- PolarDB 内容未经本会话直接核验（BLOCKED E17）；表/行数引用同日黑箱调查（MEDIUM E18）。
- OSS 为 NOT_PROVISIONED：P03 若设计开通流程，需先获得人类授权与阿里云凭据。
- 容量数字（全曲时长/LALAL 配额）为 UNKNOWN，P07/P08 实测。
