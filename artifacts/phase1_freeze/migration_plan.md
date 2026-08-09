# Phase I 冻结迁移计划（MFY-PHASE1-FREEZE-001）

**日期**: 2026-08-08
**原则**（09_MIGRATION_RULES）：isolate before delete; flag before rewrite; map before move; preserve provenance。

## 1. Phase II 表面处置决定

| 表面 | 处置 | 理由 |
|------|------|------|
| Android CreatorCenterScreen / CopyrightCenterScreen / CollaborationHubScreen | KEEP_DISABLED + @Deprecated 标注 | 无 import 不可达；代码保留供 Phase II 恢复 |
| Android PublishWorkScreen | KEEP_DISABLED + @Deprecated + **入口移除** | WorkDetail 发布按钮已摘除；发布属 Phase II |
| Android NotificationCenterScreen | KEEP_DISABLED + @Deprecated + **入口移除** | 内容全部为社交类通知；Home 铃铛已摘除 |
| docs/DEEPSEEK_TASK_CWC_CREATOR_PASS.md | ARCHIVE（原位 FROZEN 标记） | 无 archived/ 目录惯例；避免破坏引用 |
| 早期单体残留（moodify-app/moodify-system） | 保留（LEGACY） | 无删除必要，非运行时 |
| 研究资产（phys-lab/night/listening_test 等） | 保留（LEGACY） | 历史研究记录不可删 |
| Android build 产物（app/build/） | 保留（GENERATED） | 构建中间产物，git 未跟踪 |

## 2. 判断层规范化（Step G）

- `RiskFlag` 扩展契约字段（label/observed_value/unit/reference_basis/confidence/classification/rule_or_model_version/evidence_refs）——向后兼容（全可选默认值）
- `evaluate_risk_flags` 返回前统一补全（_enrich_risk_flag）
- BLOCKING 判断强制携带 evidence_refs；无证据的 BLOCKING 在报告中标记 unresolved → PARTIAL

## 3. 报告（Step H）

- `auditory/reports.py` 新增 `build_auditory_report` → `auditory_report.json`（机器可读，06_AUDITORY_REPORT_SPEC）

## 4. 明确不做

- 不删除任何 Phase II 代码文件（保留可恢复性）
- 不改动 severity 语义（INFO/WARNING/BLOCKING 保留，映射关系文档化）
- 不引入新依赖、不改 CLI v2 契约、不动控制脊柱
- 不建 config/ 新目录（使用既有 configs/ 惯例）

## 5. 风险与回滚

- 风险：RiskFlag 字段扩展影响序列化消费者（comparison_report.json）——字段全可选，to_dict 只增不减，向后兼容
- 回滚：git revert 单 commit 即可（改动集中于 3 个 py 文件 + 1 个 yaml + 5 个 kt 文件）
