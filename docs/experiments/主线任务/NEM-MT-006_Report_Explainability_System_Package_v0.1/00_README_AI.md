# AI 接手说明｜NEM-MT-006

你正在接手 Moodify 的 报告与可解释性系统 节点。

## 执行原则

1. 不要重新设计整个 Moodify。
2. 先读取 `00_PACKAGE_MANIFEST.json`。
3. 再读取 `00_NODE_STATUS.md`。
4. 再读取 `rules/AI_Execution_Rules.md`。
5. 再读取 `nem/NEM-MT-006_Report_Explainability_System.md`。
6. 每次只推进一个 AEP。
7. 执行后必须更新报告、日志、Decision Log 和 Node Status。
8. 报告系统必须可追踪到 sample_id、preset_id、run_id、mrs_version、report_id。

## 当前建议任务

执行：`aep/AEP-MT006-001_Report_Information_Architecture.md`

目标：定义 Moodify 报告系统的字段结构、三类报告层级、解释模块、图表模块和导出格式。
