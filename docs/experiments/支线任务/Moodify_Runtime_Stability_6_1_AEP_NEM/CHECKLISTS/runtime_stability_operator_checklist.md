# Runtime 稳定性实验 6.1 操作清单

## 执行前

- [ ] 确认项目路径正确。
- [ ] 确认 Python 环境可用。
- [ ] 确认 ffmpeg 可用。
- [ ] 确认磁盘空间充足。
- [ ] 确认输入样本存在。
- [ ] 确认输出目录可写。
- [ ] 确认日志目录可写。
- [ ] 确认 summary 输出路径可写。
- [ ] 确认当前没有冲突的旧进程。
- [ ] 确认 stale lock 已清理。

---

## 阶段一：基础可靠性

- [ ] 执行 AEP-6.1.01 特殊文件名 Smoke Test。
- [ ] 检查 unrecognized arguments 是否为 0。
- [ ] 执行 AEP-6.1.07 日志完整性实验。
- [ ] 检查每个任务是否有 start/end/status/exit_code。
- [ ] 执行 AEP-6.1.08 Summary 自动生成实验。
- [ ] 检查 summary 是否生成。

---

## 阶段二：真实任务吞吐

- [ ] 执行 AEP-6.1.02 90-task Full Test。
- [ ] 统计成功率。
- [ ] 统计 exit code 分布。
- [ ] 统计平均耗时、P90、P95。
- [ ] 执行 AEP-6.1.05 失败熔断实验。
- [ ] 检查连续失败后是否触发熔断。
- [ ] 执行 AEP-6.1.06 任务恢复实验。
- [ ] 检查已完成任务是否被跳过。
- [ ] 检查未完成任务是否继续执行。

---

## 阶段三：长时无人值守

- [ ] 执行 AEP-6.1.03 6h Endurance Run。
- [ ] 检查 6h run 是否正常结束。
- [ ] 检查日志是否持续刷新。
- [ ] 执行 AEP-6.1.04 24h Day Run。
- [ ] 检查 24h run 是否自动停止。
- [ ] 检查最终 summary。
- [ ] 检查是否存在卡住任务。

---

## 最终 Gate

- [ ] 根据 `GATES/gate_runtime_stability.md` 判断 ADOPT / HOLD / REJECT。
- [ ] 生成 `reports/runtime_stability_6_1_report.md`。
- [ ] 标注 blocking issues。
- [ ] 给出下一步建议。
