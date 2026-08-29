# Playback Restore Policy

## Restore

```text
current_track_id
position_ms
volume
```

## Status

默认：

```text
previous PLAYING
→ restore as PAUSED/READY
```

## Source Validation

Track identity 恢复后重新 resolve source。

如果 unavailable：

```text
Track remains current
Playback not started
status safe
Queue preserved
```

## Position

- negative → 0
- beyond duration → duration or 0 depending engine safety
- metadata unavailable → defer seek until ready

## Volume

必须 clamp 到合法范围。

## No Autoplay

这是 W08 硬 invariant。
