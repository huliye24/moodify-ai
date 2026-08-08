# DSK-MFY-CAPABILITY-ACCRETION-018｜Codex 独立验收矩阵

| ID | 优先级 | 验收项 | 失败判定 |
|---|---|---|---|
| Q0-01 | P0 | 017 HANDOFF 可读且 Registry 可用 | HOLD |
| Q0-02 | P0 | Adapter Protocol/错误分类编码前冻结 | HOLD |
| Q1-01 | P0 | provider 名不出现在上层工作流/业务逻辑 | HOLD |
| Q1-02 | P0 | argv 数组调用，无 shell 注入面 | HOLD |
| Q1-03 | P0 | 缺失 provider 稳定 unavailable，无伪成功 | HOLD |
| Q2-01 | P0 | 不修改 009 musescore_backend / 008 实现 | HOLD |
| Q2-02 | P0 | Audacity GUI-only 声明 human_handoff，不伪称自动化 | HOLD |
| Q2-03 | P0 | 错误分类统一（六类） | HOLD |
| Q2-04 | P1 | 每个适配器存在/缺失两态都有测试 | REWORK |
| Q3-01 | P0 | 输出隔离：全新目录、拒绝覆盖/路径逃逸 | HOLD |
| Q3-02 | P0 | 没有 MATLAB、网络下载、许可证混淆 | HOLD |
| Q3-03 | P1 | 合成 fixture 端到端（每适配器至少一个） | REWORK |
| Q3-04 | P1 | 测试、CLI smoke、Ruff、文档通过 | REWORK |
| Q3-05 | P1 | 双运行 evidence 一致（非确定性字段注明） | REWORK |

Codex 将独立执行：伪 provider 路径、shell 注入参数、超时、非零退出码、
空输出目录、路径逃逸、错误翻译、Audacity 自动化声明、GPL/LGPL 归属、
旧 CLI 回归、Ruff。
