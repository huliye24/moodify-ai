# History / Recently Played Contract

## Model

推荐语义：

```text
HistoryEntry
- id
- track_id
- played_at
- kind
```

## Meaningful Play

必须选择并记录一个稳定策略：

### A. Playback Started
engine 确认 PLAYING 时记录。

### B. Threshold
播放超过最小时间后记录。

### C. Hybrid
PLAYING 时创建 pending，达到阈值后 commit。

推荐 B/C 以减少误触污染，但服从当前架构。

## Recently Played

推荐：

```text
History
→ played_at desc
→ unique by track_id
```

完整 History 可以保留重复事件。

## Error

resolve/load/play 失败不应记 meaningful play。

## Queue Advance

自动下一首成功播放后按同样策略记录。

## Persistence

History 必须 restart 后保留。

## Growth

必须记录 retention 决策：
- Alpha unlimited
- capped count
- time-based retention
