# Reliability / Capacity / DR — 实测结果

**Package:** MFY_CLOUD_RELIABILITY_CAPACITY_DR_001 (61)
**Date:** 2026-08-14

## 1. Soak（线上读路径，12 分钟，10 采样点）

| 端点 | 采样 | 可用性 |
|---|---|---|
| 官网 healthz | 9/10 200 | 90%（1 次瞬时 000，前后采样均 200） |
| Ear /health | 9/10 200 | 90%（1 次瞬时 000） |
| Music bootstrap | 10/10 200 | 100% |
| 音频 Range | 10/10 206 | 100% |

瞬时抖动模式（与 56 探测 catalogue 000 同类）：单采样点 000，前后采样全 200——**网络瞬时抖动**，非服务故障。SLO 99.5% 需更长窗口（72h 真机 soak 归 65）。

## 2. 故障注入：worker 中断恢复（实测）

| 步骤 | 结果 |
|---|---|
| 30s 长音频上传（5.3MB）→ worker RUNNING | job_bbd4331b… |
| **RUNNING 中杀 worker（PID 精确）** | job 停在 RUNNING（attempts=1, finished=False）——**权威状态保留，无伪完成** |
| 重启 worker | 日志 `recovered_interrupted_jobs=1`（幂等恢复） |
| 恢复后轮询 | **SUCCEEDED** |

## 3. BFF 断连降级（实测）

上游指向不可达端口（127.0.0.1:59999）→ 请求返回 **502 UPSTREAM_UNAVAILABLE + request_id**（fail-closed，可排查，不吞错误）。

## 4. 工具修复

soak_probe.sh 双输出 bug（失败时 `000000`）修复为单 `000`。

## 5. 事实边界

- 真机 72h soak、容量上限触发、PolarDB 恢复、三路回滚演练需部署授权（65 时间线复用本矩阵）；
- 本地实测覆盖：读路径稳定性、worker 中断恢复、BFF 降级——61 的本地可执行面全部完成。
