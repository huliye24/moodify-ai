# DSK-MFY-CAPABILITY-ACCRETION-019｜验证报告

**日期：** 2026-08-02 UTC

## 1. 测试结果

| 套件 | 结果 |
|---|---|
| `tests/capability_registry/test_execution.py`（新增 14） | **14/14 PASS** |
| capability_registry 全量（017/018/019 = 50） | **50/50 PASS** |
| 009 回归 `tests/score_engine/`（55） | **55/55 PASS** |
| Ruff | clean |
| CLI 全链路：plan → approve → execute | 正常 |
| 旧 CLI 回归 | 无回归 |

## 2. CLI 端到端（合成 fixture，`outputs/deepseek_validation/DSK-MFY-CAPABILITY-ACCRETION-019/`）

| 步骤 | 命令 | 结果 |
|---|---|---|
| plan | `capability plan --provider ffprobe.cli --input source=tone.wav ...` | ✅ envelope 草案（unsigned） |
| approve | `capability approve --issuer deepseek-worker --policy-version policy/0.1` | ✅ 签名绑定 |
| execute（未批准） | `capability execute env2.json`（unsigned） | ✅ 拒绝 exit=2 |
| execute（已批准） | `capability execute env.json` | ✅ completed，record 落盘 |
| **篡改** | 改 output_dir 后执行 | ✅ signature mismatch 拒绝 exit=2 |

## 3. 失败矩阵

| 场景 | 期望 | 实测 |
|---|---|---|
| 未批准执行 | failed + policy_rejection | ✅ |
| 签名失效（内容篡改） | failed + signature mismatch | ✅ |
| 输入哈希不匹配 | failed + policy_rejection | ✅ |
| 网络执行 | failed + 拒绝 | ✅ |
| provider/capability 不匹配 | 签名层拦截（篡改无法绕过） | ✅ |
| 失败记录 evidence 完整 | failed + 保留 evidence | ✅ |
| in-flight 追踪 | 执行中可见、结束后清除 | ✅ |
| 记录持久化 | JSON 落盘且字段完整 | ✅ |

## 4. 未运行项（如实记录）

- 179 个 Workspace v2 全量回归未跑（未触碰 Core 实现）。
- 未接入 cli_v2 case 系统（编排明确不强行接入，对接顺序已在架构文档注明）。

## 5. 过程中失败与修正（记入 FAILURE_LEDGER）

- 测试用假 WAV（`RIFF\x00`）导致 ffprobe exit 1 → 改用合法 8kHz 正弦波 fixture。
- 篡改测试初版断言"serves"错误——实际篡改在签名层被拦截（这正是不可变性的
  设计保证）→ 断言改为 signature mismatch。
