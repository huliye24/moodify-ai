# MFD-001 仓库事实快照

**生成时间:** 2026-08-20
**任务:** MFD-001 Moodify Desktop Authority & Boundary
**阶段:** A1 — 只读调查

---

## Git 状态

| 项目 | 值 |
|---|---|
| 仓库路径 | `E:\moodify\` (huliye24/moodify-ai) |
| 当前分支 | `codex/moodify-classic-reconstruction-001` |
| HEAD commit | `ee160ecd feat(player): converge Moodify Web Player public surface` |
| 工作区状态 | **DIRTY** — 有 Android 相关未提交修改和未跟踪文件 |
| 根目录 | 存在，monorepo 结构 |

## 根级权威文件

| 文件 | 状态 | 说明 |
|---|---|---|
| `AGENTS.md` | ✅ EXISTS | 已正确定义产品身份为 Moodify Music / Player |
| `README.md` | ✅ EXISTS | 已收敛，Ear 为内部系统 |
| `docs/REPOSITORY_STATUS.md` | ✅ EXISTS | 状态入口，Canon v1.1 |
| `docs/canon/CURRENT_ARCHITECTURE.md` | ✅ EXISTS | 现状架构（非理想图） |
| `docs/canon/PRODUCT_BOUNDARY.md` | ✅ EXISTS | 产品边界定义清晰 |
| `docs/canon/AUTHORITY_ORDER.md` | ✅ EXISTS | 权威顺序定义 |

## 架构文档

| 文档 | 状态 |
|---|---|
| docs/canon/CURRENT_CANON.md | ✅ EXISTS |
| docs/canon/INTERNAL_SYSTEMS.md | ✅ EXISTS |
| docs/canon/CANON_CHANGELOG.md | ✅ EXISTS |
| docs/LEGACY_AND_EXPERIMENTAL_POLICY.md | ✅ EXISTS |

## 客户端应用 (apps/)

| 目录 | 状态 | 技术 |
|---|---|---|
| apps/android | ⚠️ LEGACY | 旧版 Android |
| apps/music-android | ✅ PRESENT | Jetpack Compose + Media3 ExoPlayer |
| apps/music-web | ✅ PRESENT | Web Player / PWA |
| apps/ear-workbench | ✅ PRESENT | 内部 Ear 工具 |
| apps/tools | ✅ PRESENT | 工具集 |

## Cloud / BFF / API

| 组件 | 路径 | 状态 |
|---|---|---|
| Music BFF API | moodify-music-package/src/moodify_music/api/ | ✅ PRESENT |
| BFF Boundary | moodify-music-package/src/moodify_music/bff/ | ✅ PRESENT |
| Music Models | moodify-music-package/src/moodify_music/models.py | ✅ PRESENT |
| DB Migrations | moodify-music-package/alembic/ | ✅ PRESENT |

## 音频 Core / Ear / Research

| 目录 | 状态 |
|---|---|
| moodify-core-package/ | ✅ CANONICAL |
| experiments/ | ✅ EXPERIMENTAL |
| science/ | ✅ PRESENT |
| phys-lab/ | ✅ EXPERIMENTAL |

## CI / Build / Release

| 系统 | 状态 |
|---|---|
| .github/ | ✅ PRESENT (GitHub Actions) |
| deliverables/ | ✅ PRESENT (APK releases) |

## Desktop 客户端痕迹检查

| 检查项 | 结果 |
|---|---|
| Electron 配置 (package.json electron) | ❌ ABSENT |
| Electron 源码 | ❌ ABSENT |
| Tauri 配置 | ❌ ABSENT |
| Node desktop 实现 | ❌ ABSENT |
| docs 中 desktop 引用 | ❌ ABSENT (除本任务包外) |
| .desktop 文件 | ❌ ABSENT |

**结论:** 仓库中不存在任何现有 Desktop/Electron/Tauri 实现。MFD 将从零开始。

---

## 云端运行时状态 (来自 CURRENT_ARCHITECTURE.md W01-P00)

### LA VPS (103.144.246.242)
- nginx :80
- moodify-api :8000 (FastAPI, 127.0.0.1)
- moodify-music :3100
- moodify-music-bff :8100
- moodify-audiolla docker (:18080→8000)

### 杭州 VPS (120.55.191.146)
- moodify-api :8000 (公网, service-key 鉴权)
- moodify-data-worker
- SQLite + 历史批处理 6.5GB

### 存储
- PolarDB: 3 实例 (schema 空转或近空)
- OSS/S3/R2: NOT_PROVISIONED
- 云端 AI 推理: 无 (无 GPU)

### 真实主链
1. **静态音乐托管链 (运行中):** 网站 → nginx → music-bff → music-media → 浏览器/App
2. **数据工厂批处理链 (历史运行):** 杭州 worker → SQLite (10曲 pilot 全 SUCCEEDED)
3. **完整 Ear 链路 (仅仓库代码):** Listen→Judge→Intervene→Verify (云端无生产流量)

---

*本快照基于真实文件、真实代码和真实运行证据。未经验证的能力未标记为 PRODUCTION。*
