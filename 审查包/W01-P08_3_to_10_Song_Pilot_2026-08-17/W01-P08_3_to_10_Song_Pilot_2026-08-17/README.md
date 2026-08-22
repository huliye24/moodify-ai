# W01-P08 — 3 → 10 Song Pilot

Moodify Cognitive Wave 01 的第九个任务包。

## 两个原子任务

1. **3-Song Smoke Pilot**
2. **10-Song Pilot**

## 顺序不能跳

```text
Golden Song
↓
3 Songs
↓ Gate
10 Songs
```

如果 3-song Gate 失败，就不允许为了“完成任务”继续跑 10 首。

## P08 的任务不是扩功能

它要回答：

> 同一套 Moodify 面对不同歌曲时，还成立吗？

重点看：

- first-pass acceptance
- failure/recovery
- resource/cost
- BYPASS / intervention
- human listening
- playback
- traceability
- repeated friction

## 版本纪律

10-song pilot 期间如果发生影响生产语义的代码改变：

`VERSION_SPLIT`

不得把不同系统版本的数据混成同一 cohort。

## 这批数据最终交给 P09

P08 记录事实。

P09 才负责蒸馏。
