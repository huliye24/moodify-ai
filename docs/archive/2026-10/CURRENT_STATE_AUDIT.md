# CURRENT_STATE_AUDIT.md — Moodify 仓库现实审计

> **性质：** STEP 1 交付物。只记录现实，三者分离：Canon 现实 / 代码现实 / 测试现实。
> **规则：** 未验证不写成已运行；不根据旧文档猜测现实。
> **日期：** 2026-09-17

---

## 1. 仓库身份与分支（最重要的事实）

| 项 | 现实 |
|---|---|
| 本地路径 | `E:\moodify` |
| remote | **两个**：`moodify` → `huliye24/moodify.git`；`origin` → `huliye24/moodify-ai.git` |
| 当前分支 | `codex/mood-nodes-019-archived`（**MOOD 分支，非 moodify-ai main**） |
| 工作树状态 | **脏**：`apps/web/*` 有未提交 MOOD 改动（genesis/token/treasury/nodes/security/network），`docs/canon/CANON_CHANGELOG.md` 已有未提交 MOOD 条目 |
| GitHub `moodify-ai` main | 干净；247 commits；停更 08-23；README=infra 叙事；**无 `protocol/`** |

> 本次所有 Canon 编辑发生在上述 MOOD 分支的工作树，**未提交**。提交前需先切到干净的 `moodify-ai` 主线（见 §7 结论）。

---

## 2. Canon 现实（`docs/canon/*`）

- **CURRENT_CANON v1.1**：对外产品 = Moodify Music / Player，核心动作 = `PLAY`；2026-08-19 明确把 "Auditory Intelligence Infrastructure" 排除出公共第一叙事。
- **PRODUCT_BOUNDARY v1.1**：对外只有一个 `PLAY` 面。
- **AUTHORITY_ORDER v1.1**：8 级顺序（人类指令 > AGENTS > canon > runtime evidence > …）。
- **INTERNAL_SYSTEMS**：Ear / Cloud Production / state machine / 外部能力（Audiolla/FFmpeg/Demucs/Basic Pitch）为内部。
- **与 README 冲突**：README 第一行 = "AI Audio Intelligence Infrastructure"，与 Canon 的 PLAY 冻结直接打架 → README 是「权威孤儿」。

---

## 3. 代码现实（真实 Core 资产在 legacy，engine 只是 facade）

### 3.1 真正的 DSP/分析资产在 `moodify-core-package/src/moodify/`（30+ 模块）

- `auditory/`（26 模块：loudness/true_peak/stereo/spectrogram/comparison/identity/uncertainty/…）
- `processing/`（`pedalboard_chain.py`、`spectral_chain.py`、`operators.py`）
- `intervention/`（`primitives.py`、`registry.py`、`pipeline.py`、`identity_gate.py`）
- `identity_guard/`、`safety/`、`optimizer/`、`mrs/`、`contracts/`、`authority/`
- `v01_*`（`v01_pipeline`：Import→Analyze→Diagnose→Process→Export）
- `data_plane/delivery.py`（W01-P06）：**Playback Delivery** — READY→playback metadata→signed URI→session，含 `device_class` 元数据。这是「交付预渲染对象」，**不是**「实时动态渲染」。

### 3.2 `engine/` = facade（`PHASE_B_T0_5_FACADE_LIVE`）

- 5 模块 + `report_schema/`；数学委托 legacy。`recommendation_engine/`、`contracts/` 为空 `__init__`。

### 3.3 CLI 现实：两套

| CLI | 入口 | 命令 |
|---|---|---|
| `demo/cli.py` | `moodify`（demo/pyproject） | 仅 `analyze` |
| `moodify-core-package/src/moodify/cli.py` | legacy | analyze / identity-guard / era-diagnostic / process / batch / emotions / crafts / serve / v01-analyze / v01-process |

### 3.4 `products/` = 脚手架

- `qa/`、`rating/`：空 `__init__` + 空子目录；`master/`、`supply/`：文档骨架 + migration source 表，无真实迁移代码。

### 3.5 `apps/`

- `web/`（Next.js，README 所指）、`music-android/`、`android/`（**与 music-android 重复**）、`ear-workbench/`、`tools/`。

### 3.6 无 root 构建 manifest

- 无根 `pyproject.toml` / `package.json`；每包各自 manifest。

### 3.7 命名债

- `moodify-core-package/pyproject.toml` 的 `description` 仍是 **"The Ear of AI: an auditory intelligence system…"**（旧身份残留）。

---

## 4. 测试现实

- `tests/`：`test_api.py`、`test_audio.py`、`test_mrs.py` + `conftest.py`（+ ear_batch / fixtures / studio_session_prep / temporal_texture）。
- `engine/report_schema/`：`moodify_intelligence_report.schema.json` + `schema.py` + README。
- CI：`.github/workflows/` = `ci.yml` / `test.yml` / `release.yml` / `deploy.yml` / `moodify-temporal-texture.yml`。
- 全量 pytest 依赖 numpy/scipy/librosa/soundfile/pyloudnorm/pedalboard/fastapi；本会话只对**无依赖新增模块**做冒烟验证（见 §4 结论）。

---

## 5. profile / playback 现实

| 能力 | 现实 | 状态 |
|---|---|---|
| 播放 profile（`track.moodify.json`） | **不存在**；`auditory/profiles.py` 是「测量 profile」；`schemas/canonical/*` 是 production-case/evidence 契约 | MISSING（全新） |
| 实时动态播放（`core/playback`） | **不存在**；仅有 `data_plane/delivery.py` 的交付层 | MISSING（全新） |
| 多设备播放适配 | 架构文档自述 PARTIAL | PARTIAL |

---

## 6. Duplication Risk（关键工程债）

1. **多套处理路径**：`processing/pedalboard_chain` vs `spectral_chain` vs `reconstruction/pipeline`，canonical 归属不明。
2. **多套包**：`moodify-core-package` / `moodify-app` / `moodify-system` / `moodify-runtime` 重叠。
3. **双 CLI**：`demo`（analyze）vs legacy（一堆旧命令）。
4. **双 schema 家**：`engine/report_schema` vs `schemas/canonical`。
5. **双 android**：`apps/android` vs `apps/music-android`。
6. **MOOD 侵入**：`protocol/`、`web 3.0/`、`docs/mood/`、`web-3.0-…-MOOD_PASSPORT-015/`、18 个 `codex/mood-*` 分支。

---

## 7. 对本次 CANON_CHANGE 的关键结论

1. **`core/playback`（动态播放）是全新能力，不是重构**；现有 playback 只到「交付」层。
2. **`profiles`（播放 profile）是全新能力**；现有 profile 只是「测量 profile」。
3. **One Core 原则有现实基础但未收敛**：DSP primitives / intervention / identity_guard 已在 legacy，但分散、多路径、未统一入口。
4. **命名迁移**：`engine/` → `core/`；同时 `moodify-core-package` 的 "The Ear of AI" description 需随 Canon 变更一起修正。
5. **提交风险**：当前在 MOOD 分支 + 脏工作树。Canon 编辑不提交；落地前需切干净分支（`HUMAN_DECISION_REQUIRED` 见最终报告）。
