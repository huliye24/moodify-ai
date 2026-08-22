# 给 Codex 的起始指令

执行 **MFD-004 — Playback Vertical Slice**。

开始前确认 MFD-003 最终结论：

> `MFD-004 = GO`

然后完整阅读：

1. `00_README.md`
2. `01_MFD-004_TASK.md`
3. `02_PLAYBACK_ENGINE_CONTRACT.md`
4. `03_REAL_PLAYBACK_TEST_MATRIX.md`
5. `04_PLAYBACK_EVIDENCE_TEMPLATE.md`
6. `05_IMPLEMENTATION_SEQUENCE.md`
7. `06_ACCEPTANCE_GATE.md`

本包唯一目标：

> **从真实 Moodify Cloud 得到真实 PlaybackManifest，并在 Windows Electron Desktop 上真正听到真实歌曲。**

请严格保持最小纵向切片：

- 使用 ChromiumPlaybackEngine；
- 建立 PlaybackEngine 抽象；
- 实现 Play / Pause / Seek / Ended / Volume；
- 用 2–3 首真实 track 建立最小 Next / Previous；
- 测试 signed URL 过期；
- 测试网络中断；
- 做真实人工听觉确认。

禁止：

- 正式播放器 UI
- WASAPI
- C++ native audio
- DSP
- EQ
- 系统托盘
- 媒体键
- 离线完整缓存
- 皮肤
- 安装器产品化

没有“真实 Windows 发声”的证据，不得把 MFD-004 判定为完成。

最后明确：

> `MFD-005: GO / CONDITIONAL GO / NO-GO`
