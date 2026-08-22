# 给 Codex 的起始指令

执行 **MFD-005 — Moodify Minimal Player**。

先确认 MFD-004 最终结论：

> `MFD-005 = GO`

然后完整阅读：

1. `00_README.md`
2. `01_MFD-005_TASK.md`
3. `02_UI_CONTRACT.md`
4. `03_INTERACTION_MAP.md`
5. `04_VISUAL_SYSTEM_BASELINE.md`
6. `05_UI_TEST_MATRIX.md`
7. `06_IMPLEMENTATION_SEQUENCE.md`
8. `07_ACCEPTANCE_GATE.md`

本包不再开发新的音频能力。

唯一目标：

> **把 MFD-004 的 development playback harness 收敛成第一版真正的 Moodify Minimal Player。**

核心原则：

- Play 是首屏最重要的动作；
- 用户只看到曲目、播放、切歌、进度、音量；
- 黑胶 / Disc 可以作为极简核心视觉；
- 技术复杂度继续留在 Cloud / Ear 内部；
- debug harness 必须退到 dev-only；
- 不把 Desktop 做成 foobar / Poweramp / Spotify。

禁止：

- library 大页面
- search
- upload
- favorite
- recommendation
- lyrics
- visualizer
- DSP/EQ
- WASAPI
- tray
- media key
- auto-update
- installer productization
- skin marketplace

完成后用真实云端歌曲做 Windows smoke。

最后明确：

> `MFD-006: GO / CONDITIONAL GO / NO-GO`
