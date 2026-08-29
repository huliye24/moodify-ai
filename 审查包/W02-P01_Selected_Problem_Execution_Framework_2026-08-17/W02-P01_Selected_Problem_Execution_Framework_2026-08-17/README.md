# W02-P01 — Selected Problem Execution Framework

这是 Wave 02 的第一个**真正执行包框架**。

但它仍然没有预设要做什么功能。

它必须读取 W02-P00 中由人类选择的：

`SELECTED_WAVE_02_PROBLEM.md`

才能进入执行。

## 主逻辑

```text
Selected Real Problem
→ Freeze Baseline
→ Lock Scope
→ Minimum Intervention
→ Execute
→ Regression
→ Re-measure
→ Evidence Verdict
```

## 五种结论

- PROBLEM_RESOLVED
- PROBLEM_IMPROVED
- NO_MEANINGFUL_IMPROVEMENT
- REGRESSED
- EVIDENCE_INSUFFICIENT

“代码写完”不等于“问题解决”。

## 这个包的意义

它保证 Wave 02 开始以后不会重新退化成：

> 想到一个功能 → 写代码 → 再想下一个功能。

而是始终围绕一个真实问题进行可测量的干预。
