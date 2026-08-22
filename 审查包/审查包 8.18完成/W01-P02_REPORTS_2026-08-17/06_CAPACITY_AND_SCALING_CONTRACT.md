# 06 — Capacity & Scaling Contract

**规则（任务书 §5/R9）：** 不虚构 benchmark；P00 未测量 → `CAPACITY_UNKNOWN — MEASURE_IN_P07/P08`。

## 计算节点容量契约

| 指标 | NODE-001 LA | NODE-002 杭州 | 依据 |
|---|---|---|---|
| Max concurrent jobs | **1**（worker 队列串行；未实测更高） | **1**（LSM 并行=1） | raw_scan；pilot 记录 |
| Expected full-song duration range | **CAPACITY_UNKNOWN**（无云端全曲处理证据） | 历史 pilot 10 曲全成功（单曲时长未记录） | P00 TT-052 |
| RAM safe floor | 7.7GiB（audiolla 驻留 ~770MB + node 123MB + uvicorn 68MB；余 ~6.1G） | 1.6GiB（pilot 期 swap ~1GiB 驻留；safe floor = 保留 512MB 自由） | raw_scan；E18 |
| Disk scratch budget | 76G 可用；未专门分配 scratch | 23G 可用；/var/lib/moodify 6.5GB 历史 | raw_scan |
| Swap warning threshold | 无 swap（0B）——保持无 swap | swap 使用 >1.2GiB 告警（2GiB 总量） | raw_scan；E18 |
| CPU saturation warning | load >3（4 vCPU） | load >1.5（2 vCPU） | 惯例（未实测阈值） |
| Temp asset cleanup ownership | 人工（无自动清理） | 人工（无自动清理） | E18 §20 |
| External API rate assumptions | LALAL.AI 计费+限流（未测得额度）——**CAPACITY_UNKNOWN** | — | E18 §16 |
| 阻塞 3-song pilot 的条件 | 无 OSS（对象落地本地磁盘）；worker 并发=1；LA 单点 | 1.6GB 内存硬限 + swap 依赖；磁盘 6.5GB 历史占用 | 本包判断 |

## 并发边界决策

- **当前并发 = 1（双节点）。** 原因：杭州 1.6GB 是硬约束（pilot 实证）；LA worker 队列近空，无并发需求；audiolla 单容器。
- 扩容触发指标（仅记录，不实施）：
  - 队列持续积压 > 24h 且单 worker 无法消化；
  - 杭州 swap 驻留 > 1.2GiB 持续 1h；
  - 任何新增常驻服务（Redis/worker 副本）需先在 Decision Register 论证。

## 数据平面容量（目标，P03 设计）

- OSS：NOT_PROVISIONED；目标容量假设：单曲 source+render+evidence ≈ 100-300MB（以本地 pre-music 单曲 200MB-1.8GB 观察为准）——**具体预算 P03**。
- PolarDB moodify_dev：当前 ≈0 数据；目标：job/track 元数据行级（P03 schema）。

## 明确 UNKNOWN（不猜测）

1. 云端全曲处理时长（无生产测量）→ MEASURE_IN_P07/P08。
2. LALAL.AI 配额/限流 → 需计费控制台确认。
3. 双节点同时跑 2+ 曲目的实际表现 → 未实测。
4. LA 播放带宽上限（静态媒体 248MB/5 文件当前无压力）→ 未测。
