# Migration Plan & Next-Stage Tasks / 迁移计划与下一阶段开发任务

> **Document Type:** Industrial Architecture Upgrade — Final Deliverable
> **Date:** 2026-08-23
> **Principle:** 渐进式迁移 · 不删除旧代码 · 不大规模重写 · 不破坏已有功能

---

## 1. 本次升级已完成的工作（Phase A）

| # | 变更 | 类型 |
|---|------|------|
| 1 | `docs/CURRENT_ARCHITECTURE.md` — 全仓库分析（现状/技术栈/模块关系/技术债务/可迁移模块） | 新增文档 |
| 2 | `docs/MOODIFY_ARCHITECTURE_V1.md` — 新平台架构规范（引擎/产品/应用/研究/共享五层） | 新增文档 |
| 3 | `engine/` — 五大引擎模块目录 + README + `__init__.py` | 新增结构 |
| 4 | `products/qa|master|rating|supply/` — 四产品模块目录 + README + config.yaml | 新增结构 |
| 5 | `shared/` — 共享基础设施目录（contracts/authority/safety/node/api） | 新增结构 |
| 6 | `research/` — papers（3 篇论文已就位）/ benchmarks / whitepapers | 新增结构 |
| 7 | `apps/music-web → apps/web`（git mv，历史保留；deploy.yml/脚本路径已同步） | 重命名 |
| 8 | `README.md` — 重写为 AI Audio Intelligence Infrastructure 定位 | 重写 |
| 9 | `docs/01-05` — 产业化文档体系（战略/架构/路线/商业模式/研究） | 新增文档 |
| 10 | `docs/WEBSITE_RESTRUCTURING_PROPOSAL.md` — 官网重构方案 | 新增文档 |

**未删除任何代码。** `moodify-core-package/` 原样保留，为当前唯一可运行实现。

---

## 2. 迁移计划（三阶段）

### Phase A — 结构建立 ✅（2026-08-23 完成）

- 新目录结构 + README + 配置占位
- 旧代码不动，新旧并存
- web 应用迁移至 `apps/web`（唯一代码移动，git 历史保留）

### Phase B — 模块迁移（下一阶段，逐模块执行）

**规则：** 每次迁移一个模块 → 更新 import → 跑测试 → 旧位置留兼容 shim → 提交。

**执行顺序（按依赖与价值排序）：**

| 步骤 | 迁移内容 | 从 → 到 | 验收 |
|------|---------|---------|------|
| B1 | 兼容 shim 机制建立 | `moodify-core-package` 内部 | 旧 import 路径不变 |
| B2 | 声学分析 | `auditory/` → `engine/acoustic_analysis/` | 测试全绿 |
| B3 | 特征提取 | `v01_analyzer.py`, `audio_io.py` → `engine/audio_features/` | 测试全绿 |
| B4 | 评分引擎 | `mrs/` → `engine/scoring_engine/` | 基准对齐 |
| B5 | 音乐理解 | `diagnosis/` → `engine/music_understanding/` | 测试全绿 |
| B6 | 共享设施 | `contracts/`, `authority/`, `safety/`, `node/` → `shared/` | 测试全绿 |
| B7 | QA 产品 | `diagnosis/quality_gate`, `mrs` 组合 → `products/qa/` | QA API demo |
| B8 | Master 产品 | `processing/`, `v01_presets`, `intervention/` → `products/master/` | Master API demo |
| B9 | Rating 产品 | `evaluation/`, `knowledge/` → `products/rating/` | Rating API demo |
| B10 | Supply 产品 | `stems/`, `data_factory/`, `data_plane/` → `products/supply/` | Supply API demo |
| B11 | 实验隔离 | `moodify_experimental/` → `research/experimental/` | 引擎不依赖实验代码 |

### Phase C — 收尾（远期）

- 移除兼容 shim
- `moodify-core-package/` 标记为 legacy 参考（保留，不删除）
- `apps/music-android` + `apps/android` 合并为 `apps/android`（需人工确认哪个是主线）
- 各产品独立 pyproject，可独立部署

---

## 3. 下一阶段开发任务列表（Phase B 详细任务）

### 引擎层

- [ ] **T1. shim 机制** — 在 `moodify-core-package/src/moodify/` 建立转发层，保证旧路径可用
- [ ] **T2. acoustic_analysis 迁移** — loudness/true_peak/spectrogram/stereo/icc → engine；配 `engine` 级测试
- [ ] **T3. audio_features 迁移** — analyzer + io；特征清单文档化
- [ ] **T4. scoring_engine 迁移** — MRS + metrics + benchmark；跑 baseline 对比（`tests/baseline/`）
- [ ] **T5. music_understanding 迁移** — diagnosis 模块；defect classifier 接口化
- [ ] **T6. recommendation_engine** — 从 `knowledge/emotion_targets.py` 起步，定义 similarity API
- [ ] **T7. 引擎 API v1** — `/api/v1/engine/analyze|features|score` schema + 契约测试
- [ ] **T8. 引擎性能基线** — 单曲分析耗时基准，写入 `research/benchmarks/`

### 产品层

- [ ] **T9. QA MVP** — LUFS 合规检查（Spotify/Apple/YouTube 标准）+ 报告生成 + `/api/v1/qa/check`
- [ ] **T10. Master MVP** — 三预设处理 + 身份保护门 + `/api/v1/master/process`
- [ ] **T11. Rating MVP** — 价值评分 + 情绪标签 + 分级 + `/api/v1/rating/score`
- [ ] **T12. Supply MVP** — 相似搜索原型 + 场景匹配 + `/api/v1/supply/search`
- [ ] **T13. Stem 服务化** — demucs 接入 `products/supply/stems`，容器化

### 文档与品牌

- [ ] **T14. Canon 更新** — `docs/canon/` 增补平台架构（CANON_CHANGE 记录至 CANON_CHANGELOG）
- [ ] **T15. AGENTS.md 更新** — 加入 engine/products 结构说明
- [ ] **T16. 官网重构** — 按 `docs/WEBSITE_RESTRUCTURING_PROPOSAL.md` 执行 P0 项（Hero + 四支柱）
- [ ] **T17. 白皮书 #1** — 《The Intelligence Layer for Music》
- [ ] **T18. SDK 对齐** — `sdk/` 面向新引擎 API 更新

---

## 4. 目录结构对照

### 目标结构（用户指定）

```
moodify-ai/
├── engine/                  ✅ 已建立
│   ├── acoustic_analysis/
│   ├── audio_features/
│   ├── music_understanding/
│   ├── scoring_engine/
│   └── recommendation_engine/
├── products/                ✅ 已建立
│   ├── qa/
│   ├── master/
│   ├── rating/
│   └── supply/
├── apps/
│   └── web/                 ✅ 已迁移（原 music-web）
├── research/                ✅ 已建立
│   ├── papers/              ✅ 3 篇论文已就位
│   ├── benchmarks/          ✅ 基准已复制
│   └── whitepapers/         ✅ 规划文档就位
├── docs/                    ✅ 文档体系完成
│   ├── CURRENT_ARCHITECTURE.md
│   ├── MOODIFY_ARCHITECTURE_V1.md
│   ├── 01_PRODUCT_STRATEGY.md
│   ├── 02_TECH_ARCHITECTURE.md
│   ├── 03_INDUSTRIAL_ROADMAP.md
│   ├── 04_BUSINESS_MODEL.md
│   ├── 05_RESEARCH_DIRECTION.md
│   └── WEBSITE_RESTRUCTURING_PROPOSAL.md
└── README.md                ✅ 已重写
```

### 保留的现状（渐进迁移中不动）

```
moodify-core-package/   # 当前唯一可运行实现（Phase B 逐步迁出）
apps/android/           # Android（与 music-android 合并需人工确认）
apps/music-android/     # Android 主线
apps/ear-workbench/     # 诊断工作台
moodify-pulse/          # 桌面应用（Phase C → apps/desktop）
shared/                 ✅ 新增（Phase B6 迁入）
```

---

## 5. 风险与守护

| 风险 | 守护措施 |
|------|---------|
| 迁移破坏主链 | 每步迁移跑全量测试；shim 保旧路径 |
| Canon 冲突 | CANON_CHANGE 已在架构文档声明；待人工批准后入 CANON_CHANGELOG |
| 双目录混淆 | 每个新目录 README 标注迁移状态与来源 |
| web 重命名遗漏 | deploy.yml/脚本已同步；历史 artifacts 保留原文不改 |

---

## 6. 建议的提交策略

```
commit 1: docs — Phase 1 分析文档（CURRENT_ARCHITECTURE.md）
commit 2: docs — 平台架构规范（MOODIFY_ARCHITECTURE_V1.md）
commit 3: structure — engine/products/shared/research 目录建立
commit 4: refactor — apps/music-web → apps/web（git mv + 引用同步）
commit 5: docs — 产业化文档体系（01-05）
commit 6: docs — 官网重构方案
commit 7: readme — README 重写为基础设施公司定位
```

小步提交，每步可回滚。
