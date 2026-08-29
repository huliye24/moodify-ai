# 00 — P02 Executive Summary

**Package:** W01-P02 — Cloud Topology & Node Responsibility Convergence
**执行时间:** 2026-08-17 21:05–21:35 CST
**性质:** 纯架构收敛（只设计，不部署）

## 核心结论

**One Song Infrastructure 的云端职责分配：**

```text
PLAY (Android/浏览器) ← Cloudflare 隧道 ← LA (CONTROL_API + 播放交付, 共置)
                                              ├── BFF/API → 杭州 (CPU_WORKER)
                                              ├── worker + SQLite 队列
                                              └── audiolla 容器 → LALAL.AI
杭州 worker → /var/lib/moodify (scratch) → PolarDB moodify_dev (METADATA_DB, 目标) 
                                          → OSS (OBJECT_STORAGE, PLANNED, P03)
```

- **控制面 = LA**（ADR-001）；**计算 = 杭州（数据工厂主责）+ LA（Ear worker 辅助）**（ADR-002）
- **元数据 = PolarDB moodify_dev**（目标，现状 schema-only）；**对象 = OSS**（PLANNED，P03）
- **队列 = SQLite 保持，不引 Redis**（ADR-005，R6 无必要性）
- **10 个节点全部有唯一主责 + 禁止职责**（01_NODE_ROLE_ASSIGNMENT，schema 校验通过）

## 关键边界（本包只设计）

1. 杭州 :8000 从公网收紧为仅 LA（NW-16 target）；DB 端口保持关闭。
2. 客户端不持长期云凭据（R7）；播放 URL 目标改为 BFF 签发。
3. LA→PolarDB 不建跨地域直连（NW-11 forbidden）。
4. 未引入任何重型基础设施（K8s/Redis/Kafka 等全部不引入）；唯一新增候选 = OSS（P03）。

## 明确的 UNKNOWN（不猜测）

- PolarDB 内容直接核验 BLOCKED（引用黑箱调查 MEDIUM）
- 云端全曲处理时长 / LALAL 配额 → CAPACITY_UNKNOWN, MEASURE_IN_P07/P08
- vinext 平台（moodify-music :3100）代码来源 UNKNOWN

## 验收门

- [x] P00 Reality Gate（P00 10 份产物齐备）
- [x] P01 Canon Gate（docs/canon/* + P01 报告齐备）
- [x] 12 份产物生成（01 双格式 + 02-10 + ACCEPTANCE）
- [x] 未执行任何部署/修改（全程只读 + 本地写报告）

**完成后停止，等待人类审核，不进入 P03。**
