# Moodify Minimal Player — UI Contract v0.1

## 1. Default Screen

```text
┌──────────────────────────────┐
│           Moodify            │
│                              │
│                              │
│         ◯  Disc / Vinyl      │
│                              │
│          Song Name           │
│            Artist            │
│                              │
│             ▶                │
│                              │
│      ───────●────────        │
│                              │
│       ◀      🔊      ▶       │
└──────────────────────────────┘
```

这是结构示意，不是像素稿。

---

## 2. Required Components

```text
Brand
DiscVisual
TrackIdentity
PrimaryPlaybackControl
ProgressControl
PreviousControl
NextControl
VolumeControl
StatusMessage
```

---

## 3. Required States

```text
EMPTY
LOADING
READY
PLAYING
PAUSED
ENDED
ERROR
```

UI 不要创建新业务状态。

---

## 4. Primary Control

READY / PAUSED:

```text
Play
```

PLAYING:

```text
Pause
```

LOADING:

```text
disabled / loading
```

ERROR:

```text
Retry
```

---

## 5. Minimal text

首屏文字尽量只有：

```text
Moodify
Song
Artist
必要错误 / loading
```

避免帮助文案堆积。

---

## 6. No Technical Metadata

禁止首屏：

```text
FLAC
96kHz
24bit
LUFS
DSP
AI
Preset
Playback ID
Asset Version
Cloud
Ear
```

这些不是用户当前需要理解的信息。
