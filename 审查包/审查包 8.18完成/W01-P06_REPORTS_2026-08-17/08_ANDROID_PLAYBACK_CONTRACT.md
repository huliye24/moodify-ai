# 08 — Android Playback Contract

**W01-P06 · 2026-08-17**

## Player

复用现有引擎：**Media3 ExoPlayer 1.10.1**（`PlaybackController`）。不自写解码器 / 不换框架 / 不同时重做 UI（任务书 §9）。

## Input

`PlaybackMetadata`（Kotlin data class，`PlaybackDeliveryClient.kt`）——来自服务端 04 报告的 client-safe payload。

## Player States（客户端 playback session state，非 P04 Job 态）

- IDLE / LOADING / BUFFERING / PLAYING / PAUSED / ENDED / ERROR

现状映射（`PlaybackController`）：`isLoading`(BUFFERING) / `isPlaying`(PLAYING) / `STATE_ENDED→next` / `onPlayerError→ERROR 文案`。
**合法并存**：`Job = READY` + `Playback = BUFFERING`（任务书 §12）。

## Commands

- play / pause / resume：`play(queue,index)` / `toggle()`
- seek：`seekTo()`
- next / previous：`next()/previous()`（自管理队列循环）
- swipe：**现状无垂直滑动切歌**；如产品面后续采用，接入 `move(delta)` 即可，本包不新增手势系统
- retry：UI 层重试（当前为手动）
- refresh delivery entry：`PlaybackDeliveryClient.refresh(trackId)`

## Expired URI Recovery（契约；客户端逻辑）

1. 检测交付鉴权/过期失败（`DELIVERY_URI_EXPIRED` / HTTP 403/410）
2. 请求新 `PlaybackMetadata`（`refresh`）
3. 保留 `track_id`
4. 安全时保留播放位置
5. 加载新 URI
6. resume

**要求**（任务书 §14）：不重建 Job / 不重传 source / 不重 Render / 不失 track identity。
- 服务端：TST-04/06/10 已验证（不重建、identity 稳定）。
- 客户端：`PlaybackDeliveryClient.refresh` + `isExpired` 已实现并有 JVM 测试（`tst04_urlExpiryRefresh`）；**与 `PlaybackController` 的接线未上生产**（见下）。

## Failure Isolation

**任何 Android 播放错误不得把 READY Job 改成 FAILED**（DLV-INV-09）。
- 服务端：delivery 错误不动 `jobs.current_state`（TST-09）。
- 客户端：播放错误只进 `DeliveryFailure`/`PlaybackUiState.error`，不回写服务端 Job。

## 接线现状（关键事实，不虚构）

| 项 | 状态 |
|---|---|
| `PlaybackDeliveryClient` 契约 + `PlaybackMetadata` + `DeliveryFailure` | **已实现**（Kotlin） |
| JVM 单测 `PlaybackDeliveryClientTest`（6 用例） | **已存在**（见 12 报告执行状态） |
| `PlaybackController.resolvePlaybackUri` delivery-first 逻辑 | **已实现**（含静态 CDN 兜底） |
| 生产注入 `delivery`（MainActivity 传 `PlaybackDeliveryClient(fetcher)`） | **未接线**——`PlaybackController(this)` 未传 delivery |
| 真实 BFF `GET /tracks/{id}/playback` 端点 | **未部署（BLOCKED）** |

**为何不立即接线**：接线后 `fetcher` 打向一个**尚不存在的 BFF 端点**，必然抛错并走静态 CDN 兜底——即「接线了也等同没接」。真正接通 = BFF 端点部署（BLOCKED）+ 注入 `fetcher`。本包不制造「假装接通」的假证据。

**建议的最小接线（部署后，≤10 行）**：在 `MainActivity.onCreate` 构造 `PlaybackDeliveryClient(fetcher = { id -> bff.getJson("/tracks/$id/playback") })` 并传入 `PlaybackController(this, delivery)`；`BffClient` 增加 `playback(id)` 方法。此为部署后动作，本包不落地。
