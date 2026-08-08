# DSK-MFY-CAPABILITY-ACCRETION-020｜验证报告

**日期：** 2026-08-02 UTC

## 1. 测试结果

| 套件 | 结果 |
|---|---|
| `tests/capability_registry/test_validation.py`（新增 11） | **11/11 PASS** |
| capability_registry 全量（017-020 = 61） | **61/61 PASS** |
| 009 回归 `tests/score_engine/`（55） | **55/55 PASS** |
| Ruff | clean |
| CLI smoke：`capability validate`、`capability candidates` | 正常 |
| 旧 CLI 回归 | 无回归 |

## 2. 地质记录（ValidationRule.historical_source）

| 规则 | 历史来源 |
|---|---|
| output_exists | 009 FAILURE_LEDGER #10（空产物曾被报成功） |
| nonzero_size | 009 FAILURE_LEDGER #4（空 SVG 曾当成功导出） |
| source_hash_linked | 工程厚度标准 §4.4（派生数据不得脱离源成为权威） |
| no_nan | 音频 DSP NaN 污染历史 |
| page_count_nonzero | notation.render 合同（空 PDF = 假成功） |
| roundtrip_visible | 009 ROUNDTRIP_LOSS_CONTRACT / EX-005（"成功导出"不得掩盖损失） |

**每条规则都携带真实来历（POSC-003 地质记录），无来源规则不注册。**

## 3. 失败矩阵

| 场景 | 期望 | 实测 |
|---|---|---|
| 空产物 | error 级拒绝 | ✅ |
| 空文件产物 | error 级拒绝 | ✅ |
| 输入哈希缺失/畸形 | error 级拒绝 | ✅ |
| round-trip FAIL | error 级拒绝 | ✅ |
| 规则不可被 provider 关闭 | 规则集来自 registry+能力绑定 | ✅ |
| 候选排序 | accepted 优先 | ✅ |
| 拒绝理由结构化 | rule_id+measured+expected | ✅ |
| 记录重放验证 | 从 ExecutionRecord 重建 context | ✅ |

## 4. 未运行项（如实记录）

- 179 个 Workspace v2 全量回归未跑（未触碰 Core 实现）。
- 多 provider 候选的真实执行（如 transcode 双 provider）未跑——本机
  media.transcode 仅 ffmpeg 一个 provider；候选机制已测试，多 provider
  场景依赖 018 适配器就绪后由后续任务接入。
- 声明式回退（fallback）仅保留机制（registry 声明路径），未接真实双
  provider 触发场景（本机无第二 provider）。

## 5. 过程中失败与修正（记入 FAILURE_LEDGER）

- 规则对不存在 artifact 调用 stat() 报 FileNotFoundError → 防御性 exists() 检查。
- CLI validate PASS 时仍打印失败消息 → 显示逻辑修正（PASS 不显示 detail）。
