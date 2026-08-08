# DSK-MFY-CAPABILITY-ACCRETION-020｜Codex 独立验收矩阵

| ID | 优先级 | 验收项 | 失败判定 |
|---|---|---|---|
| Q0-01 | P0 | 019 HANDOFF 可读且 gateway 可用 | HOLD |
| Q0-02 | P0 | 验证规则/候选合同编码前冻结 | HOLD |
| Q1-01 | P0 | error 级验证失败即 rejected，不可绕过 | HOLD |
| Q1-02 | P0 | 失败候选保留 + 结构化理由，不隐藏 | HOLD |
| Q1-03 | P0 | 拒绝理由含 rule_id/测量值/期望值 | HOLD |
| Q1-04 | P0 | 每条 ValidationRule 有 historical_source（地质记录），无来源标记 unproven | HOLD |
| Q1-05 | P1 | 通用规则库至少 3 条规则携带真实来历（源自 009/008 失败台账） | REWORK |
| Q2-01 | P0 | 回退仅走 registry 声明路径 | HOLD |
| Q2-02 | P0 | 每候选独立 envelope（019 不变性） | HOLD |
| Q2-03 | P0 | 验证分数双运行一致 | HOLD |
| Q2-04 | P1 | 规则库覆盖 media/notation/audio 域 | REWORK |
| Q3-01 | P0 | 不修改 008/009/017-019 实现 | HOLD |
| Q3-02 | P0 | 无 MATLAB、网络下载、许可证混淆 | HOLD |
| Q3-03 | P1 | 合成 fixture 端到端（多 provider/参数变体） | REWORK |
| Q3-04 | P1 | 测试、CLI smoke、Ruff、文档通过 | REWORK |
| Q3-05 | P1 | 人工审查挂点（ArtisticReviewHook）有明确说明 | REWORK |

Codex 将独立执行：伪造输出（空文件/NaN/错误采样率）、验证绕过尝试、
候选排序稳定性、回退触发、拒绝理由完整性、旧 CLI 回归、Ruff。
