# Moodify Desktop — Windows Product Contract v0.1

## Identity

```text
Product: Moodify
Client: Moodify Desktop
Platform: Windows
Executable: Moodify.exe
```

Exact package identifier must come from repository authority.

---

## Process Model

```text
One installed app
→ one main instance
→ one PlaybackEngine authority
→ one tray instance
```

---

## Window Policy

One explicit policy only:

### Option A

```text
Minimize → background
X → quit
```

### Option B

```text
Minimize → background
X → tray/background
Tray Quit → quit
```

Codex should follow existing product decision or choose the least surprising Alpha behavior and document it.

---

## Tray

Allowed:

```text
Show Moodify
Play / Pause
Quit
```

Optional:

```text
Next
Previous
```

No complex menu.

---

## Media Surface

Expose only product-safe metadata:

```text
title
artist
playback state
```

Do not expose:

```text
signed URL
playback id
asset version
internal preset
Ear metadata
```

---

## Release Tier

```text
Internal Alpha
Public Alpha
Stable (future)
```
