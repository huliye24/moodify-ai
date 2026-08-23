# 06 — Judgment & BYPASS Policy

**W01-P05 · 2026-08-17**

## JUDGE 输出（§9）

```text
judgment_id / subject / observations / detected conditions
confidence / uncertainty / evidence refs / recommended action
action ∈ {INTERVENE, BYPASS, HUMAN_REVIEW}
```

**不得只输出一个"质量分"。**

## BYPASS 是一等合法决策（§10.1，TST-05）

BYPASS 条件：

- 未发现足够证据支持干预；
- 干预收益不确定；
- 当前 profile 明确保留原信号；
- verification 发现处理版本不优于 source；
- 人类 authority 要求保留。

BYPASS 记录：reason / evidence / decision owner / affected stages / source-final relationship。

> 原则：**不确定时保留原始信号，比强行"处理"更符合 Moodify。**

## Human Authority（§9.1）

- 判断需要人耳权威时允许 `HUMAN_REVIEW_REQUIRED`（P05 不因自动化方便删除人类判断边界）。
- One Song 主链自动完成条件：无 HUMAN_REVIEW 信号且 VERIFY PASS。
- 停住条件：JUDGE 输出 HUMAN_REVIEW 或 VERIFY 要求人工。
- P07 Golden Song 提供人工确认环节。

## 实现

- judger 注入式；默认实现（无注入时）：BYPASS with uncertainty=1.0（保守默认）。
- INTERVENE 仅在 JUDGE action=INTERVENE 时执行；否则 INTERVENE stage = BYPASSED（TST-05）。
