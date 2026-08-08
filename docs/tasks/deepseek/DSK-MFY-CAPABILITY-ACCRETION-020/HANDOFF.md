# DSK-MFY-CAPABILITY-ACCRETION-020 HANDOFF

**Status:** READY_FOR_CODEX_REVIEW  
**Worker:** DeepSeek | **Date:** 2026-08-02 UTC  
**Branch:** `codex/mainline-cloud-dev-20260603` | **HEAD:** `df3a8a3c`（未提交新 commit）

## 三阶段状态

| Stage | 状态 |
|---|---|
| Stage A（CapabilityValidator 规则库） | PASS |
| Stage B（候选生成与选择） | PASS |
| Stage C（CLI、验证与文档） | PASS |

最终判定：**READY_FOR_CODEX_REVIEW**（本 Worker 不得宣布 ACCEPT）。

## CLI

```powershell
py -3.11 -m moodify.cli capability validate --record <ExecutionRecord.json>   # 重放验证
py -3.11 -m moodify.cli capability candidates --envelope <env.json> \
    --variant key=value ...                                                    # 生成候选变体
```

## 交付物

| 位置 | 内容 |
|---|---|
| `moodify-core-package/src/moodify/capability_registry/validation/` | rules（6 条通用规则+地质来源）、candidates（生成/排序/拒绝理由）、cli |
| `moodify-core-package/src/moodify/cli.py` | `capability validate/candidates` 挂载 |
| `moodify-core-package/tests/capability_registry/test_validation.py` | 11 个测试 |
| `docs/architecture/CAPABILITY_ACCRETION_ARCHITECTURE.md` | Validation 层状态更新 |
| `docs/tasks/deepseek/DSK-MFY-CAPABILITY-ACCRETION-020/` | PROGRESS/VALIDATION/FAILURE_LEDGER/HANDOFF |

## 关键设计

- **每条 ValidationRule 携带 historical_source**（地质记录，POSC-003）：
  6 条通用规则全部有真实来历（009 台账/厚度标准/round-trip 合同/EX-005），
  无来源规则不注册；规则库扩充禁止凑数造规则。
- **规则不可被 provider 关闭**：规则集来自 registry quality_policy 声明 +
  能力绑定，与 provider 无关。
- **验证失败即负面知识**：error 级失败 → RejectionReason（rule_id + 测量值 +
  期望值）结构化保留，候选全部保留（含失败者），不隐藏、不删除。
- **候选每项绑定独立 envelope**（019 不可变性）；排序 accepted 优先。
- **回退仅走声明路径**（registry 声明 fallback），机制就位、真实触发待
  多 provider 环境。
- 验证从 ExecutionRecord 重放（`capability validate --record`），与 019
  记录直接衔接。

## 验证摘要

- 61/61 capability_registry + 55/55 score_engine；Ruff clean。
- 地质记录测试：每条规则有 historical_source；规则不可被 provider 关闭。
- 失败矩阵：空产物/空文件/哈希缺失/round-trip FAIL/排序/结构化理由/重放
  全部有测试。

## 限制（事实边界）

- 本机 media.transcode 仅 ffmpeg 一个 provider：多 provider 候选执行与
  声明式回退的真实触发场景未跑（机制已测试，接入待后续）。
- 179 个 Workspace v2 全量回归未跑（未触碰 Core 实现）。
- 验证规则库为首批 6 条，后续按地质记录规则扩充。

## Codex 验收命令

```powershell
py -3.11 -m pytest tests/capability_registry/test_validation.py -v
py -3.11 -m moodify.cli capability validate --record <019 产生的 record.json>
py -3.11 -m moodify.cli capability candidates --envelope <019 的 env.json> --variant output_stem=alt
py -3.11 -m moodify.cli score backends   # 旧 CLI 回归
```

DeepSeek Worker 停止于此。最终判定属于 Codex。
