# MFD-005 Interaction Map

## Mouse

### Play
Click primary button.

### Previous / Next
Click minimal controls.

### Seek
Drag / click progress.

### Volume
Drag volume.

### Wheel
If enabled:

```text
wheel up   → previous
wheel down → next
```

必须有 threshold/debounce。

---

## Keyboard

```text
Space → play/pause
Up    → previous
Down  → next
Left  → optional seek backward
Right → optional seek forward
```

不要抢占系统级快捷键。

---

## Track switching

```text
next
→ request/select next source
→ LOADING
→ READY
→ optional auto-play based on existing playback intent
```

行为必须与 PlaybackEngine 保持一致。

---

## Error retry

```text
ERROR
→ Retry
→ refresh manifest if needed
→ load
→ READY / PLAYING
```

不要创建无限 retry loop。
