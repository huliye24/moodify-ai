# MFD-004 — Playback Vertical Slice

**项目：** Moodify  
**阶段：** Moodify Desktop Phase 1 — Windows Alpha  
**任务包编号：** MFD-004  
**日期：** 2026-08-20  
**执行对象：** Codex  
**性质：** 第一条真实播放闭环 / Vertical Slice / Play 贯通  
**优先级：** P0  
**前置任务：** MFD-003 — Desktop–Cloud Contract  
**后续任务：** MFD-005 — Moodify Minimal Player

---

## 1. 本包的唯一目标

第一次把下面这条链路真正跑通：

```text
Moodify Desktop
    ↓
Player API / BFF
    ↓
PlaybackManifest
    ↓
Authorized Audio Asset
    ↓
Playback Engine
    ↓
Windows Audio Output
    ↓
Human Hearing
```

完成后，必须能够回答：

> **Windows 上的 Moodify 能不能从真实云端取得一首真实歌曲，并稳定播放出来？**

这就是本包的全部价值。

---

## 2. 为什么这是分水岭

MFD-001 建立权威。  
MFD-002 建立 Electron 地基。  
MFD-003 建立 Desktop–Cloud 契约。  

MFD-004 才第一次证明：

> **Moodify Desktop 是一个播放器，而不只是一个 Electron 壳。**

---

## 3. 本包只做最小播放能力

必须：

- 真实用户级会话；
- 真实 track；
- 真实 PlaybackManifest；
- 真实媒体资源；
- Play；
- Pause；
- Seek；
- Ended；
- 一个最小 Next / Previous 路径；
- 基础播放错误恢复；
- 播放状态可观测。

但不要把它扩成完整产品。

---

## 4. 本包不做

- 最终 UI
- Vinyl 动画
- 皮肤
- 歌单管理
- 收藏
- 推荐
- 系统托盘
- Windows 媒体键
- 自动更新
- 安装器产品化
- 离线完整缓存
- 本地音乐扫描
- 上传
- DSP 编辑
- EQ
- WASAPI Exclusive
- native C++ engine
- bit-perfect 宣称
- gapless
- crossfade
- lyrics
- waveform UI

---

## 5. 第一版播放引擎原则

首版优先：

> **Chromium / Web Audio / HTMLMediaElement 能正确播放，就先用它。**

不要因为“以后可能要极致音频”而阻塞第一条真实播放闭环。

但从第一天建立接口：

```text
PlaybackEngine
└── ChromiumPlaybackEngine
```

未来可以增加：

```text
PlaybackEngine
├── ChromiumPlaybackEngine
└── NativeWindowsPlaybackEngine
```

现在不要实现 Native。

---

## 6. 验收句

MFD-004 通过的唯一核心句：

> **打开 Moodify Desktop，取得真实云端曲目，点击 Play，Windows 能稳定发声，并完成基础播放控制。**
