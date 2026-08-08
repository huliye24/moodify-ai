# DSK-MFY-DECISION-INTELLIGENCE-011｜Codex独立验收矩阵

| ID | 优先级 | 验收项 | 失败判定 |
|---|---|---|---|
| D0-01 | P0 | 010 HANDOFF存在；合同先于编码 | HOLD |
| D0-02 | P0 | 权利、隐私、删除和模型主张边界冻结 | HOLD |
| D1-01 | P0 | episode六层分开且来源/哈希可追溯 | HOLD |
| D1-02 | P0 | Owner标签没有推断、代填或重写 | HOLD |
| D1-03 | P0 | 未评审/平局/不确定/缺失未混为负样本 | HOLD |
| D1-04 | P0 | 源记录只读，敏感媒体正文未复制 | HOLD |
| D1-05 | P1 | rejected ledger完整、双构建确定 | REWORK |
| D2-01 | P0 | work/creator/project无跨split泄漏 | HOLD |
| D2-02 | P0 | 无target leakage或评审后字段偷看 | HOLD |
| D2-03 | P0 | MRS/Gate未冒充人工偏好标签 | HOLD |
| D2-04 | P0 | 数据不足时输出DATA_NOT_READY | HOLD |
| D2-05 | P1 | CPU baseline、coverage/abstention/指标可复现 | REWORK |
| D3-01 | P0 | baseline未接生产、自动DSP或自动Final | HOLD |
| D3-02 | P0 | 未宣称自主智能、优势或生产就绪 | HOLD |
| D3-03 | P1 | 12类失败、dataset card、偏差/晋级报告完整 | REWORK |
| D3-04 | P1 | 测试、Ruff、Mypy、CLI smoke通过 | REWORK |

Codex将独立注入重复work、creator泄漏、标签缺失/冲突、伪Owner、哈希篡改、
媒体正文、target字段、顺序扰动、删除请求、少样本和生产接入尝试。

