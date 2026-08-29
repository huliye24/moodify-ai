# Design System Migration List

**Document ID:** MFY-DESIGN-MIGRATION-001
**Version:** 1.0
**Date:** 2026-08-14
**Package:** MFY_SHARED_DESIGN_SYSTEM_AND_SHELL_001 (45)
**Status:** LIVE — 逐页迁移，未要求一次性重写

## 1. Foundation-First 盘点（开工门结论）

| 区域 | 分类 | 结论 |
|---|---|---|
| apps/music-web `app/globals.css` | **ADAPT** | 4 个 CSS 变量 + 暗色布局作为种子；60+ 硬编码 hex 全部 COMPLETE 进 tokens.css；旧类名保留至页面迁移 |
| apps/music-web 页面 UI（内联样式） | **ADAPT→逐页迁移** | 无组件层；45 建组件层，46/49 逐页替换 |
| apps/android `ui/theme/Color.kt` | **KEEP（唯一 token 源）** | 归并三绿/双红/琥珀为规范语义 token（Evidence/Attention/Blocking）；instrument 暗色板接线 darkColorScheme |
| apps/android 屏幕硬编码色值 | **ADAPT** | 6 文件红绿琥珀统一为语义 token；其余装饰色保留至屏幕迁移（47） |
| apps/music-android | **ISOLATE** | 纯 M3 默认原型壳，不反向污染设计系统；产品化时整体重建（49/50 决策留/退） |
| ops/web_origin/site | **ISOLATE** | 运维遗留 JS 注入，无样式面，不进设计系统（46 负责官网内容化） |
| docs/design/MOODIFY_AESTHETIC_SYSTEM.md | **KEEP（北向输入）** | 设计哲学；具体值 COMPLETE 进 design_tokens_v1.md |

## 2. 45 包交付物

| 产物 | 位置 | 说明 |
|---|---|---|
| Token 单一来源 | docs/design/design_tokens_v1.md | 规范色板/排版/间距/动效/语义 + Web/Android 映射 |
| Web token 实现 | apps/music-web/app/tokens.css | CSS custom properties（唯一色值来源） |
| 组件库 | apps/music-web/components/ui/ | primitives / status / audio / surfaces / data / states 六组无业务权威组件 |
| 组件陈列 | apps/music-web/app/design/page.tsx | Storybook 等价物（全部状态截图证据面） |
| a11y 基线测试 | apps/music-web/tests/design-system.test.mjs | token 单一来源 / 语义纪律 / 焦点环 / reduced-motion / 无 autoplay / 可访问名称 |
| Android token 归并 | apps/android/.../ui/theme/Color.kt、Theme.kt | 三绿双红琥珀归一 + dark scheme |
| 迁移清单 | 本文档 | KEEP/ADAPT/COMPLETE/ISOLATE + 逐页计划 |

## 3. 逐页迁移计划（46/47/49 消费）

| 页面 | 迁移动作 | 包 |
|---|---|---|
| /design（陈列） | 已迁移（45） | 45 |
| 官网 /、/ear、/music、/evidence、/about、/contact | 新页面全部基于 tokens + 组件 | 46 |
| Music 首页 / Discover | 替换硬编码色为 token；nav/player 迁移到组件 | 49 |
| Music Track / Creator / Library / Studio | 同上前置工作，逐页替换 | 49/50 |
| Ear Android 屏幕（Home/Processing/NowPlaying…） | 语义色已统一；主题与布局对齐 instrument 暗色 | 47 |
| Ear web 工作台（若建） | 基于 tokens + 组件新建 | 47 |

迁移规则：每页迁移 = 完整可读组合；不批量替换全局；任一页回归可切回旧壳（回滚见 §5）。

## 4. 使用与禁止（摘要）

- 组件只接受状态 prop；不推导 Ear 判断或 Music 发布结论；
- amber 只用于"需人注意"；red 只用于阻塞失败；evidence green 是唯一进行/验证 accent；
- 禁止新建未登记色值；新色先进 design_tokens_v1.md 再使用；
- 三端使用同一字体/颜色/空间语法，导航、密度、主动作按产品不同（官网叙事 / Ear 仪器 / Music 作品）。

## 5. 回滚

- 设计系统经适配层（tokens.css + 组件）接入；页面级切回旧壳即可恢复旧视觉；
- 业务 API 与状态模型不随视觉回滚改变（包 45 验收要求）；
- Android：语义 token 别名保持旧名可用（MoodifyGreen→Evidence 等），逐屏回退无需改代码逻辑。
