# Codex 独立验收矩阵｜DSK-MFY-CLI-NATIVE-REFACTOR-015

## P0

| ID | 验收项 | 失败处置 |
|---|---|---|
| P0-01 | CLI/JSON 是正式合同，不是 GUI 或 shell 包装 | REWORK |
| P0-02 | Canonical project 是项目、决策、运行和证据事实源 | REWORK |
| P0-03 | domain 无 CLI/subprocess/GUI/第三方实现依赖 | REWORK |
| P0-04 | source 只读且 hash 不变，输出只进新目录 | HOLD |
| P0-05 | plan/dry-run 与 execute 分离，错误 fail closed | REWORK |
| P0-06 | JSON stdout 纯净、stderr 分离、退出码稳定 | REWORK |
| P0-07 | 无隐式联网/安装/许可/全局配置修改 | HOLD |
| P0-08 | 旧 CLI 和相关回归通过，无删除式迁移 | REWORK |
| P0-09 | 无用户 dirty/untracked 文件被覆盖 | HOLD |
| P0-10 | 前置能力状态真实，不伪造 PASS | HOLD |

## 架构与功能

| ID | 验收项 |
|---|---|
| F-01 | Project/Asset/Decision/Plan/Run/Artifact/Revision/Evidence 严格模型 |
| F-02 | domain/app/ports/adapters/cli_v2 依赖方向成立且无循环 |
| F-03 | project/result/evidence schema 可独立验证与 round-trip |
| F-04 | capabilities/version/project init/inspect 的 JSON 合同成立 |
| F-05 | import→plan→dry-run→execute→verify 最小闭环成立 |
| F-06 | dry-run 无音频派生物，execute 证据完整 |
| F-07 | 幂等键、取消、超时和失败状态可解释 |
| F-08 | 旧命令兼容映射与结构化 deprecation 成立 |
| F-09 | 未实现/不可用 backend 返回真实 typed error |

## 验证

| ID | 验收项 |
|---|---|
| V-01 | Unicode/空格/特殊路径及路径逃逸防护 |
| V-02 | JSON stdout、stderr、退出码自动测试 |
| V-03 | schema 错误、缺失源、未知能力、超时/取消失败注入 |
| V-04 | 双运行确定性或合同定义的内容级等价 |
| V-05 | 源 hash、artifact hash、evidence 回读一致 |
| V-06 | 旧 CLI smoke、相关回归、import boundary、lint/type check |

Codex 必须独立重跑关键命令、检查 stdout/stderr、抽查 schema/evidence/hash 和依赖边界。DeepSeek 自报 PASS 不代表验收通过。

