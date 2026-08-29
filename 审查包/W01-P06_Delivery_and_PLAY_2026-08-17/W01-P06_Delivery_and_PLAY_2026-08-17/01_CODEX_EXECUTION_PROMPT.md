# Codex Execution Prompt — W01-P06

执行：

**Moodify Cognitive Wave 01 / W01-P06 — Delivery + PLAY**

## 第一步

先生成：

`CURRENT_ANDROID_PLAYBACK_REALITY.md`

必须理解当前播放器、数据层、远程 source、Media3/ExoPlayer、播放 service 与现有测试。

不要先重写。

## 两个任务

### T06-1 Playback Delivery
- READY guard
- playback metadata
- auth
- signed URL or proxy ADR
- range/seek
- expiry refresh
- delivery evidence

### T06-2 Android PLAY
- load READY track
- PLAY/PAUSE
- buffering
- retry/reconnect
- URL refresh
- seek
- next/previous/swipe if already in scope
- playback failure mapping

## 禁止

- audio processing
- state machine changes
- render changes
- DB/Object identity changes
- UI expansion unrelated to PLAY
- skin/community
- iOS
- offline library

## 安全

- no OSS AccessKey in APK
- no DB credential in APK
- no processing API key in APK
- no full signed URL in long-lived logs

完成一个 READY test track 的 Android E2E 后停止，不进入 P07。
