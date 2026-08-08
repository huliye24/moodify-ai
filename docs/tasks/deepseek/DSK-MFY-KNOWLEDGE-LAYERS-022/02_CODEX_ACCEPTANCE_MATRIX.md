# DSK-MFY-KNOWLEDGE-LAYERS-022｜Codex 独立验收矩阵

| ID | 优先级 | 验收项 | 失败判定 |
|---|---|---|---|
| Q0-01 | P0 | 注册表 schema 编码前冻结（PR-0xx/EX-0xx 字段） | HOLD |
| Q0-02 | P0 | 素材盘点真实（数量/来源可核对，无编造） | HOLD |
| Q1-01 | P0 | 每条原理条目有可核对来源（文档/章节/ADR） | HOLD |
| Q1-02 | P0 | 每条经验条目有失败事实+根因+边界+防复发机制 | HOLD |
| Q1-03 | P0 | 经验防复发机制指向真实文件/测试/流程 | HOLD |
| Q2-01 | P0 | 008/009 失败台账至少 3 条真实失败入注册表 | HOLD |
| Q2-02 | P0 | 编号连续无重复；Markdown 结构一致 | HOLD |
| Q2-03 | P1 | 原理与经验关联（PR↔EX）至少 3 组 | REWORK |
| Q3-01 | P0 | 不修改任何代码/既有文档（只新建三文件） | HOLD |
| Q3-02 | P0 | 无 MATLAB、网络下载、许可证混淆 | HOLD |
| Q3-03 | P1 | THREE_LAYER_KNOWLEDGE.md 追溯约定完整可执行 | REWORK |
| Q3-04 | P1 | HANDOFF 引用本次 PR/EX 条目（示范约定） | REWORK |
| Q3-05 | P1 | PROGRESS/VALIDATION/FAILURE_LEDGER 齐全 | REWORK |

Codex 将独立执行：随机抽取 PR/EX 条目核对来源、经验防复发机制指向性、
编号连续性、与 008/009 失败台账交叉验证、确认无代码/既有文档被修改。
