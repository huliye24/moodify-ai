# Media Controls & System Metadata Contract

## Commands

```text
PLAY / PAUSE / PLAY_PAUSE
→ W04 Playback

PREVIOUS / NEXT
→ W05 Queue
→ W04 Playback

SEEK (only if safely supported)
→ W04 Playback.seek
```

## System Playback State

```text
IDLE    → disabled/none
PLAYING → Playing
PAUSED  → Paused
ERROR   → safe stopped/paused projection
```

Windows 展示状态必须跟随真实 Playback。

## Metadata

允许：

```text
title
artist
album
duration
artwork only if already reliable
```

使用 W06 fallback。

禁止：
- full local path
- Ear/Evidence/stem state
- internal processing IDs

## Update

Track 改变时更新 metadata；Queue 改变时更新 previous/next availability；退出时清除 system media session。

## Background

媒体键可以工作，但不得因此把窗口强行置前。
