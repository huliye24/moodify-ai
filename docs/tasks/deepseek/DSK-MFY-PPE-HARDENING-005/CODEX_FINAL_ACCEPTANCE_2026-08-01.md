# DSK-MFY-PPE-HARDENING-005｜Codex 最终验收

**日期：2026-08-01**  
**最终判定：ACCEPT_WITH_RECORDED_INCIDENT**

## 结论

PPE 加固实现已达到本轮可接受状态，可以作为后续真实样本工作的工具链基线。第一次 Worker 运行对旧 `outputs/ppe_2026-08-01/ledger/ledger.duckdb` 的越权追加仍作为不可抹除事件保留；该文件不是洁净复验基线，不得通过回写或删除历史来伪装恢复。

新的 Codex 独立验收基线：

```text
E:\moodify\outputs\codex_acceptance\DSK-MFY-PPE-HARDENING-005-R2\
```

## Codex 收尾修改

1. 修复 promotion marker 恢复：DB 写入后文件替换失败时保留 marker 与临时文件；相同请求重试会完成替换并保持 approval 单行。
2. 对 marker 请求不一致、approval 不一致、恢复文件缺失或再次替换失败执行 fail-closed，不删除恢复证据。
3. 新增 `PROMOTION_RECOVERY_REQUIRED` 稳定错误码。
4. 为 RunManifest 增加 `artifact_hashes`，覆盖 environment、命令日志、闸门、最终状态、evidence、DuckDB 和双格式报告。
5. 新增 DB 写入后 replace 失败及幂等恢复测试，以及逐项产物 SHA-256 复核测试。
6. 更新 README，说明哈希契约和恢复协议。

## 独立验证

- `pytest -v`：43 passed。
- `ruff check src tests`：通过。
- `mypy src`：通过。
- `python -m moodify_bridge.cli` 双目录执行：均为 `PASS_WITH_WARNINGS`、退出码 0。
- 两次运行各有 8 个 manifest artifact hashes，逐项重新计算全部匹配。
- PyYAML：正确报告 6.0.3。
- 缺失批准：`APPROVAL_FILE_MISSING`，退出码 2。
- 非空输出目录：`OUTPUT_DIR_NOT_EMPTY`，退出码 2。
- replace 失败：保留 approval、marker 和 temp；相同命令重试成功，approval 不重复。

## 保留边界

- 合成案例无真实音频测量、候选比较和人工批准，相关闸门保持 WARN；本验收不证明声音改善。
- 跨 DuckDB 与文件系统不存在单一 OS 原子事务；当前保证的是可检测、可恢复、不可误报成功。
- 原 8 月 1 日账本污染事件继续记录在 Failure Ledger，不得把它表述为未发生。

本任务至此完成。下一阶段可以使用新的统一 PPE 入口处理已授权、已冻结的验证集，但仍须经过真实测量与人工听感门禁。

