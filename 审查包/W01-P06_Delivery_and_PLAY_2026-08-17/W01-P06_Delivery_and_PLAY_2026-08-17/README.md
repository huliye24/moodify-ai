# W01-P06 — Delivery + PLAY

这是 Moodify Cognitive Wave 01 的第七个任务包。

## 两个原子任务

1. Playback Delivery Contract
2. Android PLAY Integration

## 主链

```text
READY
→ Playback Metadata
→ Authorized Delivery
→ Android
→ PLAY
```

P06 不处理声音本身。

它只负责把 P05/P04 已确认 READY 的 render 安全送到用户。

## 三条核心边界

- READY 才能播放
- Android 不持有长期 OSS / DB Secret
- 播放失败不能把生产 Job 改回 FAILED

P06 完成后，才进入 P07 Golden Song 001。
