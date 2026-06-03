# NEM-MT-005｜AI 接手说明

你是接手 Moodify MT-005 的工程执行 Agent。

## 执行原则

1. 不要重新定义整个 Moodify 项目。
2. 本节点只处理“样本资产库 / 数据资产 / 真实 AI 音乐样本体系”。
3. 不要先大量堆文件，先建立 sample_id、registry、metadata schema 和 storage layout。
4. 任何样本必须有来源、权限状态、存储路径和状态字段。
5. 权限不确定的样本只能标记为 `uncertain` 或 `internal_research_only`，不得标记为可公开或可商用。
6. Runtime 输出必须写入 processing_lineage。
7. MRS 输出必须写入 mrs_history。
8. preset 使用记录必须写入 preset_usage_history。
9. 不得帮助规避平台识别、版权检测、指纹检测或隐藏来源。
10. 只允许围绕合法的研究、测试、质量评估和数据资产管理进行设计。

## AI 阅读顺序

1. `00_PACKAGE_MANIFEST.json`
2. `00_NODE_STATUS.md`
3. `rules/AI_Execution_Rules.md`
4. `rules/Sample_Asset_Rules.md`
5. `nem/NEM-MT-005_Sample_Asset_Library.md`
6. 当前 Gate 文件
7. 当前 AEP 文件
8. `templates/` 中对应模板

## 当前下一步

读取 `aep/AEP-MT005-001_Sample_ID_System.md`，建立第一版 sample_id 规则和样本身份系统。
