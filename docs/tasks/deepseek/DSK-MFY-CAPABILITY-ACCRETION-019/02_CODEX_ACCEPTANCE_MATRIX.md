# DSK-MFY-CAPABILITY-ACCRETION-019｜Codex 独立验收矩阵

| ID | 优先级 | 验收项 | 失败判定 |
|---|---|---|---|
| Q0-01 | P0 | 018 HANDOFF 可读且适配器可用 | HOLD |
| Q0-02 | P0 | Envelope/Record 合同编码前冻结 | HOLD |
| Q1-01 | P0 | 无 envelope 不得执行（gateway 强制） | HOLD |
| Q1-02 | P0 | envelope 不可变：修改后签名失效/拒绝 | HOLD |
| Q1-03 | P0 | 输入哈希锁定，源文件执行期间只读 | HOLD |
| Q2-01 | P0 | 执行只经 ExecutionGateway，无旁路 | HOLD |
| Q2-02 | P0 | 未授权直接调用 adapter 可被拒绝/识别 | HOLD |
| Q2-03 | P0 | 失败 ExecutionRecord 证据完整 | HOLD |
| Q2-04 | P1 | 状态机转换有测试 | REWORK |
| Q3-01 | P0 | provider 只拿到授权输入/参数/输出白名单 | HOLD |
| Q3-02 | P0 | 不修改 008/009 实现；不强行接入 cli_v2 | HOLD |
| Q3-03 | P0 | 无 MATLAB、网络下载、许可证混淆 | HOLD |
| Q3-04 | P1 | 合成 fixture 端到端 + 双运行 | REWORK |
| Q3-05 | P1 | 测试、CLI smoke、Ruff、文档通过 | REWORK |
| Q3-06 | P1 | 架构文档包含与 cli_v2 case 的对接顺序 | REWORK |

Codex 将独立执行：篡改 envelope（改参数/输出路径/输入哈希）、无签名执行、
绕过 gateway 直接调 adapter、失败注入、输出越界目录、旧 CLI 回归、Ruff。
