# Moodify Design Tokens v1

**Document ID:** MFY-DESIGN-TOKENS-V1
**Version:** 1.0
**Date:** 2026-08-14
**Status:** APPROVED BASELINE — package MFY_SHARED_DESIGN_SYSTEM_AND_SHELL_001 (45)
**North star:** docs/design/MOODIFY_AESTHETIC_SYSTEM.md（六层审美系统）
**Scope:** 官网、Moodify Ear、Moodify Music 三入口共享设计语言；不共享业务权威。

这是**唯一 token 来源**。Web（`apps/music-web/app/tokens.css`）与 Android（`apps/android/.../ui/theme/Color.kt`）实现都从此表映射；三端不得出现三套漂移色值。

## 1. 色板（深色优先，默认主题为深色）

### 1.1 基础场域

| Token | Hex / 值 | 用途 |
|---|---|---|
| `bg` | `#05081E` | 石墨场域底（graphite field） |
| `surface` | `#0B0F2C` | 抬升面（输入、卡片内层） |
| `surface-subtle` | `rgba(255,255,255,.025)` | 悬浮/次表面 |
| `line` | `rgba(255,255,255,.075)` | hairline 边界 |
| `text` | `#F5F6FF` | 矿物白主文字 |
| `text-muted` | `#8D94B2` | 次级文字 |
| `text-faint` | `#59617F` | 弱信息（注释、时间戳） |

### 1.2 语义色（全端唯一语义）

| Token | Hex | 唯一含义 | 禁止 |
|---|---|---|---|
| `evidence` | `#7FB8A8` | 证据/进行中/已验证（mineral green，唯一 accent） | 不得用于装饰渐变 |
| `attention` | `#D9A466` | **仅**需要人注意（等待人工、审核待办） | 不得用于普通提示或成功 |
| `blocking` | `#C87070` | **仅**阻塞性失败（阻断错误、不可恢复） | 不得用于轻微警告 |
| `focus` | `#6A55FF` | 键盘焦点环 | — |
| `brand-violet` | `#6C48FF` | 品牌渐变起点（仅品牌时刻） | 不作为证据色 |
| `brand-cyan` | `#1EBCED` | 品牌渐变终点（仅品牌时刻） | 不作为证据色 |
| `on-accent` | `#FFFFFF` | 强调底上的文字（品牌/证据按钮） | — |
| `on-contrast` | `#05081E` | 高对比底上的文字（如 evidence 按钮面） | — |

### 1.3 封面占位（作品无图时的固定色组，非语义色）

`cover-violet #431D76/#8F42C0` · `cover-cyan #0C5384/#17B7D9` · `cover-blue #172A76/#315EE0` · `cover-rose #69224C/#DD4F8D` · `cover-amber #71421D/#D29C4F` · `cover-mint #145C62/#48B5A9`

## 2. 排版

| Token | 值 |
|---|---|
| 正文字体 | `Inter, "Noto Sans SC", "PingFang SC", sans-serif` |
| 展示字体 | `Georgia, "Noto Serif SC", serif`（标题/品牌时刻） |
| 数字 | tabular-nums（证据、时长、数值对齐） |
| 字号阶梯 | 10 / 11 / 12 / 13 / 14 / 16 / 20 / 24 / 32 / 40 / 48 px |
| 行高 | 1.4（正文 13–14 用 1.7–2.0） |
| 字重 | 400 常规 / 600 半粗（仅小号标签与强调） / 700（导航品牌） |

## 3. 间距与圆角

- 基础单位 4；阶梯 4 / 8 / 12 / 16 / 24 / 32 / 48。
- 圆角：8（紧凑控件）/ 12（卡片）/ 16（面板、表单卡）/ 999（pill、胶囊按钮）。
- hairline 边界优先于阴影；层级靠亮度与留白，不靠投影堆叠。

## 4. 动效

| Token | 值 |
|---|---|
| 时长 | 150ms（状态变化）/ 200ms（过渡）/ 400ms（大型进入） |
| 缓动 | ease-out（进入）、ease-in-out（状态过渡） |
| reduced-motion | 全局 `@media (prefers-reduced-motion: reduce)` 关闭非必要循环与位移动画 |

## 5. 状态语义（组件可接受状态，不自推判断）

| 状态 | 语义色 | 允许出现 |
|---|---|---|
| ready | 中性 | 可操作 |
| processing / in progress | `evidence` | 进行中（证据/进度） |
| human required | `attention`（amber） | **仅**等待人工 |
| inconclusive / pending | 中性 + 明确文字 | 不确定 |
| failed / blocked | `blocking`（red） | **仅**阻塞失败 |
| empty / offline | 中性（text-faint） | 空态/离线 |
| disabled | 降透明度（opacity .45），不改语义色 | 不可操作 |

## 6. 使用与禁止规则

**允许**
- 证据、进度、已验证 → `evidence`；
- 等待人工、审核待办 → `attention`；
- 阻塞性失败、不可恢复错误 → `blocking`；
- 品牌时刻（hero、wordmark 渐变）→ `brand-violet`→`brand-cyan`。

**禁止**
- 用紫色渐变表示证据或进度；
- 用 amber 表示成功或普通提示；用 red 表示轻微警告；
- 组件内部推导 Ear 判断或 Music 发布结论（组件只接受状态 prop）；
- 新建未登记的颜色值（新色必须进本表再使用）。

## 7. Web/Android 映射

| Token | Web CSS | Android |
|---|---|---|
| bg | `--bg` | `Background`（dark scheme `Field`） |
| evidence | `--evidence` | `Evidence`（替代 MoodifyGreen/Signal/连接绿三套） |
| attention | `--attention` | `HumanAttention`（替代 MoodifyOrange 装饰用法） |
| blocking | `--blocking` | `Blocking`（替代 MoodifyCritical + ConnectionCard `#E05B5B` 双红） |
| 字号/间距/圆角 | CSS 变量 + spacing 阶梯 | Type.kt / Dp 常量 |

Android 实现文件：`apps/android/app/src/main/java/com/moodify/app/ui/theme/Color.kt`、`Theme.kt`（dark scheme 接线）。
