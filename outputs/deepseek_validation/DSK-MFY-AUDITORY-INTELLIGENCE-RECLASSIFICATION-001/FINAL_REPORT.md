# DSK-MFY-AUDITORY-INTELLIGENCE-RECLASSIFICATION-001｜Final Codex Response

## 1. Implementation Verdict

**COMPLETED** — golden case（双候选 + 学习记录 + 受控导出）与受控数据集导出实际运行成功。

## 2. Repository Discovery

- 仓库布局：`moodify-core-package/src/moodify/`（49 模块 + auditory + learning 域）
- CLI：cli.py（旧 argparse）+ cli_v2（handlers dict）
- 生命周期：app/production_control.py（CaseState 状态机，保持权威）
- 处理引擎：processing/、v01_*、orchestration、adapters
- 分析：v01_analyzer、features、perception、auditory/*（AS-001 已交付）
- FFmpeg 包装：capability_registry/adapters
- 证据：app/evidence.py + auditory/manifests.py
- 数据库/持久化：文件（case.json 原子写）+ DuckDB（bridge）

## 3. Capability Inventory

`docs/auditory_intelligence/current_capability_inventory.{md,json}` — 50 能力，
分类：INTERVENTION 16 / SHARED 15 / JUDGMENT 7 / LEGACY_UNKNOWN 5 /
OBSERVATION 3 / REPRESENTATION 2 / VERIFICATION 1 / LEARNING 1。
LEGACY_UNKNOWN（knowledge/memory/llm/icc/system_depth）显式标注不确定。

## 4. Architecture Decision

`docs/adr/ADR-MFY-001-auditory-intelligence-reclassification.md` —
Moodify 核心 = 观察/表示/判断/验证/学习；处理 = 干预仪器；Audacity = 外部
工作台；技术成功 ≠ 艺术批准；学习记录提交前不算学习完成。

## 5. Domain Boundaries Added

- `moodify/learning/`：models（AuditoryObservation/InterventionRecord/
  HumanListeningEvaluation/LearningRecord/RightsMetadata/PairwisePreference/
  CandidateOutcome）、eligibility、exports、store、service、errors
- `moodify/auditory/`：已含观察/验证（AS-001），新增 inventory

## 6. Existing Processing Reclassification

processing/v01_*/craft/calibration/optimizer/physics/conservation/transcription/
score_engine/orchestration/adapters/services → INTERVENTION（原位保留并文档化
为干预实验室）。无删除、无批量重命名。

## 7. Compatibility Strategy

- 既有公共接口不变；auditory/learning 纯增量；
- cli_v2 只加子命令；cli.py 路由白名单扩展（learning/architecture）；
- 无弃用警告；全部迁移记录于 migration_map.md。

## 8. Domain Models and Schemas

学习域 4 个核心模型 + 权利元数据 + 资格状态 + 偏好/结果，schema_version 1.0，
全部 JSON 往返 + 原子写 + 哈希。

## 9. Case Lifecycle Integration

学习状态（NOT_STARTED→CAPTURED→REVIEW_PENDING→COMMITTED/EXCLUDED）为
**正交记录**（09_learning/），未改动 ProductionCase 状态机。COMPLETED +
EXCLUDED 合法且原因显式。

## 10. Learning Record Workflow

build（证据缺失失败关闭）→ review（权利+资格）→ commit（ELIGIBLE→COMMITTED，
其他→EXCLUDED）。偏好/结果 JSONL 追加。

## 11. Rights and Dataset Eligibility

资格默认 UNKNOWN/PENDING_REVIEW，绝不 ELIGIBLE；任一授权显式否定→INELIGIBLE；
导出只含 ELIGIBLE，其余报告但排除；manifest 哈希校验；确定性（无导出时间戳）。

## 12. CLI Commands

```bash
case observations add / intervention register / listening evaluate
case learning build|review|commit
learning dataset export --dataset-id --project-dir --output
architecture inventory --format md|json
```

成功码：AUDITORY_OBSERVATION_RECORDED / INTERVENTION_RECORDED /
HUMAN_LISTENING_EVALUATION_RECORDED / LEARNING_RECORD_BUILT /
LEARNING_RECORD_COMMITTED / LEARNING_RECORD_EXCLUDED。

## 13. Golden Case

`outputs/auditory_golden_learning/`（可复现：`python -m moodify.learning.run_learning_golden`）：
源 → before 扫描 → 观察 → 计划 → 候选 A（presence 提升，ACCEPTED）+
候选 B（过度限幅，OVERPROCESSED/REJECTED）→ 干预记录 → after 扫描 →
对比 → 人耳评估（A 优先）→ 成对偏好 → 学习记录 BUILT → REVIEWED（ELIGIBLE）
→ **COMMITTED** → **DATASET_EXPORT included=1** → manifest 校验通过。

## 14. Tests Executed

- tests/learning/：21 passed（模型 schema/资格默认/权利/工作流/提交幂等/
  导出过滤/确定性/manifest 校验）
- tests/auditory/：23 passed（AS-001 回归）
- tests/cli_v2/：19 passed（兼容回归）
- 合计 63 passed，无失败。

## 15. Evidence Paths

- `outputs/auditory_golden_learning/cases/MFY-CASE-LEARN-001/`
  （01_before_scan、02_observations、04_interventions、05_comparison/<cid>、
  06_after_scans、08_listening、09_learning）
- `outputs/auditory_golden_learning/exports/MFY-AUDITORY-DATASET-001/`
- `learning_golden_summary.json`

## 16. Files Changed

23 files, +3083 行（commit 9e622a8）：moodify/learning 9 模块、
auditory/inventory、cli.py、cli_v2/main.py、tests/learning 2 文件、
docs/adr 1、docs/auditory_intelligence 8。

## 17. Legacy Debt

- LEGACY_UNKNOWN 5 模块（knowledge/memory/llm/icc/system_depth）待人工复核；
- cli.py 旧 argparse 与 cli_v2 双入口并存（存量）；
- cli_v2 分号风格 E702 未清理（存量，避免大 diff）；
- moodify_runtime/learning_store.py、learning_surface.py 为未跟踪遗留文件
  （非本任务产出，未触碰）。

## 18. Known Limitations

- 人耳评估在 golden case 中为模拟记录（真实听音需人工执行）；
- 资格计算规则为初版（训练授权字段 4 项 + 审查字段），复杂权利场景需扩展；
- 导出为 JSON 记录包（音频文件由外部内容寻址存储负责，未复制大文件）；
- 学习记录未接 DuckDB bridge（当前为文件存储）。

## 19. Remaining Risks

- LEGACY_UNKNOWN 模块的真实职责未核（可能含被遗忘的能力）；
- 训练授权字段的语义（YES/NO/UNKNOWN）需要法务确认；
- 多 case 导出未做并发锁（当前单线程串行）。

## 20. Final Status

**COMPLETED** — 20 项 Definition of Done 全部满足：能力清点、ADR、
领域边界、处理重分类、兼容性保持、四模型、资格安全默认、学习记录
可建/可提交/可排除、受控导出、接受+拒绝候选保留、既有测试绿、新测试绿、
golden case 成功、文档完整、无虚假训练宣称、源未覆盖、产物可哈希、
限制与债务列出、代码/测试/文档/证据一致。
