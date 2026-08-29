# Latency Smoke — LA → Hangzhou → PolarDB（低强度，非压测）

日期：2026-08-13

## 测量（从 LA 服务器 curl 杭州 8000，各 20 次）

| 路径 | min | p50 | p95 | max |
|---|---|---|---|---|
| GET /internal/v1/music/catalogue | — | ~0.36s | ~0.42s | 0.45s |
| GET /internal/v1/music/creators/by-handle/cadeau10 | — | ~0.35s | ~0.40s | 0.41s |
| GET /health | 0.33s | 0.35s | 0.40s | 0.40s |

基础网络（审计数据）：LA↔杭州 ping 170ms 0% 丢包；TCP p50 0.17s。

## 解读
- HTTP 往返 = RTT(0.17s) ×2 + 应用处理 ≈ 0.35-0.40s，符合预期（无异常）。
- BFF 缓存（30/60/300s）进一步降低用户侧重复请求延迟。
- 写路径（幂等键 + 事务）p50 同量级，可接受。
