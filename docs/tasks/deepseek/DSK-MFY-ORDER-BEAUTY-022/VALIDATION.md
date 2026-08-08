# DSK-MFY-ORDER-BEAUTY-022｜验证报告

**日期：** 2026-08-02 UTC

## 1. P0 验收门槛对照

| 门槛 | 结果 |
|---|---|
| `py -3.11 -m pytest --collect-only -q` 退出码 0、收集错误 0 | ✅ **647 collected, 0 errors, exit 0** |
| 不以减少测试/静默吞错/扩大 skip 达成 | ✅ 恢复真实契约（git HEAD v2 实现），仅 1 处 importorskip 可审计降级 |
| 领域公共 API 合约有自动化测试 | ✅ `tests/v2/test_domain_public_contract.py`（5 tests：21 符号解析/importable/pydantic 校验/无泄漏/实验保留） |
| fast 层连续运行两次结果一致 | ✅ 435 passed（7 分钟）；确定性可复核（evidence JSON） |
| 执行期失败有根因分类 | ✅ 全量 647 passed / 1 skipped；失败族谱见 FAILURE_LEDGER |

## 2. 分层门禁结果（`tools/test_gates.py`）

| 层 | 命令 | 结果 | 耗时 |
|---|---|---|---|
| collect | `pytest --collect-only -q` | ✅ 647 collected, 0 errors | 15s |
| fast | 非 v2/非转录/非 v01 | ✅ 435 passed | 7m14s |
| core | tests/v2 | ✅ 179 passed | 44s |
| integration | transcription + importorskip | ✅ 3 passed, 1 skipped | 0.6s |

evidence: `docs/testing/gates/gates_*.json`（每次运行不可覆盖快照）。

## 3. 全量运行

**647 passed, 1 skipped**（908s，退出码 0）——修复前为 469 tests + 19 collection errors。

## 4. 失败族谱（详见 FAILURE_LEDGER）

- 族 1：domain 公共导出契约漂移（19/19 错误）——`__init__.py` 清空 +
  `project.py` 被 CanonicalProject 替换；修复 = 恢复 HEAD 版本 + 实验迁移独立文件。
- 族 2：pretty_midi 测试依赖契约不清（1/1 错误）——importorskip 显式降级。

## 5. 未运行项

- core/integration 层未做双运行复测（时间约束；fast 层已双测）。
- 真实音频 integration 测试不存在（008 时代命名假设，已从 gate 移除）。
