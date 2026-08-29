# MFD-002 Architecture Baseline

本文件定义本阶段推荐的 Desktop 基础边界。

---

## 1. Runtime

```text
Electron App
│
├── Main Process
│   ├── lifecycle
│   ├── native OS integration
│   ├── secure config
│   ├── IPC handlers
│   └── service orchestration
│
├── Preload
│   └── typed capability bridge
│
└── Renderer
    └── React UI
```

---

## 2. Authority

```text
Renderer owns:
UI state only

Main owns:
desktop runtime authority

Cloud owns:
business data authority

Ear owns:
internal auditory intelligence
```

本包不会连接 Cloud / Ear，但工程必须从一开始遵守这一边界。

---

## 3. Future modules

```text
domain/
├── session
├── library
└── playback
```

未来：

```text
renderer
  ↓
domain-facing services
  ↓
main/preload boundary
  ↓
Player API / BFF
```

不要让 renderer 自己散落 fetch。

---

## 4. Playback future

MFD-002 不实现播放。

但未来 Playback 应该能被替换：

```text
PlaybackEngine
├── ChromiumPlaybackEngine
└── NativeWindowsPlaybackEngine (future only)
```

现在只留概念边界。

---

## 5. Cross-platform

工程名应保持：

> `Moodify Desktop`

Windows 是第一发行平台。

目录和 package naming 不要锁死成 `moodify-windows`，除非 MFD-001 明确要求。

---

## 6. Dependency principle

首版依赖越少越好。

每新增一个包都应回答：

- 为什么原生平台 / 标准库不够？
- 是否影响 Electron 安全？
- 是否影响打包？
- 是否影响未来 macOS？
- 是否真正进入当前主线？
