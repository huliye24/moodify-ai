# MFD-005 — Moodify Minimal Player

**项目：** Moodify  
**阶段：** Moodify Desktop Phase 1 — Windows Alpha  
**任务包编号：** MFD-005  
**日期：** 2026-08-20  
**执行对象：** Codex  
**性质：** 产品界面收敛 / 极简交互 / 第一版可见产品  
**优先级：** P0  
**前置任务：** MFD-004 — Playback Vertical Slice  
**后续任务：** MFD-006 — Reliability & Local State

---

## 1. 本包目的

MFD-004 已经证明：

> Desktop 可以从真实 Moodify Cloud 获取真实播放资源，并在 Windows 上真正播放。

MFD-005 不再继续增加底层能力。

本包只做一件事：

> **把工程调试播放器收敛成第一版真正的 Moodify Player。**

---

## 2. 产品原则

Moodify Desktop 0.1 不是：

- foobar2000
- Poweramp
- Spotify
- Apple Music
- DAW
- 音频调试台

Moodify 的核心体验不是：

> “给用户更多音频参数。”

而是：

> **把复杂度留给 Moodify，用户只需要 Play。**

---

## 3. 首版用户界面

第一版只保留用户真正需要的东西：

```text
                Moodify


            [ Vinyl / Disc ]

              Song Name
                Artist


                  ▶


          ───────●────────
```

必要时增加：

- 播放 / 暂停
- 上一首 / 下一首
- 进度
- 音量
- 极轻量错误状态
- 极轻量加载状态

不要增加第二层复杂导航。

---

## 4. 交互主线

核心行为：

```text
打开 Moodify
→ 自动恢复当前可播放曲目
→ Play
→ 上下 / 滚轮切歌
→ Pause
→ Seek
```

用户不应该看到：

- stems
- analysis
- DSP
- preset 参数
- Ear 判断
- processing graph
- codec 调试数据
- playback manifest
- signed URL
- Cloud 状态机

---

## 5. 本包不做

- 登录流程产品化
- library 大页面
- 复杂歌单
- 搜索
- 收藏
- 推荐
- 社区
- 皮肤市场
- 歌词
- visualizer
- waveform
- 频谱
- EQ
- DSP
- WASAPI
- 系统媒体键
- tray
- auto-update
- installer 产品化
- 离线完整缓存

---

## 6. 验收句

MFD-005 通过后，应该能够说：

> **用户第一次打开 Moodify Desktop，不需要理解技术，也知道如何听歌。**
