# Human Authority Baseline — 2026-08-20

**Authority level: HUMAN / CURRENT / CANONICAL INPUT**

本文件是 MFD-001 的人类输入基线。

若仓库内旧文档与本文件冲突：

> **以本文件代表的 2026-08-20 最新人类决策为准。**

但执行者仍必须保留真实历史，不得通过删除历史来伪造连续性。

---

# 1. 当前产品定义

Moodify 当前阶段的对外品牌与产品，不再要求用户理解“AI 的耳朵”这一内部技术概念。

当前产品表达：

> **Moodify — 让音乐更好听。**

当前用户产品：

> **Moodify Player / Moodify Music**

核心体验：

> **Play**

用户提供或选择音乐，Moodify 内部完成必要处理和播放决策，用户得到适合播放的版本与体验。

---

# 2. Ear 的新位置

Moodify Ear 不废弃。

Moodify Ear：

- 是内部听觉智能系统；
- 是研究系统；
- 是判断与验证系统；
- 可以继续积累听觉知识与证据；
- 可以服务 Cloud；
- 可以服务 Playback Decision；
- 不作为当前阶段独立公开产品上线。

因此：

```text
Moodify != Moodify Ear only

Moodify
├── Player
├── Cloud
└── Ear
```

---

# 3. 对外与对内复杂度

对外：

```text
Music
  ↓
Moodify
  ↓
Play
```

对内可以是：

```text
Acquire
→ Scan
→ Analyze
→ Separate when needed
→ Judge
→ Process / Reconstruct
→ Verify
→ Playback decision
→ Asset
→ Delivery
```

内部流程不得被误认为首版 UI。

---

# 4. 每首歌专属播放

阶段性产品机制：

> Moodify 尝试为不同歌曲建立不同的播放处理与播放决策，使“同一首歌用 Moodify 听起来更好”。

这不是要求在客户端展示 EQ / DSP 参数。

相反：

> 用户不需要成为音频工程师。

Poweramp / foobar / Neutron 等产品的重要启发，在于证明播放链与参数能够显著改变听感；Moodify 的方向是把这些复杂选择自动化、云端化、歌曲级化。

---

# 5. 客户端产品线

```text
Moodify Player
├── Android
├── Desktop
│   └── Windows first
└── iOS later
```

iOS 暂缓的现实原因：

- 当前缺少 Mac 开发设备。

因此先发展 Desktop。

---

# 6. Desktop 技术选择

已确认：

> **Electron**

原因包括：

- 团队已有 Electron 经验；
- 快速进入执行；
- UI 与客户端壳层不是 Moodify 核心技术壁垒；
- 后续可复用到 macOS / Linux；
- 更适合建立 `Moodify Desktop` 而不是 Windows-only 思维。

但：

> Electron 只是客户端技术，不是 Moodify 的音频智能中心。

---

# 7. Desktop 第一阶段原则

不要追求：

- 最强桌面播放器；
- 最多设置项；
- 最复杂音频面板；
- 模仿 foobar；
- 模仿 Poweramp；
- 模仿 Spotify。

首版目标：

> **Windows 用户打开 Moodify，按下 Play，稳定听到 Moodify 为这首歌准备好的播放版本。**

---

# 8. 后续阶段

MFD-001：Authority & Boundary  
MFD-002：Electron Foundation  
MFD-003：Desktop–Cloud Contract  
MFD-004：Playback Vertical Slice  
MFD-005：Minimal Player  
MFD-006：Reliability & Local State  
MFD-007：Windows Productization  
MFD-008：Alpha Release Gate
