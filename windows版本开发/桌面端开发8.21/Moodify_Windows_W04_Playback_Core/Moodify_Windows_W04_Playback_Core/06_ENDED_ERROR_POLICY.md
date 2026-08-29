# Ended & Error Policy

## Ended Policy

### Context has next Track

```text
T1 ended
→ resolve T2
→ load T2
→ autoplay
```

### No next Track

```text
status = ENDED
current Track remains visible
position = duration
```

### Replay

用户再次按 Play：

推荐：

```text
seek(0)
→ play
```

或服从现有 engine 行为。

---

## Error Policy

### SOURCE_UNAVAILABLE

- no crash
- current Track remains
- UI minimal message
- next action may remain available

### LOAD_FAILED

- status ERROR
- retain error evidence

### DECODE_FAILED

- status ERROR
- do not poison future Tracks

### PLAY_REJECTED

- state must not say PLAYING if engine rejected

### ENGINE_ERROR

- recoverable for next Track

---

## Safe Skip

W04 若实现 error skip：

必须有：

```text
visited set / max skip count
```

避免：

```text
bad1 → bad2 → bad1 → ...
```

如果没有成熟 context，可不自动跳过。

W05 Queue 完成后再做更完整策略。

---

## Stale Events

任何：

```text
ended
error
timeupdate
loadedmetadata
```

如果属于旧 generation：

```text
IGNORE
```
