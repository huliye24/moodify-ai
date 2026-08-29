# 09 — Playback Failure Taxonomy

**W01-P06 · 2026-08-17 · 实现：`delivery.py::PLAYBACK_FAILURES` + Android `DeliveryFailure`**

> 这是 **Delivery/Playback** 失败分类，**不替换、不污染** P04 compute failure taxonomy（DLV-INV-09/10）。
> 服务端 `DeliveryError.code` 与 Android `DeliveryFailure.code` 一一对应。

| Code | Meaning | Retry | Server/Client | Notes |
|---|---|---:|---|---|
| TRACK_NOT_READY | Track 未到生产 READY | false/manual | server | TST-01 |
| TRACK_NOT_FOUND | 未知 Track | false | server | TST-01 路径覆盖 |
| ACCESS_DENIED | 访问域无权播放 | false | server | TST-07 |
| DELIVERY_URI_EXPIRED | 临时凭证过期 | true | client/server | refresh；TST-04 |
| DELIVERY_URI_INVALID | 交付入口非法/签名不符 | policy | client/server | `_verify_uri` |
| NETWORK_UNAVAILABLE | 无网络 | true | client | 客户端 |
| NETWORK_TIMEOUT | 超时 | true | client | 客户端 |
| RANGE_NOT_SUPPORTED | seek 交付问题 | policy | client/server | DLV-INV-07 |
| OBJECT_NOT_FOUND | final object 缺失 | false/reconcile | server | TST-03；触发 reconciliation |
| UNSUPPORTED_MEDIA | 播放器无法解码 | false | client | 格式 |
| DECODER_ERROR | 解码运行时错误 | policy | client | ExoPlayer |
| AUDIO_FOCUS_LOST | 被中断 | true/resume | client | **契约占位，Android 未实现音频焦点**（01 报告 §1） |
| PLAYER_INTERNAL_ERROR | 播放引擎错误 | policy | client | ExoPlayer |
| UNKNOWN_PLAYBACK_ERROR | 未分类 | policy | client | 兜底 |

## 对应实现

- 服务端：`PLAYBACK_FAILURES`（14 codes）+ `DeliveryError`（非法 code 直接 `ValueError` 防呆）。
- Android：`DeliveryFailure` enum（14 codes，`PlaybackDeliveryClient.kt:46-61`），`playbackError(code)` 兜底 `UNKNOWN_PLAYBACK_ERROR`。

## Rule

1. 这些 code 属交付/播放域；**任何播放失败不得改 P04 Job 状态**（TST-09 验证）。
2. `OBJECT_NOT_FOUND` 是 DB 与对象存储不一致信号 → 触发 reconciliation 证据，**不是**把 Job 改 FAILED。
3. `AUDIO_FOCUS_LOST` 等客户端-only code 在服务端不出现；两端共享同一词汇表便于关联排障。
