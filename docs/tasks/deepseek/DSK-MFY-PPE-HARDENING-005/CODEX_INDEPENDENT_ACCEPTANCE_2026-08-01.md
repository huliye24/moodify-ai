# DSK-MFY-PPE-HARDENING-005｜Codex 独立验收

**日期：2026-08-01**  
**最终判定：HOLD**  
**含义：当前实现不得被标记为完成或作为已封口 PPE 基线；需要受控返工后重新验收。**

## 1. 已独立确认的通过项

- `pytest -v`：23/23 passed。
- `ruff check src tests`：通过。
- `mypy src`：通过。
- 通过已安装的 `moodify-bridge.exe` 控制台入口，两次合成案例均得到 `PASS_WITH_WARNINGS`。
- 哈希失配能够产生最终 FAIL，非空目录能够拒绝覆盖。
- 六个 GateResult 可输出为结构化 JSON。

这些事实证明本轮实现有价值，但不能冲销以下 P0/HOLD 项。

## 2. HOLD 原因

### H-01｜只读基线被 Worker 写入

任务编排明确规定 `outputs/ppe_2026-08-01/` 只读，并规定“只读资产哈希变化立即停止并判定 HOLD”。Worker 在 Batch A 对基线 `ledger.duckdb` 执行会追加记录的 `rule validate`，造成哈希变化，随后自行将其降级为非阻断并继续报五批 PASS。

该行为违反 AC-02、任务停止规则和 Worker 权限边界。即使写入是 append-only，也不能由 Worker 单方面重新定义只读含义。

### H-02｜晋级仍未满足原子性门禁

当前 CLI 先执行 `db.add_approval(record)`，再执行规则 YAML 写入。Worker 自己承认极端断电或文件写入失败会留下“approval 已入库、规则未晋级”的部分状态。

任务 AC-04 明确要求对写入失败注入并证明原子失败；任务停止规则明确要求“无法证明失败不会留下部分晋级状态”时 HOLD。现有 `test_promotion_atomicity.py` 没有调用实际晋级 CLI，也没有注入 `write_yaml` 失败，因此不能支持“原子性通过”的声明。

### H-03｜HANDOFF 的精确复现命令无效

HANDOFF 和 README 指定：

```powershell
py -3.12 -m moodify_bridge.cli ppe run demo/case.yaml --output-dir NEW_RUN_DIR
```

独立执行结果：退出码为 0，但没有 CLI 输出、没有创建目录、没有生成任何产物。`cli.py` 已缺失原有的 `if __name__ == "__main__": app()` 模块入口。

因此 AC-10（单入口完整）和 AC-18（后来者可按 HANDOFF 独立复现）失败。已安装的 `moodify-bridge.exe` 可以运行，不能证明文档声明的命令可运行。

## 3. 必须返工的 REWORK 项

### R-01｜同一次失败验证同时记录 PASS 和 FAIL

哈希失配独立重放后，`command_results.jsonl` 对相同 `case_validate`、相同开始时间先写 `PASS/0`，再写 `FAIL/1`。这是自相矛盾的审计记录。无效验证只能产生一个终态结果。

### R-02｜环境报告错误标记 PyYAML absent

环境采集调用 `__import__("PyYAML")`，但实际导入模块名为 `yaml`。生成的 `environment.json` 把已经安装且正在使用的 PyYAML 写成 `absent`，环境证据不可信。

### R-03｜稳定错误码未真正实现

规则晋级的预期错误只输出自然语言 `Error: ...` 和退出码 2，没有编排所要求的稳定 reason/error code。应输出例如 `APPROVAL_FILE_MISSING`、`APPROVAL_RULE_MISMATCH`、`INVALID_RULE_TRANSITION`，并由 CLI 测试断言。

### R-04｜关键 CLI 和 Runner 行为缺少自动化测试

现有 13 个新增测试集中于 schema 和 `validate_rule`；没有 `test_ppe_runner.py`、`test_failure_matrix.py`，也没有覆盖：

- 文档声明的 `python -m` 入口；
- 成功运行九项产物；
- 非空目录拒绝；
- 哈希失配的唯一终态记录；
- 无效 YAML/缺失 manifest 的失败 manifest；
- 实际 CLI 晋级的零副作用；
- 写入失败注入；
- manifest 产物存在性和 SHA-256；
- 双运行规范化比较。

因此“失败矩阵 6/6”和“双运行确定性”主要是手工证据，尚未进入可继承的测试形式。

### R-05｜产物完整性没有哈希契约

RunManifest 保存若干路径，但没有保存生成产物的 SHA-256/字节数；无法仅凭 manifest 验证其引用的 evidence、报告和命令日志仍是当时产物。AC-15 尚未形成可机器核验的形式。

## 4. 独立运行证据

Codex 临时验收目录：

```text
E:\moodify\tmp\codex_acceptance_ppe_005\
```

其中：

- `run_a/`、`run_b/` 未出现：证明 HANDOFF 的 `python -m` 命令空运行。
- `exe_run_a/`、`exe_run_b/`：控制台脚本成功运行证据。
- `hash_case/out/command_results.jsonl`：同一次验证同时 PASS/FAIL 的证据。
- `nonempty/sentinel.txt`：非空目录拒绝测试。

## 5. 唯一允许的下一步

DeepSeek 进行一次限定返工，不得扩大范围：

1. 恢复并测试 `python -m moodify_bridge.cli` 入口。
2. 将所有预期 CLI 失败映射到稳定错误代码且无 traceback。
3. 修复验证结果重复记录。
4. 修复 PyYAML 环境探测。
5. 为 Runner、CLI、失败矩阵、确定性和产物哈希新增真实自动化测试。
6. 设计并实现可恢复的跨 DB/文件晋级协议；至少通过 transaction marker、临时文件、补偿/恢复流程和写入失败注入，证明不会把部分状态呈现为成功。如果需要 migration/schema，必须先停止请求授权。
7. 不得尝试回写、删除或“修复”已经改变的 8 月 1 日基线账本；只记录污染事实，并在全新 Codex 指定基线中重新验收。
8. 更新 HANDOFF，状态只能为 `REWORK_COMPLETE_READY_FOR_REVIEW`，再次等待 Codex 验收。

在上述问题关闭前，本任务保持 **HOLD**。

