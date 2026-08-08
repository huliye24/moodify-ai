# DSK-MFY-DATA-ASSET-013｜Codex 独立验收矩阵

| ID | 优先级 | 验收项 | 失败判定 |
|---|---|---|---|
| D0-01 | P0 | 012 HANDOFF 可审计，合同先于编码 | HOLD |
| D0-02 | P0 | 四层数据状态隔离且 fail-closed | HOLD |
| D0-03 | P0 | 权利按用途明确，训练权不被推断 | HOLD |
| D0-04 | P0 | 隐私、保留、删除和撤回合同完整 | HOLD |
| D1-01 | P0 | catalog 可追溯到源哈希、版本和 lineage | HOLD |
| D1-02 | P0 | 未复制受限媒体、歌词或客户敏感正文 | HOLD |
| D1-03 | P1 | 构建确定、增量，重复和 quarantine 可解释 | REWORK |
| D2-01 | P0 | 晋升只产生 proposal，不自动批准 | HOLD |
| D2-02 | P0 | Approved Training 要求显式人工批准与权利证据 | HOLD |
| D2-03 | P0 | work/creator/project/近重复无跨 split 泄漏 | HOLD |
| D2-04 | P1 | scorecard 分开报告规模、质量、权利与可学习性 | REWORK |
| D3-01 | P0 | 撤回可传播到直接/派生资产和数据集快照 | HOLD |
| D3-02 | P0 | 源数据、历史记录和生产数据库哈希未变化 | HOLD |
| D3-03 | P1 | 双构建、失败注入、CLI 和测试完整 | REWORK |
| D3-04 | P1 | App 数据飞轮只形成需求，不越界开发 | REWORK |
| D3-05 | P0 | 无训练完成、商业估值或模型优势虚假声明 | HOLD |

Codex 将独立注入伪训练授权、rights-pending、过期/撤回许可、重复/近重复、跨 work/creator/project 泄漏、伪人工批准、删除请求、正文泄漏、路径逃逸、顺序扰动和生产写入尝试。

