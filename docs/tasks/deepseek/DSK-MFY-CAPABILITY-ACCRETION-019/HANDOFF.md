# DSK-MFY-CAPABILITY-ACCRETION-019 HANDOFF

**Status:** READY_FOR_CODEX_REVIEW  
**Worker:** DeepSeek | **Date:** 2026-08-02 UTC  
**Branch:** `codex/mainline-cloud-dev-20260603` | **HEAD:** `df3a8a3c`（未提交新 commit）

## 三阶段状态

| Stage | 状态 |
|---|---|
| Stage A（ApprovedExecutionEnvelope） | PASS |
| Stage B（ExecutionGateway 与记录） | PASS |
| Stage C（CLI、验证与文档） | PASS |

最终判定：**READY_FOR_CODEX_REVIEW**（本 Worker 不得宣布 ACCEPT）。

## CLI

```powershell
py -3.11 -m moodify.cli capability plan --provider ffprobe.cli --case-id <id> \
    --input source=a.wav --output-dir <newdir> --out env.json       # 生成未签名草案
py -3.11 -m moodify.cli capability approve --envelope env.json \
    --issuer <operator> --policy-version policy/0.1                  # 本地签名批准
py -3.11 -m moodify.cli capability execute --envelope env.json \
    --records-dir execution_records                                 # 经网关执行
```

## 交付物

| 位置 | 内容 |
|---|---|
| `moodify-core-package/src/moodify/capability_registry/execution/` | envelope（不可变+签名）、gateway（唯一入口+记录）、cli |
| `moodify-core-package/src/moodify/cli.py` | `capability plan/approve/execute` 挂载 |
| `moodify-core-package/tests/capability_registry/test_execution.py` | 14 个测试 |
| `docs/architecture/CAPABILITY_ACCRETION_ARCHITECTURE.md` | Workflow 层状态更新 |
| `docs/tasks/deepseek/DSK-MFY-CAPABILITY-ACCRETION-019/` | PROGRESS/VALIDATION/FAILURE_LEDGER/HANDOFF |

## 关键设计（Law 3 落地）

- **无 envelope 不得执行**：gateway 是唯一执行入口，adapter 不可被上层直接调用。
- **不可变性**：envelope 内容哈希 → 签名绑定；任何篡改（含 output_dir 路径
  逃逸）在签名层被拦截，无法到达 provider——**篡改测试实测通过**。
- **输入哈希锁定**：执行前逐一重校验（path 存在 + sha256 一致）。
- **权限**：网络执行默认拒绝；输出目录必须绝对路径；provider/capability 一致性校验。
- **ExecutionRecord 全量保留**：状态机（envelope_created→approved→executing→
  completed/failed）、退出码、耗时、artifacts、errors、error_class、evidence
  全部落盘 JSON；失败记录不静默丢弃。
- **in-flight 追踪**：执行中可见、结束后清除（测试验证）。

## 验证摘要

- 50/50 capability_registry + 55/55 score_engine 回归；Ruff clean。
- CLI 全链路实测：plan → approve → execute → record 落盘。
- 失败矩阵：未批准/篡改/哈希不匹配/网络/失败证据/in-flight 全部有测试。
- 未运行：179 Workspace v2 全量回归（未触碰 Core）；未接入 cli_v2 case
  （编排明确不强行接入）。

## 限制（事实边界）

- CLI 本地签名为模拟批准；真实人工审批签名机制是后续工作。
- 未接入 cli_v2 case 系统；对接顺序在架构文档注明（019 是独立最小证明）。
- 本地签名不防内部恶意操作（信任边界：approve 是 operator 动作）。

## Codex 验收命令

```powershell
py -3.11 -m pytest tests/capability_registry/test_execution.py -v
# 全链路（合成 fixture）：
py -3.11 -m moodify.cli capability plan --provider ffprobe.cli --case-id codex \
    --input source=<wav> --output-dir <newdir1> --out codex_env.json
py -3.11 -m moodify.cli capability execute --envelope codex_env.json --records-dir <recs>   # 应拒绝
py -3.11 -m moodify.cli capability approve --envelope codex_env.json --issuer codex
py -3.11 -m moodify.cli capability execute --envelope codex_env.json --records-dir <recs>   # 应成功
# 篡改：改 codex_env.json 的 output_dir 后 execute 应报 signature mismatch
py -3.11 -m moodify.cli score backends   # 旧 CLI 回归
```

DeepSeek Worker 停止于此。最终判定属于 Codex。
