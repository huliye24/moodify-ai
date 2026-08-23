# MFD-004 Playback Evidence Template

Codex 最终应生成实际证据文件。

---

## Environment

```text
Windows:
Electron:
Node:
App version:
Desktop commit:
Backend version:
Output device:
```

---

## Track A

```text
track_id:
playback_id:
asset_version:
mime:
container:
codec:
duration:
sample_rate:
channels:
content_length:
range_support:
```

### Result

```text
load:
play:
audible:
pause:
resume:
seek_25:
seek_50:
seek_near_end:
ended:
```

---

## Track B

同上。

---

## Expiry

```text
expired manifest detected:
refresh requested:
new playback_id or URL:
play after refresh:
```

---

## Network interruption

```text
disconnect behavior:
state:
crash:
reconnect:
manual retry:
result:
```

---

## Human audible verification

```text
Audible:
Unexpected distortion:
Unexpected speed change:
Channel anomaly:
Obvious truncation:
Notes:
```

---

## Known limitations

只写真实限制。

不要把未来计划写成已实现。
