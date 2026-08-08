# Current-to-Target Module Map

本文件建立逻辑边界，不授权一次性搬迁。

| 当前路径 | 目标边界 | 分类 | 迁移策略 |
|---|---|---|---|
| `moodify-core-package/src/moodify/audio_io.py` | ingestion | production candidate | 保留入口，增加 SourceAsset adapter |
| `v01_analyzer.py`, `reality_metrics.py`, `features/`, `perception/` | wse | partial/research mixed | 建 metric registry；逐项标 backend/confidence |
| `processing/`, `v01_presets.py` | treatments | partial production | 不重写 DSP；阶段参数写 ledger |
| `optimizer/`, legacy workflow search | candidate_generation | experimental | 先封装 Experiment/Candidate，不迁移 |
| `evaluation/`, `services/judge.py`, `version_compare.py` | evaluation/quality_gates | partial | 适配 Evaluation/Decision schema |
| `services/archive.py`, `v01_delivery.py` | assets/reporting | partial | 输出 DeliverableManifest |
| `storage/workspace_store.py` | ppe | partial production | 与 case ID 建映射，不替换现存 Workspace ID |
| `moodify_runtime/runner.py`, `supervisor.py`, `cli.py` | ppe/cli | partial production | job 注入 case/pipeline/rule IDs |
| `operator_api.py`, console | cli/internal operations | partial | 保持旧路由；新增兼容端点需测试 |
| `report.py`, comparison/report modules | reporting/evaluation | partial | 只读统一 schema |
| `craft_*`, `learning_*`, `data_loop_runner.py` | rules/ppe | experimental | 禁止自动 production promotion |
| `moodify-bridge/schemas.py`, `store.py` | schemas/ppe | v0.4 contract partial | 作为主 schema 孵化点 |
| `moodify-bridge/metrics.py` | wse | partial | 与 core analyzer 做交叉验证 |
| `docs/experiments`, `experiments`, `science` | experiments/{wse,mse,treatments,evaluation} | research/history | 不移动；新实验按目标目录新增 |

目标目录按需创建：`src/moodify/{ingestion,wse,mse,ppe,treatments,candidate_generation,evaluation,quality_gates,assets,schemas,reporting,rules,cli,common}`。在核心包迁移前，不在仓库根再造一套假实现。测试目标分 `unit/integration/regression/fixtures`，现有测试路径保持可运行。

