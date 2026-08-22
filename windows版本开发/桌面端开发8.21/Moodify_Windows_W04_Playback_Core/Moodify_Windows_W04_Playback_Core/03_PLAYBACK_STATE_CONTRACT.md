# Playback State Contract

本文件定义语义，不强制字段名。

## Recommended State

```text
PlaybackState {
  current_track_id
  status
  position_ms
  duration_ms
  volume
  context
  error
  generation
}
```

## Status

### IDLE

无 current Track。

### LOADING

已选择 Track，正在解析/加载 source。

### READY

Track 已加载，可播放，但当前未播放。

### PLAYING

engine 正在播放。

### PAUSED

用户或系统暂停。

### ENDED

当前 context 已无下一首，当前 Track 播放结束。

### ERROR

当前播放请求失败。

---

## State Invariants

### S-01

```text
PLAYING
→ current_track_id != null
```

### S-02

```text
position_ms >= 0
```

### S-03

若 duration known：

```text
0 <= position_ms <= duration_ms
```

### S-04

```text
0 <= volume <= 1
```

或现有引擎等价 normalized range。

### S-05

新 Track load 时：

```text
generation++
position = 0
error = null
```

### S-06

旧 generation 的 async event 不得修改当前 state。

### S-07

ERROR 不得静默删除 current Track identity。

### S-08

ENDED 应保留 current Track，以便用户重新播放。

### S-09

UI 不应维护另一套 independent status。

### S-10

正式 Queue state 不在 W04 建立。
