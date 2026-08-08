# DSK-MFY-IDENTITY-CORE-010｜Codex独立验收矩阵

| ID | 优先级 | 验收项 | 失败判定 |
|---|---|---|---|
| I0-01 | P0 | 009 HANDOFF存在且依赖边界明确 | HOLD |
| I0-02 | P0 | 编码前冻结身份/证据/Owner/可证伪合同 | HOLD |
| I0-03 | P0 | 实现事实、验证事实和产品主张严格分开 | HOLD |
| I1-01 | P0 | finding四态且每项引用有效证据 | HOLD |
| I1-02 | P0 | 缺失/冲突证据不产生虚假PRESERVED | HOLD |
| I1-03 | P0 | human_only未被启发式冒充机器理解 | HOLD |
| I1-04 | P0 | 无总分、排名、自动Final或自动批准 | HOLD |
| I1-05 | P1 | schema严格、确定、引用/哈希失败可见 | REWORK |
| I1-06 | P1 | 默认五中心和006/007兼容 | REWORK |
| I2-01 | P0 | 盲听映射评审前隔离且可事后审计 | HOLD |
| I2-02 | P0 | 未响度匹配不伪称公平盲听 | HOLD |
| I2-03 | P0 | Owner decision只由显式人工输入形成 | HOLD |
| I2-04 | P0 | CraftObservation默认NOT_PROMOTED | HOLD |
| I2-05 | P1 | 重复/篡改/无Owner决策稳定失败 | REWORK |
| I3-01 | P0 | claim边界未宣称独有性或优势已证明 | HOLD |
| I3-02 | P0 | source/candidate/只读哈希不变 | HOLD |
| I3-03 | P1 | 五类fixture、双运行、12类失败完整 | REWORK |
| I3-04 | P1 | Bridge全测、Ruff、Mypy、CLI smoke通过 | REWORK |
| I3-05 | P1 | HANDOFF可由第二执行者复现 | REWORK |

Codex将独立构造证据缺失/冲突/断链、human_only、哈希篡改、映射泄漏、未
响度匹配、无Owner、重复决策、自动Final、Craft晋级、默认表面泄漏和旧CLI
回归，并给出`ACCEPT / REWORK / HOLD`。

