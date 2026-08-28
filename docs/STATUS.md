# Moodify v1.0 Current Status

**日期：** 2026-08-24
**阶段：** Moodify Entropy Reduction 002 — Mainline Context Freeze
**性质：** v1.0 工作状态入口；不是新 Canon；引用 `AGENTS.md` + `docs/canon/*` + `docs/brand/public/*` + `docs/reduction/*`。
**CANON_CHANGE：** `NO`
**执行状态：** 仅入口文件；未修改、删除、移动任何业务代码或目录。

---

## Product Identity

Moodify Music / Moodify Player

---

## Primary Action

PLAY

---

## Current Mission

Build the simplest complete listening loop:

```
Cloud Prepared Track
      ↓
Moodify Player
      ↓
User Play
```

---

## Active Development

### KEEP

| 模块 | 路径 | 职责 |
|---|---|---|
| Web Player | `apps/web/` | 对外 Player 主入口；`page.tsx` + `listen/` + `evidence/` + `/library` |
| Android Player | `apps/music-android/` | 对外 Android Player；CI release 唯一工程 |
| Music BFF | `moodify-music-package/.../bff` | 唯一公开 API |
| Audio Intelligence | `moodify-core-package/src/moodify/` | Ear 内部核心；`v01_pipeline` + `data_factory` |
| Music Data Authority | `moodify-music-package/models.py` + Alembic | tracks / track_versions / favorites / play_events |
| Product Home | `ops/web_origin/site/rongjingmusic/` | `rongjingmusic.com` |
| Company Home | `ops/web_origin/site/rongjingwenchuan/` | `rongjingwenchuan.com` |
| Transition Player | `ops/web_origin/site/rongjinwenchuan/` | `.xyz` 过渡 |

### Cloud (Active — Build to READY)

| 节点 | 当前状态 | 目标 |
|---|---|---|
| LA VPS (ECS) | 运行：nginx + cloudflared + moodify-api + moodify-music + music-bff + worker + audiolla | 维持 |
| Hangzhou VPS (ECS) | 运行：moodify-api + moodify-data-worker + 4 timers + /var/lib/moodify | 升级到生产闭环 |
| OSS (Object Storage) | NOT_PROVISIONED | 存储音频资产 |
| PolarDB | BLOCKED（核验空转） | Music data authority 激活 |
| Worker / Queue | SQLite 队列（近空） | 生产 job queue |
| Cloud AI Inference | 无 GPU / 无模型 serving | 受控引入 |

---

## Frozen

**DO NOT DEVELOP**（以下方向冻结；恢复需 `CANON_CHANGE = YES`）：

| 方向 | 原因 |
|---|---|
| `moodify-qa` | 第二公开产品身份；违反 Canon 不变量 #1 |
| `moodify-qa-desktop` | 第三桌面产品；依赖 QA |
| `moodify-pulse` | 第二产品身份 "AI Emotional Music Container" |
| `apps/ear-workbench` | 内部研究工具；永远不进入公开导航 |
| Creator Studio / 发布 / 主页 / 关注 | 当前无 creator 产品证据 |
| Marketplace | 当前无商业闭环 |
| License Intent | 当前无成交证据 |
| Support / 支付意图 | 当前无真实支付 |
| CWC 积分账本 | 当前无用户闭环 |
| Creation Passport | 非 MVP 首次播放所需 |
| Enterprise API / SSO | 当前无企业用户 |
| Social features（关注 / 分享 / 协作歌单） | 当前无社交证据 |
| Billing / Credit ledger | 当前无收入模型 |
| MAMSE / Physics / LLM / Lyric / Transcription research | 研究资产；不进入主线 CI |
| Reconstruction Job（billing 未完成） | 真实生产 case 出现前不扩状态 |
| Second Android (`apps/android/`) | 与 `apps/music-android` 双 authority |
| Second Desktop | v1.0 不发布 Desktop |
| Multi-model research dashboard | 当前无生产流量 |
| Public Evidence dashboard | Evidence 属内部系统 |

---

## Decision Rule

Every new feature must answer:

> **Does this make users more willing to press Play again?**

If yes → Consider KEEP.
If no → FREEZE.

This rule is subordinate to `PUBLIC_BRAND_CONSTITUTION.md §13` 5-item test and `AGENTS.md §Judgment Authority`.

---

## Governance Entry Points

| 文件 | 角色 |
|---|---|
| `AGENTS.md` | 仓库最高认知入口 |
| `docs/canon/CURRENT_CANON.md` | 当前产品身份 |
| `docs/canon/PRODUCT_BOUNDARY.md` | 内外边界 |
| `docs/brand/public/PUBLIC_BRAND_CONSTITUTION.md` | 最高 Public Brand 主题权威 |
| `docs/reduction/MAINLINE_DECLARATION.md` | 主线声明 + 共享地图 |
| `docs/development/README.md` | 开发入口（本目录） |
| `docs/cloud/README.md` | Cloud Production 入口 |

---

**下一步：Cloud Production 001 — 上传 → 云端处理 → READY → Web 播放闭环。**