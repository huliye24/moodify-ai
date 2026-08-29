# 10 — Playback Evidence Contract

**W01-P06 · 2026-08-17**

> 播放证据 = 交付验证 / 故障定位 / Golden Song·Pilot 验收 用，**与 P03/P05 生产 Evidence 分离**（DLV-INV-10：只读关联，不反向篡改生产证据）。

## Events

- PLAY_REQUESTED
- PLAY_STARTED
- PLAY_PAUSED
- PLAY_RESUMED
- PLAY_ENDED
- PLAY_FAILED

## Safe Fields

- `event_id`
- `playback_session_id`（关联 `PlaybackSession`）
- `track_id`
- `render_object_id` / version（DLV-INV-11 可追溯）
- `timestamp`
- safe playback `position_ms` / `duration_ms`
- `app_version`
- `failure_code`（09 taxonomy）
- `correlation_id`

## Do Not Collect By Default（隐私红线，任务书 §17）

- ❌ 音频监听/录音
- ❌ 不必要硬件标识（IMEI 等）
- ❌ 与播放无关传感器数据
- ❌ 完整 signed URL（query 含签名）
- ❌ 云凭证
- `device_class` 仅粗粒度（避免过度采集）

## Schema

包内已给 `schemas/playback_event.schema.json`（W01-P06 包）。事件落点：轻量、可关联、可被 P07/P08 验收消费；**第一阶段不建完整推荐/行为分析平台**（任务书 §16）。

## 现状（事实）

- `PlaybackSession` 在 `DeliveryService` 内实现（内存态 `self._sessions`），用于交付排障/证据关联。
- **持久化 playback event 存储未建**（第一阶段不建分析平台）；P07 Golden Song 时按需落最小事件。
- 隐私：Android 现状**无任何 playback 埋点上报**（01 报告无相关代码）→ 默认满足「不收集」。
