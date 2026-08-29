# Cloud Reliability / Capacity / DR — 执行清单

**Document ID:** MFY-RELIABILITY-CAPACITY-DR-001
**Version:** 1.0
**Date:** 2026-08-14
**Package:** MFY_CLOUD_RELIABILITY_CAPACITY_DR_001 (61)
**Status:** 清单生效；真机 soak/故障注入/恢复演练待部署授权

## 1. 目标与边界

- 目标：证明产品在明确容量边界内稳定维持一个季度；
- 不追求无限规模；定义 Phase I 容量边界、SLO、降级与恢复；
- 本地可执行部分：soak 探针短跑（本机对线上读路径）、备份/恢复演练（53 已做）；
- 真机部分：72h soak、故障注入、PolarDB 恢复、回滚演练。

## 2. 容量边界（Phase I 季度）

| 维度 | 边界 | 依据 |
|---|---|---|
| Ear 并发 worker | 1（2C2G，KEEP_2C2G 裁决） | 28 包 |
| 队列深度 | ≤500 jobs（API 上限） | 47 包 |
| 媒体单文件 | ≤100MiB；上传并发 burst 2 | nginx moodify-api-limits |
| 登录限速 | 5 次/10 分钟/IP | 51 包 |
| 磁盘余量 | ≥3GB（worker 守卫） | node/config |
| 备份 RPO/RTO | 24h / ≤4h | 58 包 |

## 3. SLO（季度）

| 指标 | 目标 |
|---|---|
| 官网/Ear/Music 可用性 | ≥99.5%（月） |
| Range 播放成功 | ≥99%（月） |
| Ear 案例成功率 | 保留 fail-closed 语义；不承诺人为通过率 |
| 备份执行率 | 100%（每日） |

## 4. 执行矩阵（真机，待授权）

| 项 | 动作 | 证据 |
|---|---|---|
| soak | soak_probe.sh 72h（web/ear/music/range 时间序列） | soak-*.log |
| 容量 | 队列 500 上限触发 + 上传 burst 429 | 日志 |
| 告警 | A1–A10 触发演练（53 表） | 告警日志 |
| 故障注入 | worker kill → 幂等恢复；BFF 断连 → 502 降级 | 48/51 行为 |
| 备份恢复 | PolarDB dump → 隔离恢复 → 对账零漂移 | 58 流程 |
| 回滚 | 静态/API/worker 三路演练 | 53 脚本 |

## 5. 本地已具备证据（55 包基线）

- soak 探针脚本语法 OK（本包）；
- 53 包本地备份/恢复演练：ID/hash 零漂移，backup.sha256 3/3 OK；
- 告警表 A1–A10 + R1–R3 runbook 已定义；
- worker 幂等恢复（48）、BFF 失败降级（51）测试绿。

## 6. 事实边界

- 真机 soak/注入/恢复需部署授权与观察窗口（65 包 T+0 后 7 天观察复用本矩阵）；
- 容量边界为定义值，真机触发验证后记录实测。
