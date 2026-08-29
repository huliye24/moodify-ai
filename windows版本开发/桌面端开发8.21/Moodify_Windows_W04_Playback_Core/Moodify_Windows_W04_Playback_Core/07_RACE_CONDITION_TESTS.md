# Playback Race Condition Test Plan

播放器最容易出现的问题不是普通 Play，而是异步竞争。

## R-01 Rapid Track Switch

```text
load T1
before ready → load T2
before ready → load T3
```

期望：

```text
current = T3
T1/T2 late events ignored
```

## R-02 Late Ended

T1 切到 T2 后 T1 产生 ended。

期望：不得跳过 T2。

## R-03 Late Error

T1 失效后已切 T2，但 T1 error 迟到。

期望：T2 不进入 ERROR。

## R-04 Rapid Toggle

连续点击：

```text
play pause play pause play
```

最终 UI 与 engine 一致。

## R-05 Play Promise Reject

play() 异步 reject。

期望：

```text
not PLAYING
```

## R-06 Seek During Load

metadata 尚未 ready 时 seek。

必须安全排队、忽略或 clamp，策略明确。

## R-07 Rapid Next

连续 10 次 next。

期望最终落在确定 Track，不 crash，不出现多个并发 playback authority。

## R-08 Playlist Reorder During Playback

当前 Track 所在 Playlist 被 reorder。

当前 Track 继续播放。

下一首计算依据最新还是 snapshot 必须明确。

推荐 W04：

```text
use latest stable playlist order
```

除非已有设计相反。

## R-09 Remove Current PlaylistItem

当前 Track 从 Playlist 移除。

推荐：

```text
current audio continues
context recomputed safely
```

## R-10 Delete Source During Playback

不要求跨 OS 行为完全一致，但不得造成 app crash / unrecoverable state。
