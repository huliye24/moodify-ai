# Playback Persistence Seam for W08

W04 不负责完整 restart recovery。

但必须为 W08 留出清晰接口。

## Candidate Persistable State

```text
current_track_id
position_ms
volume
context_type
context_id
context_cursor
```

是否持久化：

```text
was_playing
```

留给 W08 产品决策。

通常重启后不应自动突然出声。

## Persist Frequency

禁止每个 timeupdate 都强写磁盘。

推荐未来：

- throttle / debounce
- pause
- track switch
- app close
- periodic checkpoint

## Not Persistable

不要持久化：

- raw audio element
- native player pointer
- Promise
- callback
- source file handle
- generation token as durable identity

## W04 Requirement

只需提供：

```text
getPlaybackSnapshot()
restorePlaybackSnapshot(...) seam
```

或现有架构等价边界。

W08 再正式实现 restore policy。
