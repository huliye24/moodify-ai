# ASSET_AUDIT_BEFORE — 资产审计前状态

任务：DSK-RJWC-ASSET-REGISTRY-001
日期：2026-08-09

## 仓库范围（Phase 0 发现）

| 根 | 内容 | 资产密度 |
|---|---|---|
| `apps/android/` | Moodify Android App（Kotlin + Compose） | 高（MFY-SFT-0001） |
| `moodify-core-package/` | 核心引擎（auditory/evaluation/contracts/access/api/cli/learning） | 高（MFY-SYS/MDL/KNW/REP/DATA） |
| `docs/` | canonical 架构/契约/审计/实验文档 | 中（KNOWLEDGE） |
| `schemas/canonical/` | 契约 JSON Schema | 中（REPRESENTATION） |
| `scripts/`、`tools/` | 部署/扫描/面板工具 | 中（SOFTWARE/TOOLING） |
| `artifacts/` | 迁移/提取证据（pr15/reconstitution/mfy_mig） | 中（历史证据） |
| `outputs/` | 音频案例/黄金语料/账本 | 高（DATA，含版权未核样本） |
| `treatment_records/` | 人工治疗记录 | 中（HUMAN_LABEL 数据） |
| `moodify_runtime/` | 运行时代码（PR #15 资产矿） | 低（历史/重复） |

## 审计前事实

- 无资产注册表；资产分散在代码库各处，缺统一 ID/所有权/证据索引
- 所有权：仓库代码为 RJWC/Moodify 自研；但品牌/域名/样本语料/云资源状态未登记
- 第三方依赖散落在 requirements.txt/pyproject/Android gradle，无集中清单
- 历史遗留（PR #15 提取前系统、CWC 已删功能、night 打包）未分类归档

## 决策

- 登记以知识驱动为主（17 条），扫描脚本（candidates.json 77 组）作位置验证与候选发现
- 非资产（运维能力/第三方服务/实验/依赖/废弃项）显式分离于 non_assets.index.json
