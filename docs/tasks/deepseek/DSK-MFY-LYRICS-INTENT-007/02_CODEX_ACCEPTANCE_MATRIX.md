# DSK-MFY-LYRICS-INTENT-007｜Codex 独立验收矩阵

## Stage 1｜立意

| ID | 优先级 | 验收项 | 失败判定 |
|---|---|---|---|
| L1-01 | P0 | 歌词被定义为可选证据而非处理控制中心 | HOLD |
| L1-02 | P0 | 创作者声明和 human_owner 主权保持不变 | HOLD |
| L1-03 | P0 | 合同在代码修改前冻结且可追溯 | HOLD |
| L1-04 | P0 | 权利基础、隐私、正文暴露与保留边界明确 | HOLD |
| L1-05 | P0 | 禁止心理/身份/真实意图断言 | HOLD |
| L1-06 | P1 | 事实、人工声明、有限推断、不确定性严格分层 | REWORK |
| L1-07 | P1 | 无歌词兼容与歌词冲突状态语义明确 | REWORK |
| L1-08 | P1 | 不新增第六个默认叙事中心 | REWORK |

## Stage 2｜聆听

| ID | 优先级 | 验收项 | 失败判定 |
|---|---|---|---|
| L2-01 | P0 | 唯一既有命令可处理有/无歌词 Spec | HOLD |
| L2-02 | P0 | 无 rights_basis 时不读取、复制或分析正文 | HOLD |
| L2-03 | P0 | 正文不进入 stdout/result/异常/default summary | HOLD |
| L2-04 | P0 | 路径、编码、大小、NUL、文件类型检查 fail-closed | HOLD |
| L2-05 | P0 | 歌词不能覆盖 One-Point 合同或自动产生 Final | HOLD |
| L2-06 | P1 | lyrics_evidence 分层、可追溯、确定性 | REWORK |
| L2-07 | P1 | 原文/审计副本及全部派生产物被 SHA-256 覆盖 | REWORK |
| L2-08 | P1 | 冲突诚实进入 NEEDS_EVIDENCE 并 Entrust 给 owner | REWORK |
| L2-09 | P1 | 结构识别不伪装成语义/情感理解 | REWORK |
| L2-10 | P1 | 稳定错误码、无 traceback、无部分不可信结果 | REWORK |
| L2-11 | P1 | 旧 CLI 与 006 全量测试无回归 | REWORK |

## Stage 3｜留白

| ID | 优先级 | 验收项 | 失败判定 |
|---|---|---|---|
| L3-01 | P0 | 默认表面仍恰好五个叙事中心 | HOLD |
| L3-02 | P0 | 真实/合成歌词正文泄漏扫描为零 | HOLD |
| L3-03 | P0 | demo、006 验收证据和只读资产哈希不变 | HOLD |
| L3-04 | P1 | 无歌词 golden replay 与 006 行为兼容 | REWORK |
| L3-05 | P1 | 两次新目录运行规范化一致且哈希全匹配 | REWORK |
| L3-06 | P1 | 不少于 12 类失败注入全部符合合同 | REWORK |
| L3-07 | P1 | Pytest、Ruff、Mypy 全部通过 | REWORK |
| L3-08 | P1 | README/HANDOFF 足以让第二执行者复现 | REWORK |

## Codex 将独立执行

1. 审查合同冻结时间、修改路径和 dirty worktree 边界。
2. 构造有歌词、无歌词、中文、多语、反讽声明和歌词/声音冲突案例。
3. 注入缺失 rights、路径逃逸、目录、缺失文件、非 UTF-8、NUL、超限、
   空文本、未知字段、非空输出目录和篡改哈希。
4. 对 stdout、stderr、result、summary、HTML、异常和日志做正文泄漏扫描。
5. 重算 package_manifest 全部哈希并检查相对路径。
6. 从零运行两次并比较规范化结果。
7. 重跑 006 测试、全量 Bridge 测试、Ruff 和 Mypy。
8. 给出 `ACCEPT / REWORK / HOLD`；对安全且范围内的遗留问题直接收尾。
