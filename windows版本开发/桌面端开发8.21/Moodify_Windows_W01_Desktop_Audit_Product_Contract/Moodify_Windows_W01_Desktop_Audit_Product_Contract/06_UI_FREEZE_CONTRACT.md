# Moodify Windows UI Freeze Contract

**Reference:** `reference/current_windows_alpha.png`  
**Scope:** W01–W12 默认共同约束，除非未来人类明确批准视觉重构。

```text
VISUAL_REDESIGN = FORBIDDEN
```

## 1. 当前视觉语言必须保留

当前 Windows Alpha 的主要特征：

- 大量留白
- 明亮、低噪声背景
- Moodify waveform 作为中心视觉
- 顶部极简 header
- 左侧轻量 sidebar
- 主区围绕当前播放
- 强调色极少
- 黑色顶部“添加歌曲”作为清晰但克制的主动作
- Prev / Play / Next 低密度控制
- 不展示工程参数
- 不以封面墙、榜单、推荐流作为首页主结构

本图是**方向基准**，不是要求 pixel-perfect 复制。

---

## 2. 功能扩展优先级

新增能力的 UI 载体，按以下顺序优先考虑：

1. Context menu / 右键菜单
2. Secondary view / 二级页面
3. Modal / dialog
4. Popover
5. Inline state change
6. 最后才考虑增加常驻主按钮

例如 Track 右键可以容纳：

```text
播放
下一首播放
────────
添加到歌单 >
收藏
────────
在资源管理器中显示
从音乐库移除
```

而不需要把这些动作全部铺在主页。

---

## 3. 首页原则

首页持续回答一个问题：

> 我现在要听什么，以及现在正在播放什么。

首页不承担：

- 音频工程控制台
- Ear 调试
- Evidence
- Stem 管理
- 云端流水线详情
- 复杂设置矩阵
- 社交 feed
- 管理后台

---

## 4. Sidebar 原则

Sidebar 可以逐步承载：

- 我的歌单
- 当前播放
- 必要的 Library 入口（后续决定）
- 未来被批准的 Skin Community

但避免：

- 无限层级
- 功能目录树
- 技术模块导航
- 工作台化

---

## 5. 禁止样式漂移

本阶段禁止主动改成：

- Spotify clone
- Apple Music clone
- Poweramp 参数面板
- Dashboard
- Admin console
- Dense card grid
- Neon / gamer UI
- 大量渐变和玻璃拟态叠加
- 工程指标首屏

---

## 6. Product Boundary

用户看到的是：

```text
Music
→ Moodify
→ Play
```

内部可以有：

```text
Analyze
Stem
Judge
Intervene
Render
Verify
Evidence
```

但这些复杂度不应因为 Windows 端“功能补全”而重新泄漏到公开播放器界面。

---

## 7. W01 Rule

W01 本身只审计当前 UI 与交互，不做视觉开发。

如果发现 UI 缺失导致一个核心功能没有入口：

- 记录 interaction gap
- 提出最低噪声的交互建议
- 留给对应建设包执行
- 不在 W01 顺手重做页面
