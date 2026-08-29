# 03 — Industrial Roadmap / 产业化路线图

> **Document Type:** Industrial Documentation System
> **Date:** 2026-08-23
> **Authority:** Roadmap document (not Canon). Statuses distinguish verified capability from plan.

---

## 总览

```
2026 Q3          2026 Q4          2027 H1          2027 H2+
─────┬───────────────┬───────────────┬─────────────────┬──────
  引擎抽取         产品模块上线       商业化落地         产业平台
  Engine         Product        Commercialize      Industry
  Extraction     Modules        & Partners         Platform
```

---

## Phase 1 — Research Foundation（已完成）

**状态：✅ 完成**

- 可复现的分析、诊断、受控处理、测量工作流（v0.1.0 mainline）
- 数据工厂 10 曲 pilot 全部 SUCCEEDED（完整证据链）
- LUFS / True Peak / 频谱 / 立体声 / 动态范围测量能力（已验证）
- MRS 评分框架 + 不确定性量化
- Android App（v2.0.0/3.1）+ Web PWA 上线
- 证据：`docs/REPOSITORY_STATUS.md` Capability Table

---

## Phase 2 — Engine Extraction（当前阶段）

**状态：🚧 进行中**

### 目标
把 Moodify Intelligence Engine 从单体中抽取为独立、可测试、有清晰 API 的能力层。

### 任务清单

| # | 任务 | 验收标准 |
|---|------|---------|
| 2.1 | engine/acoustic_analysis 模块迁移 | 从 `auditory/` 迁移 LUFS/true_peak/spectrogram/stereo，测试全绿 |
| 2.2 | engine/audio_features 模块迁移 | 从 `v01_analyzer.py` 迁移特征提取，测试全绿 |
| 2.3 | engine/scoring_engine 模块迁移 | 从 `mrs/` 迁移评分，基准对齐 |
| 2.4 | engine/music_understanding 迁移 | 从 `diagnosis/` 迁移，测试全绿 |
| 2.5 | 引擎统一 API 契约 | `/api/v1/engine/*` schema 冻结 + 契约测试 |
| 2.6 | 兼容 shim 机制 | 旧 import 路径继续工作（渐进迁移） |
| 2.7 | 引擎性能基准 | 单曲分析时间基线建立 |

### 里程碑
- **M2.1** 引擎五大模块全部迁移完成，CI 绿
- **M2.2** 引擎 API v1 契约冻结

---

## Phase 3 — Product Modules

**状态：⏳ 计划中**

### 目标
QA / Master / Rating / Supply 四个产品模块作为独立可部署服务上线。

### 任务清单

| # | 任务 | 依赖 |
|---|------|------|
| 3.1 | **QA MVP** — LUFS 合规检查 + 平台标准（Spotify/Apple/YouTube）+ QA 报告 | M2.1 |
| 3.2 | QA API（`/api/v1/qa/*`）+ 批量检测 | 3.1 |
| 3.3 | **Master MVP** — 三预设处理链 + 身份保护门 + 证据输出 | M2.1 |
| 3.4 | Master API + 处理前后对比报告 | 3.3 |
| 3.5 | **Rating MVP** — 价值评分 + 情绪标签 + S/A/B/C/D 分级 | M2.3 |
| 3.6 | **Supply MVP** — 音频相似搜索 + 场景匹配原型 | M2.5 |
| 3.7 | Stem separation 服务化（demucs 接入 supply/stems） | 3.6 |

### 里程碑
- **M3.1** QA 产品可对外演示（上传→检测→报告闭环）
- **M3.2** Master 产品可对外演示
- **M3.3** Rating/Supply 原型完成

---

## Phase 4 — Commercialization & Partners

**状态：⏳ 远期**

| # | 任务 |
|---|------|
| 4.1 | QA API 商业化（调用计费 + 批量 SaaS） |
| 4.2 | 合作伙伴接入（音乐平台/AI 音乐工具公司） |
| 4.3 | Rating 目录评级服务（版权方/基金试点） |
| 4.4 | Supply 商业用乐匹配（游戏/影视/广告试点客户） |
| 4.5 | GPU 推理基础设施（云端分轨/大规模检测） |
| 4.6 | 对象存储接入（OSS/S3/R2） |
| 4.7 | 白皮书发布 + 产业合作发布 |

---

## 关键依赖与风险

| 风险 | 影响 | 缓解 |
|------|------|------|
| 引擎迁移破坏现有功能 | 主链中断 | 兼容 shim + 每步测试 + 不删除旧代码 |
| MRS 有效性未经验证 | Rating/QA 商业化受阻 | 明确标注 research status；听测验证前置 |
| 无 GPU 基础设施 | 分轨/大规模处理受限 | Phase 4 再投入；CPU 路径先行 |
| 云端无生产流量 | 商业叙事空心 | QA MVP 优先做出可演示闭环 |
| 单人开发带宽 | 进度不可控 | 严格按里程碑裁剪范围 |

---

## 完成定义（每个阶段）

- 代码：测试全绿 + ruff 通过 + CI 绿
- 文档：架构文档同步更新
- 证据：能力状态表更新（不虚构）
- 演示：每个产品模块有可演示的闭环
