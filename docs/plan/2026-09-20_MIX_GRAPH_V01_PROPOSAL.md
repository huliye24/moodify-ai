# MIX GRAPH v0.1 — 第一条完整 Stereo Finishing Session 提案

**日期：** 2026-09-20（提案）/ 2026-09-29（裁决通过，开工）
**Canon 依据：** v2.0 Professional Finishing（commit `a69c3e3c`）+ v2.1 Sound Protocol（commit `b6673830`），目标架构 `docs/MOODIFY_PROFESSIONAL_FINISHING_V1.md`（TARGET）
**状态：** APPROVED — 人类已裁决 5 项开工决策（记录见 §5.1），2026-09-29 开工
**性质：** 提案已批准；实现随 Mix Graph v0.1 工程包落地

---

## 1. 目标

打通 Canon v2.0 的第一条生产端完整链：

```text
input.wav
  → Moodify Analyze（v01_analyzer）
  → Diagnosis（v01_diagnostics）
  → mix_graph.json（会话权威表示）
  → EQ → Compression → Stereo → Limiter（processing/pedalboard_chain providers）
  → A/B（响度对齐预览）
  → Verification（before/after 测量 + evidence）
  → master.wav + evidence.json
```

验收口径：**可序列化、可重放、可旁路、可测试**。在四节点图通过前不增加任何新节点类型。

## 2. 现有资产 → Mix Graph 映射（全部复用，不建第二套）

| Mix Graph 概念 | 现有资产（CANONICAL，见 REPOSITORY_STATUS） | 用法 |
|---|---|---|
| Session Intake / Source | `audio_io.py` | 读入 stereo wav，落 source 指纹 |
| Analysis Pack | `v01_analyzer.py` | 生成 analysis pack，挂到 graph.analysis |
| Diagnosis | `v01_diagnostics.py` | 产出诊断项，作为节点 `reason` 的来源 |
| Plan / 参数初始化 | `v01_presets.py` | 诊断 → 初始参数（rule/heuristic 策略） |
| Processor Runtime | `processing/pedalboard_chain.py`、`processing/operators.py`、`processing/spectral_chain.py` | EQ / Compressor / Stereo / Limiter 四个 provider 包一层 provider 接口 |
| Export | `v01_exporter.py` | 渲染落盘 |
| Verification | treatment records / inspector / algorithmic review 体系 | before/after 测量 + evidence，不建第二套 evidence authority |
| Reference matching / 可微优化 | 暂缓 | v0.2+（参考 dasp-pytorch / matchering，见 reference map） |

## 3. 包边界

**做（v0.1）：**
1. `moodify-core-package/src/moodify/mix_graph/` 新包：
   - `schema.py` — `moodify.mix_graph.v0.1` schema + 校验（node/source/intent/verification/provenance）
   - `graph.py` — 序列节点模型：`enabled/bypass`、`parameters`、`reason`、`evidence_refs`、`version`、provenance
   - `providers/` — `base.py`（capabilities/validate/render/provenance 接口）+ `pedalboard_providers.py`（EQ、Compressor、Stereo、Limiter）
   - `session.py` — load → render → verify → export 的会话执行器（含 dry-run 与逐节点 before/after 测量）
   - `verify.py` — loudness/peak/dynamics before-after 对比，复用现有测量，产出 evidence 片段
2. `mix_graph.json` 读写 + **确定性重放**：同版本 core + 同 graph + 同输入 → 同输出（数值一致性以实测为准）
3. CLI：`moodify finishing new / render / verify / export`（或并入现有 CLI 结构，见待裁决）
4. 测试：schema 校验、bypass 语义（bypass 节点输出 = 短路）、重放确定性、四 provider 单测、一条 golden case 端到端
5. 证据：`artifacts/mix_graph_v01/`（golden case 输入/图/输出/evidence）

**不做（v0.1 显式排除）：**
- stem / bus / 并行图 / send-return（只做串行 stereo 链）
- reference matching、可微参数搜索（dasp-pytorch 路线）
- repair/repair-model providers（DeepFilterNet 路线）
- VST3/AU hosting（pedalboard 插件宿主路线）
- Web/Android 工作台 UI（App 端 Preview/A-B 属后续包）
- 真人盲听环节（沿用「全流程算法化」既定决策；verification 只出机器证据）

## 4. 完成门（沿用 MHP 四道门）

1. `ruff` 全绿
2. 新增测试 + `pytest -m v01` 全绿
3. 全量 pytest 全绿（LSM 模式 parallel=1）
4. GitHub Actions 绿（push 后确认）

另加 Canon 门：`python scripts/canon_guard.py` + `tests/test_canon_guard.py`。

## 5. HUMAN_DECISION_REQUIRED（开工前）——已于 2026-09-29 裁决

### 5.1 裁决记录（2026-09-29，人类确认"同意，去做吧"）

1. **模块归属**：✅ `moodify-core-package` 新包 `moodify.mix_graph`（One Core；协议运行时 `sound_protocol.py` 同在此包）。
2. **CLI 入口**：✅ **三层结构（修改原"二选一"）**——`mix_graph.json` schema 按**未来协议载荷**设计（AI 面 = 权威面）；`moodify finishing new/render/verify/export` 为薄封装（人/调试面）；v0.2 再把 graph 映射进 MSP 作业（protocol 0.1→0.2）。理由：产品定义确认为 CLI-first / Sound Protocol first（与 Canon v2.1 对齐），MSP/0.1 目前只允许 preset 选择，Mix Graph 补上"可编辑参数图"这一目标态。
3. **schema 冻结时机**：✅ v0.1 先 EXPERIMENTAL；冻结门 = golden 通过 + 确定性重放证据（同版本 core + 同 graph + 同输入 → 逐样本一致）。
4. **golden 曲目**：✅ `demo/input/example.mp3`（已核实存在，与 data factory 历史证据同源可比）。
5. **分支**：✅ 续作 `codex/professional-finishing-layer-20260920`；前置动作 = apps/web 未提交工作已收口为独立 WIP commit `7fdb1ee2`（产品定义 CLI-first 后 UI 线优先级下降，parked）。

### 5.2 原始决策问题（存档）

1. **模块归属**：新包 `moodify.mix_graph` 放 `moodify-core-package`（推荐，One Core）——确认？
2. **CLI 入口**：新子命令组 `moodify finishing *`（推荐，语义清晰）还是扩展现有 `moodify process`？
3. **schema 冻结时机**：v0.1 先 EXPERIMENTAL，跑通 golden 后再冻结为 v1 契约（推荐）？
4. **golden 曲目选择**：从现有 demo/input 与 data factory pilot 曲目中选 1 条（推荐 `example.mp3` 同源素材）？
5. **分支**：Mix Graph v0.1 开在本分支续作，还是另开 `codex/mix-graph-v01-*`（推荐续作本分支，Canon 依据就在此）？

## 6. 风险与事实边界

- pedalboard 在 Windows 本机的可用性未在本包验证（历史上 data factory 在 Linux 云端跑）；如本机不可用，provider 测试标记 skip + 云端节点跑通后补证据，不静默降级。
- `engine/` → `core/` 命名迁移是另一条已立待办（v1.2 changelog），本包不掺入。
- 本提案所有 TARGET 表述不得在任何对外材料写成已实现。
