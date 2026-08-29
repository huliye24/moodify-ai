# 02 — Technical Architecture / 技术架构

> **Document Type:** Industrial Documentation System
> **Date:** 2026-08-23
> **Authority:** Technical architecture overview. Detailed spec: `docs/MOODIFY_ARCHITECTURE_V1.md`. Current state: `docs/CURRENT_ARCHITECTURE.md`.

---

## 1. 架构总览

```
┌─────────────────────────────────────────────────────────┐
│  Application Layer                                       │
│  apps/web (Next.js) · Android · Desktop · Partner API   │
├─────────────────────────────────────────────────────────┤
│  Product Layer                                           │
│  products/qa · products/master · products/rating ·       │
│  products/supply                                         │
├─────────────────────────────────────────────────────────┤
│  Engine Layer — Moodify Intelligence Engine              │
│  engine/acoustic_analysis · engine/audio_features ·      │
│  engine/music_understanding · engine/scoring_engine ·    │
│  engine/recommendation_engine                            │
├─────────────────────────────────────────────────────────┤
│  Infrastructure Layer                                    │
│  shared/contracts · shared/authority · shared/safety ·   │
│  shared/node · shared/api                                │
└─────────────────────────────────────────────────────────┘
```

---

## 2. 技术栈

### 引擎与后端

| 组件 | 技术 | 用途 |
|------|------|------|
| 语言 | Python >= 3.10 | 引擎与后端 |
| Web 框架 | FastAPI 0.136 | REST API |
| 音频 I/O | librosa 0.11 / soundfile 0.13 | 读取 WAV/MP3/FLAC/M4A/OGG/AAC |
| 响度 | pyloudnorm 0.2 | LUFS 测量（ITU-R BS.1770） |
| DSP | pedalboard 0.9 | 处理链（EQ/压缩/限制） |
| 数值计算 | NumPy 2.4 / SciPy 1.17 | 信号处理 |
| 数据校验 | Pydantic 2.13 | Schema 契约 |
| 分轨（可选） | demucs / torch | Stem separation |
| 测试 | pytest | 单元 + 契约测试 |
| Lint | ruff | 代码质量（CI 强制） |

### 应用层

| 组件 | 技术 | 用途 |
|------|------|------|
| Web | Next.js 16 + React 19 | 播放器 PWA |
| 样式 | Tailwind CSS 4 | 设计系统 |
| ORM | Drizzle ORM | SQLite/D1 数据层 |
| 部署 | Cloudflare Workers | 边缘部署 |
| 桌面 | Electron + Vite | moodify-pulse |
| 移动 | Android (Gradle/Kotlin) | Moodify Music |

### 基础设施

| 组件 | 技术 | 用途 |
|------|------|------|
| 容器 | Docker multi-stage | API + Worker 镜像 |
| 编排 | docker-compose | 本地/单机部署 |
| 反向代理 | nginx | 多域名路由 |
| 隧道 | Cloudflare (cloudflared) | 公网接入 |
| 队列 | SQLite JobQueue | 任务队列（Redis 预留） |

---

## 3. 核心数据流

### 3.1 处理主链（v0.1.0 mainline，已验证）

```
Import → Analyze → Diagnose → Process → Export
```

### 3.2 数据工厂链（10 曲 pilot 已完成）

```
SOURCE → LISTEN → REPRESENT → JUDGE → ABC INTERVENTION → VERIFY
       → ALGORITHMIC REVIEW → DATASET → NEXT CASE
```

### 3.3 平台目标数据流

```
Audio Input → Engine (分析/特征/评分)
    → QA (质量判定) / Master (处理) / Rating (估值)
    → Supply (匹配/交付)
    → Applications (播放/展示)
```

---

## 4. 引擎设计原则

1. **纯函数** — 输入音频，输出分析结果；无副作用
2. **无产品逻辑** — 引擎不知道 QA/Master/Rating/Supply 的存在
3. **版本化输出** — 所有分析结果可复现、可追溯
4. **不确定性感知** — 每个评分携带不确定度
5. **证据支撑** — 每个判断产出 evidence artifact

## 5. 权限与安全模型

- **Scoped machine authority** — 机器只能在已验证、版本化、明确授权的范围内决策
- **Human escalation** — 超范围/证据不足/不确定的案例必须产生 `HUMAN_REQUIRED`
- **Safety bounds** — DSP 干预受安全边界约束（`shared/safety`）
- **Identity gate** — 处理不得破坏音乐身份（identity_guard）

## 6. API 架构

```
/api/v1/engine/*       # 引擎：分析、特征、评分
/api/v1/qa/*           # QA：检测、报告、合规
/api/v1/master/*       # Master：处理、预设、重建
/api/v1/rating/*       # Rating：评分、标签、分级
/api/v1/supply/*       # Supply：搜索、匹配、分轨、交付
```

每个产品模块独立命名空间，可独立部署为微服务（当前单体，渐进拆分）。

## 7. 部署拓扑（当前实况）

```
Cloudflare → LA VPS (nginx + moodify-api :8000 + music-web :3100 + bff :8100 + worker)
           → Hangzhou VPS (moodify-api + data-worker + SQLite)
PolarDB（已备未用）· 对象存储（未开通）· GPU 推理（未开通）
```

> 事实规则：未验证的云端能力不写成已运行（Canon R6/R10）。

## 8. 迁移状态

| 阶段 | 内容 | 状态 |
|------|------|------|
| Phase A | 新目录结构（engine/products/research/shared）+ README + 配置 | ✅ 完成（2026-08-23） |
| Phase A | apps/music-web → apps/web（git mv，历史保留） | ✅ 完成 |
| Phase B | 模块逐个迁移 + 兼容 shim + 测试 | ⏳ 待执行 |
| Phase C | 移除 shim，moodify-core-package 转为 legacy 参考 | ⏳ 未来 |
