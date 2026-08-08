# DSK-MFY-PPE-HARDENING-005｜Codex 独立验收矩阵

本文件是 DeepSeek 的预知验收标准，也是 Codex 的最终检查表。DeepSeek 不得自行勾选“最终通过”。

| ID | 优先级 | 验收项 | 必须证据 | 失败判定 |
|---|---|---|---|---|
| AC-01 | P0 | 修改范围合规 | Git/file inventory 仅涉及允许路径 | HOLD |
| AC-02 | P0 | 只读资产不变 | before/after SHA-256 完全一致 | HOLD |
| AC-03 | P0 | 无批准不晋级 | 规则文件、approval 表和状态均不变 | REWORK/HOLD |
| AC-04 | P0 | 无部分晋级 | 缺失批准、错版本、非法转换、写入失败注入均原子失败 | HOLD |
| AC-05 | P0 | 阻断门不可抵消 | 任一 blocking FAIL 导致 FINAL_STATUS=FAIL | REWORK |
| AC-06 | P0 | 不伪造科学事实 | 无音频测量/候选/人工批准均为明确 WARN/缺失语义 | HOLD |
| AC-07 | P1 | 六闸门机器可读 | 严格 schema、固定 ID/状态、reason code、证据路径 | REWORK |
| AC-08 | P1 | 批准语义清楚 | 明确区分 approval_required 与 approval_present | REWORK |
| AC-09 | P1 | CLI 失败可理解 | 预期错误无 traceback、非零退出、稳定错误码 | REWORK |
| AC-10 | P1 | 单入口完整 | 一个命令生成声明的全部基线产物 | REWORK |
| AC-11 | P1 | 输出不可覆盖 | 非空输出目录默认拒绝，历史产物不变 | HOLD |
| AC-12 | P1 | 失败可追踪 | 失败 manifest/command result 保留步骤、错误和路径 | REWORK |
| AC-13 | P1 | 确定性 | 双全新目录规范化产物一致，易变字段有明确定义 | REWORK |
| AC-14 | P1 | 安全重试 | 失败后只允许新目录重试，旧失败现场保留 | REWORK |
| AC-15 | P1 | 报告引用完整 | manifest 中每个成功产物存在且哈希匹配 | REWORK |
| AC-16 | P1 | 回归完整 | bridge 全量测试、Ruff、Mypy 均通过 | REWORK |
| AC-17 | P2 | 环境显式 | Python/包/平台/后端写入 environment.json | REWORK |
| AC-18 | P2 | 继承成立 | README/HANDOFF 足以让第二执行者独立复现 | REWORK |
| AC-19 | P2 | 历史事实诚实 | 不修改 8 月 1 日报告，不宣称声音改善或生产批准 | HOLD |

## Codex 验收动作

DeepSeek 交接后，Codex 至少执行：

1. 读取 HANDOFF、完整 diff 和修改文件清单。
2. 独立运行 bridge 全量测试、Ruff、Mypy。
3. 在两个由 Codex 新建的全新目录重复 PPE 单入口。
4. 独立重放至少三项失败：哈希失配、无批准晋级、非空输出目录。
5. 查询 DuckDB，确认失败没有产生部分 approval/晋级状态。
6. 对 demo、8 月 1 日输出和论文复核哈希。
7. 对照 AC-01～19 给出 `ACCEPT / REWORK / HOLD`，附证据路径。

只有 Codex 明确给出 `ACCEPT` 后，本加固任务才完成。

