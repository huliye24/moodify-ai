# 给 Codex 的起始指令

执行 **MFD-002 — Electron Foundation**。

首先读取 MFD-001 最终交付，并确认：

> `MFD-002 = GO`

如果 MFD-001 是 NO-GO，停止。

然后依次阅读本包：

1. `00_README.md`
2. `01_MFD-002_TASK.md`
3. `02_ARCHITECTURE_BASELINE.md`
4. `03_SECURITY_BASELINE.md`
5. `04_IMPLEMENTATION_SEQUENCE.md`
6. `05_ACCEPTANCE_GATE.md`

你的目标不是开发 Moodify 的播放功能，而是建立一个安全、可运行、可测试、可构建的 Electron Desktop Foundation。

严格禁止跨入 MFD-003 / MFD-004：

- 不接真实 Moodify Cloud
- 不放 service key
- 不登录
- 不播放真实歌曲
- 不写 DSP
- 不写 WASAPI
- 不做正式播放器 UI
- 不做安装器产品化

完成后必须给出真实证据，并明确：

> `MFD-003: GO / CONDITIONAL GO / NO-GO`
