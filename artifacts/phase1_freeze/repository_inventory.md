# Moodify 仓库清单 — MFY-PHASE1-FREEZE-001 Step A

**审计日期**: 2026-08-08
**审计范围**: E:\moodify 全仓库（monorepo：core-package + android + runtime + research assets）

## 1. 应用表面 (App Surfaces)

| 表面 | 位置 | 状态 |
|------|------|------|
| Android 客户端 | `apps/android/`（Kotlin + Compose） | 活跃。4-tab 底部导航：首页/听觉检测/案例/我的（commit 9d72799 冻结） |
| 主导航 tab | `apps/android/app/src/main/java/com/moodify/app/ui/MoodifyApp.kt` | nav_home / nav_process / nav_cases / nav_profile |
| 全屏覆盖层 | HomeScreen / ProcessingHubScreen / WorksScreen / ProfileScreen 等 12 个 Screen | 活跃 |
| 死屏（不可达） | CreatorCenterScreen.kt / CopyrightCenterScreen.kt / CollaborationHubScreen.kt | 存在但无 import 引用，Phase II 残留 |
| 发布流程 | PublishWorkScreen.kt | **已从 WorkDetail 接线**，Phase II 边缘，建议冻结 |
| 社交通知 | NotificationCenterScreen.kt | 已接线，建议复核 |

## 2. 后端服务 (Backend Services)

| 服务 | 位置 | 状态 |
|------|------|------|
| REST API (FastAPI) | `moodify-core-package/src/moodify/api/main.py` | 活跃。4 router：root + v1(mobile) + workspace_projects + lyric_align + pairwise_judge + calibration + sessions |
| 运行时 | `moodify_runtime/`（~80 模块：cli/runner/cloud_worker/mrs_engine/operator_console/queue/scheduler/studio/xclp_gate） | 活跃 Python 运行时 |
| 部署表面 | `deploy/`（Dockerfile / deploy.sh / backup.sh / service / nginx conf） | 活跃 |
| 桥接 | `moodify-bridge/`（local-first 研究-生产桥，Python 包 + demo cases） | Phase I 工具 |

## 3. CLI / 流水线 (CLI / Pipelines)

| 项 | 位置 | 状态 |
|----|------|------|
| CLI v1 | `src/moodify/cli.py`（analyze/process/presets/serve/legacy-*） | 兼容层，v2 命令转发至 cli_v2 |
| **CLI v2（规范）** | `src/moodify/cli_v2/main.py`（SCHEMA_VERSION 1.0.0，JSON-first，原子写） | 活跃。`python -m moodify case create/analyze/approve/execute/verify/package/scan/...` |
| v2 子命令 | version/capabilities/project/asset/plan/run/case/learning/architecture | 全覆盖 |
| 旧六阶段流水线 | `src/moodify/orchestration/`（WorkflowOrchestrator） | legacy，api/main.py 明确"有意不用" |
| 状态转移 | `src/moodify/orchestration/state_transfer.py` | legacy |

## 4. WSE / MSE / PPE 模块映射

### WSE（什么发生在声音里）
- `src/moodify/auditory/`：scan_audio（频谱/时间线/metrics.json/evidence 目录）、compare_scans、manifests（hash 校验）
- `src/moodify/features/`：f0.py / chroma.py / perceptual.py
- `src/moodify/perception/`：心理声学掩蔽（AEP-ACU-007）
- `src/moodify/physics/`：核心假设可复现实验
- `src/moodify/adapters/auditory/ocean_listen/`：Ocean Listen 桥（configs/ocean_adapter.json，enabled:false）
- 数学基座：audio_io/bands/fingerprint/conservation/icc/uncertainty/mrs_robust

### MSE（音乐结构是什么）
- `src/moodify/lyric_align/`：歌词时间对齐（heuristic + whisperx）
- `src/moodify/transcription_pipeline/`：音频转 MIDI v0.2
- `src/moodify/score_engine/`：MoodifyScore 内部乐谱模型 + MIDI/MusicXML 适配

### PPE（如何可靠产出）
- `src/moodify/capability_registry/`：execution（批准信封 SHA-256）/ validation（验证门）/ knowledge（版本化策略回馈）
- `src/moodify/evaluation/`：SPEC-013 + pairwise judge（configs/pairwise_policy_v1.yaml）
- `src/moodify/app/evidence.py`：EvidenceBundle 聚合器
- `src/moodify/app/production_control.py`：ProductionCase 脊柱（见 §5）

## 5. 规范控制脊柱 (Canonical Control Spine) — 完整存在

`src/moodify/app/production_control.py`：
- `CaseState` 16 状态：CREATED→SOURCE_REGISTERED→SPECIFIED→ANALYZING→ANALYZED→PLANNED→TECHNICALLY_VALIDATED→AWAITING_ARTISTIC_APPROVAL→APPROVED→EXECUTING→EXECUTED→VERIFYING→VERIFIED→PACKAGED→COMPLETED
- `ProductionCase`：register_source/specify/analyze/set_plan/run_technical_gate/approve/check_approval_gate
- `ApprovedExecutionEnvelope`：不可变授权，引擎只收 envelope
- `ProductionControlService`：execute/verify/package + REQUIRED_EVIDENCE_FILES 校验
- 持久化：`ProductionCaseStore`，文件系统 JSON（`<project>/cases/<case_id>/case.json`，原子写 + fsync）
- 证据包：`evidence/` 11 个必需文件 + evidence_manifest.json（全链 hash 交叉校验）

## 6. 判断层 (Judgment Layer)

| 组件 | 位置 | 状态 |
|------|------|------|
| 单候选听觉判断 | `auditory/judgment.py`（Judgment / RiskFlag）+ auditory/models.py | 活跃 |
| 双候选判断 | `evaluation/pairwise/`（run_pairwise_judge / DecisionPolicy / record_human_decision） | 活跃（2e26fa4） |
| 旧评测 | `evaluation/judges.py`（LLMJudge/AcousticJudge/ConsensusJudge） | legacy，保留 |
| 五维诊断 | `diagnosis/`（DefectClassifier/HealthScorer/QualityGate） | 活跃（旧引擎） |
| 证据链 | `app/evidence.py` + case 目录 `01_before_scan/03_processing/candidates/04_after_scan/05_comparison/05_lyric_align/06_pairwise` | 活跃 |

## 7. 学习循环 (Learning Loop)

- `learning/models.py`：AuditoryObservation / InterventionRecord / HumanListeningEvaluation / RightsMetadata / PairwisePreference / CandidateOutcome / LearningRecord
- `learning/service.py`：build → review（**HumanReview 职能落地形态**：RightsMetadata 权利审查 + review_status）+ commit；add_preference_and_outcome
- `learning/store.py`：CaseLearningStore
- `learning/eligibility.py`：默认非合格
- `learning/exports.py`：受控数据集导出
- 安全规则已内建：单案例反馈不自动改全局阈值（记录先于提交，提交需 review）

## 8. CWC / Phase II 表面 (grep 全仓库)

- `apps/`：95 处命中 / 41 文件，其中 ~31 个在 `app/build/`（GENERATED 中间产物）；手写源码 ~10 处（strings.xml 死屏字符串、CollaborationHubScreen、SupportScreens、NotificationCenterScreen、i18n 测试 json）
- `moodify-core-package/src/`：**0 处真实命中**（1 处 GOLDEN_CASE_SCRIPT.md 误报："不依赖任何版权音乐"）
- 已删除（git 历史可恢复）：CwcIntro/Auth/Center/Gift Screen、CwcRepository、CreatorPass、`moodify://cwc/` 深链、首启登录门
- `docs/DEEPSEEK_TASK_CWC_CREATOR_PASS.md`：**Phase II CWC 完整规格文档，未归档**

## 9. 生成文件与死代码

| 类别 | 位置 |
|------|------|
| Android 构建产物 | `apps/android/app/build/`（GENERATED） |
| Python 缓存 | 各 `__pycache__/`、`*.pyc`（GENERATED） |
| Electron 产物 | `moodify-pulse/dist/`、`dist-electron/`、`node_modules/`（LEGACY 产物） |
| 早期单体残留 | `moodify-app/`、`moodify-system/`（LEGACY，嵌套空壳） |
| 内容资产 | `07Music/`、`pre-music/`（MP3/分轨素材）、`RJWC_VideoPack_System/`（已交付） |
| 研究资产 | `phys-lab/`、`night/`、`listening_test/`、`experiments/`、`science/`、`scratch/`、`calibration_reports/`、`inspector_reports/`（保留） |
| 开发辅助 | `scripts/demo_*.bat`、`scripts/simulate_deepseek_outputs.py`（可归档） |
| 工程记录重复 | `docs/echain/`（17 份）+ `e_chain/`（2 份重复） |

## 10. 测试 (Tests)

- 位置：`moodify-core-package/tests/`，**85 个 test_*.py 文件**
- 布局：顶层 ~25 + v2/(18) + lyric_align/(11) + capability_registry/(6) + ocean_listen/(6) + evaluation/(5) + api/(2) + architecture/(2) + auditory/(2) + cli_v2/(2) + learning/(2) + score_engine/(4) + orchestration/(1) + baseline/(1)
- marker：`v01`（legacy v0.1.0 主线）、`legacy`（旧系统兼容，已定义未用）、`experimental`（未来/研究，已定义未用）
- CLI v2 闭环测试：`tests/cli_v2/test_cli_v2_case_commands.py`（16 用例）+ `test_cli_v2_closed_loop.py`（10 用例，subprocess 真实 CLI）

## 11. 规范运行时路径 (Canonical Runtime Paths)

1. CLI v2：`python -m moodify case create → asset.import → case.analyze → case.approve → case.execute → case.verify → case.package`
2. API：POST /workspace/projects → /v1/uploads → /operator/jobs/{id}/attach-run
3. 控制脊柱：ProductionCase（唯一权威生产生命周期）
4. 证据：case 目录阶段化 + evidence/ 包 + evidence_manifest.json

## 12. 重复/失控执行路径 (Duplicated / Uncontrolled Paths)

| 路径 | 说明 | 处置建议 |
|------|------|---------|
| `cli.py` legacy-analyze / legacy-process | v0.1.0 兼容 | 保留（v01 测试覆盖） |
| `orchestration/` WorkflowOrchestrator | 旧六阶段流水线，API 已注释不用 | 保留（legacy） |
| `evaluation/judges.py` | 旧评测器 | 保留（legacy） |
| `diagnosis/` | 五维诊断（被 v2 判断层部分替代） | 保留（legacy，有真实产出） |
| `run.execute` / `run.verify` CLI | 需 `--allow-uncontrolled` | 保留（显式非默认） |
