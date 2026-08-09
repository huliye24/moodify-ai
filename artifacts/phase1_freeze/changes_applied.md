# Phase I 冻结变更记录（MFY-PHASE1-FREEZE-001）

**日期**: 2026-08-08

## 已应用变更

### 配置
- 新增 `moodify-core-package/configs/phase1_scope.yaml`：Phase I 策略配置（canonical loop、primary surfaces、phase1_core/secondary、phase2_frozen 完整清单、freeze_behavior、enforcement 落地机制、exit conditions）

### Android（Phase II 冻结）
- `ui/MoodifyApp.kt`：移除 publishOpen/notificationOpen 状态、BackHandler 分支、覆盖层分支、WorkDetail onPublish 回调、Home onOpenNotifications 回调；移除 2 个 import
- `ui/screens/WorkDetailScreen.kt`：移除 onPublish 参数与发布按钮
- `ui/screens/HomeScreen.kt`：移除 onOpenNotifications 参数与通知铃铛
- 5 个 Screen 加 `@Deprecated("PHASE2_FROZEN (MFY-PHASE1-FREEZE-001): ...")`：
  - CreatorCenterScreen.kt / CopyrightCenterScreen.kt / CollaborationHubScreen.kt（原本不可达）
  - PublishWorkScreen.kt（发布流程，入口移除）
  - NotificationCenterScreen.kt（社交通知，入口移除）

### 判断层（Step G 契约规范化）
- `src/moodify/auditory/models.py`：RiskFlag 新增契约字段（label/observed_value/unit/reference_basis/confidence/classification/rule_or_model_version/evidence_refs），to_dict 输出全字段
- `src/moodify/auditory/judgment.py`：新增 `_enrich_risk_flag`（classification 映射、unit 映射、reference_basis、rule_or_model_version、evidence_refs），evaluate_risk_flags 返回前统一补全；BLOCKING 强制证据引用

### 报告（Step H）
- `src/moodify/auditory/reports.py`：新增 `build_auditory_report` → 机器可读 `auditory_report.json`（header/summary/sections/findings/evidence_index/unresolved_evidence_findings）；BLOCKING 无证据 → overall_status=PARTIAL（失败语义）

### 文档
- `docs/architecture/phase1_scope.md`：产品身份、规范路径、主导航、冻结清单、核心承诺、退出门
- `docs/architecture/phase1_wse_mse_ppe_map.md`：三域映射 + 检查表
- `docs/DEEPSEEK_TASK_CWC_CREATOR_PASS.md`：文件头 PHASE2_FROZEN 标记（规格归档）

### 测试
- 新增 `tests/test_phase1_freeze.py`（11 用例）：scope config、freeze 清单、规则版本、契约字段、BLOCKING 证据强制、报告 PARTIAL 语义、证据索引解析、judge 不虚构、CLI v2 契约存在

### 审计交付物
- `artifacts/phase1_freeze/repository_inventory.md`
- `artifacts/phase1_freeze/phase_classification.csv`
- `artifacts/phase1_freeze/migration_plan.md`
- 本文件 + `validation_report.md`

## 未做（明确保留）

- Phase II 代码文件均未删除（KEEP_DISABLED + 标注）
- severity 语义未改（INFO/WARNING/BLOCKING；契约映射：INFO→LOW, WARNING→MEDIUM, BLOCKING→HIGH/CRITICAL）
- CLI v2 契约、控制脊柱、证据包机制未动
- 无新依赖

## 例外豁免

按 11_DO_NOT_BUILD_NOW 规定，本次无冻结功能兼容性修复需求，无例外记录。
