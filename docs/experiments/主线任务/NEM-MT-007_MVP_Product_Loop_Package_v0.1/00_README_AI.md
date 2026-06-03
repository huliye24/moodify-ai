# NEM-MT-007｜AI 接手说明

你是接手 Moodify NEM-MT-007 节点的工程执行 Agent。

## 执行规则

1. 不要重新设计整套 Moodify。
2. 先读取 `00_PACKAGE_MANIFEST.json`。
3. 再读取 `00_NODE_STATUS.md`。
4. 再读取 `rules/AI_Execution_Rules.md`。
5. 当前优先执行 `aep/AEP-MT007-001_MVP_Product_Scope.md`。
6. 每次只推进一个 AEP。
7. 完成后更新 `decisions/Decision_Log.md` 与对应报告。
8. 不要扩大 MVP 范围。
9. 不要先做复杂 GUI。
10. 所有输出必须能追踪到 input、preset、runtime_job、mrs_result、report、export_manifest。

## MVP 固定闭环

```text
Import -> Validate -> Select Preset -> Process -> Score -> Explain -> Export
```

## 禁止事项

- 不要加入支付系统。
- 不要加入用户账号系统。
- 不要加入多租户云平台。
- 不要加入复杂权限系统。
- 不要把 MT-007 做成完整商业版产品。

MT-007 的目标是最小闭环，而不是最终形态。
