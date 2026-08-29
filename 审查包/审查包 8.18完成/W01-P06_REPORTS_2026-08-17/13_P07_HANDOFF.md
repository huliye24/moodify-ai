# 13 — W01-P07 Handoff — Golden Song 001

**From:** W01-P06（Delivery + PLAY） → **To:** W01-P07（Golden Song 001）

P06 冻结了交付契约。P07 **不得重新设计**以下（除非证明有阻塞性缺陷）：

- playback authorization（05）
- delivery URL identity（03/04/06）
- Android player 架构（01/08）
- compute pipeline（P05）
- Job state machine（P04）
- object identity（P03）

## P07 Input（P06 交付物）

- 一套 READY-only 交付契约：`DeliveryService`（`data_plane/delivery.py`）+ 10 服务端测试
- Android 交付客户端契约：`PlaybackDeliveryClient` + `PlaybackMetadata` + `DeliveryFailure` + 6 JVM 测试
- Playback metadata / authorization / failure / evidence 契约（04/05/09/10）
- 签名 URL vs 代理 ADR（06）：原则 = 服务端签发短 TTL 授权入口
- 安全基线（11）：移动端零长期云凭证

## P06 遗留 / 阻塞（P07 必须直面）

| # | 项 | 状态 | P07 动作 |
|---|---|---|---|
| 1 | 真实 BFF `GET /tracks/{id}/playback` 端点 | **BLOCKED（未部署）** | 部署或人类裁决替代路径 |
| 2 | OSS 对象存储 | **NOT_PROVISIONED** | 人类开通，或走 A2（music-media 签名） |
| 3 | Android 生产接线（注入 delivery fetcher） | 未接线（依赖 #1） | 端点就绪后最小接线（08 报告给出 ≤10 行方案） |
| 4 | `duration_ms/sample_rate/channels` 持久化 | 当前 0 | P07 从 VALIDATE metrics 落库 |
| 5 | 播放格式（WAV vs 压缩流式） | HUMAN_DECISION_REQUIRED | 人类裁决 |
| 6 | 真实 READY 曲目 | 无 | P07 选一首授权曲目跑通 |
| 7 | 版本口径 2.0.1 vs 3.1 | HUMAN_DECISION_REQUIRED | 人类对齐 |

## P07 Question

> 一首真实、熟悉、授权的歌，能否完整穿过整个 Moodify 系统，产出技术正确、可听评审、全程可追溯的播放体验？

## P07 rule

**只修 Golden Song 001 的阻塞项。不做功能扩张。**

P07 不再开发系统功能；它使用 P00–P06 已建成的现实系统跑：

```text
Source → Upload → Data Plane → Job → Compute → Verify → READY → Delivery → Android → PLAY
```

> ⚠️ P07 的真实执行强依赖 #1/#2/#6（基础设施 + 真实曲目 + 人类授权），这些超出 Codex 单方面能力，预期大量 `HUMAN_REQUIRED` / `BLOCKED`。
