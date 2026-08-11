# ME-002 — 证据门控发展

**状态：** PROPOSED  
**版本：** 0.1  
**适用对象：** 能力成熟度晋级、experimental → canonical、发布声明、权限扩大、自动化范围扩大、架构身份变更  
**不适用对象：** 不携带成熟度或身份含义的日常进度记录

## 1. 来源命题

计划、版本号、演示、代码完成和单项测试只能证明发生了工作，不能自动证明系统获得了新的能力或身份。重要声明必须先定义其证明责任，并在证据满足范围、有效性、归因、复现和留存要求后，才允许改变 Moodify 的架构地位、权限或对外语言。

思想来源：

- `ODSC-005 — Developmental Gates in Long-Lived Systems`；
- `ODSC-008 — Evidence-Gated Development`；
- `MODM-001 — The Origin of Moodify`。

来源文件位于外部研究目录 `E:\软件建造的哲学`。本约束只吸收与 Moodify 当前工程治理直接相关的部分。

## 2. Moodify 工程命题

Moodify 的进展单位不只是 feature，而是一个能够被反驳的 claim。

例如：

```text
“实现了 CQT”                         -> implementation claim
“CQT 在指定真实案例中提供增量证据”     -> operational claim
“CQT 应进入 canonical scan”            -> constitutional claim
“历史 CQT 证据改善了后续判断规则”       -> accumulative claim
“外部机构可以依赖该判断”                -> industrial claim
```

前一层证据不能自动证明后一层声明。尤其禁止用 implementation claim 的绿色测试，直接换取 canonical、自治、平台或产业身份。

## 3. Claim 分类

### ME-002-K1：Implementation

证明机制存在并按规格运行。典型证据包括单元测试、集成测试、静态检查、schema 验证和可重复构建。

### ME-002-K2：Operational

证明机制在真实或生产近似条件下有效。典型证据包括真实 Production Case、资源测试、故障注入、恢复演练和跨环境复现。

### ME-002-K3：Constitutional

证明 authority、状态变化和责任边界受到实际约束。典型证据包括越权动作被阻断、旁路不可获得合法结果、审计链完整和失败状态保持真实。

### ME-002-K4：Accumulative

证明历史证据以受控方式改变并改善后续行为。典型证据包括案例集合、理论或规则版本、对照结果、反例和 rule lineage。

### ME-002-K5：Industrial

证明外部主体能够依赖系统的语义、证据和连续性。典型证据包括外部采用、独立实现、兼容性验证、真实依赖和争议重建。

## 4. 约束

### ME-002-C1：先写 Claim，后判完成

任何会改变成熟度、canonical 地位、权限或身份语言的工作，必须给出可以被证伪的 Claim，而不能只列交付文件和完成百分比。

### ME-002-C2：证据范围不得小于声明范围

合成信号只能支持合成范围；单机测试只能支持该环境；一个成功案例不能证明普遍可靠；技术指标不能单独证明艺术质量或产业价值。

### ME-002-C3：结果必须能够归因

证据必须说明结果来自被声明的机制，而不是人工修复、不同执行路径、未记录参数、挑选样本或验证模型与被验证模型共享的循环假设。

### ME-002-C4：负面证据必须保留

失败案例、反例、跳过项、警告和不支持声明的结果不得从证据包中选择性删除。没有观察到失败，不等于证明安全。

### ME-002-C5：证据必须可定位和可重放

证据包至少应记录输入身份、代码或规则版本、配置、运行环境、输出身份、验证方法和结论范围。不能重建来源的截图、口头结论或临时日志不足以承担长期 Claim。

### ME-002-C6：证明责任随后果增加

Claim 引发的影响、不可逆性、外部依赖、委托权限和有效期限越大，所需证据必须越强，且不能仅由实现者本人宣布通过。

### ME-002-C7：通过不是永久状态

依赖、实现、schema、profile、规则或生产环境发生实质变化时，相关 Claim 必须重新审查。回归证据可以缩小、重开或撤销已通过的声明。

## 5. 最小 Gate 记录

适用变更在晋级前至少记录：

```text
Claim ID:
Claim statement:
Claim class:
Scope:
Current status:
Required evidence:
Exclusion conditions:
Contradictory / negative evidence:
Uncertainty and known limits:
Evidence artifact refs:
Decision authority:
Regression triggers:
Decision:
```

Claim statement 必须足够精确，使未来证据有可能证明它为假。

## 6. Gate 决议

只允许以下明确结果：

- `PASSED`：在声明范围内证据充分；
- `PASSED_NARROWED`：只证明了比原声明更小的范围；
- `PROVISIONAL`：允许有限使用，仍需持续证据；
- `DEFERRED`：证据不足，但尚未出现直接反证；
- `FAILED`：证据未达到证明责任；
- `INVALIDATED`：证据过程受污染或违反排除条件；
- `REOPENED`：环境变化或新证据要求重新审查；
- `REVOKED`：原 Claim 已不再成立。

不得用模糊的“基本完成”“效果不错”“大体可用”代替 Gate 决议。

## 7. 与现有 Moodify 门禁的关系

ME-002 不创建新的 case lifecycle，也不替代当前 freeze gates。它为现有门禁补充统一解释：

- `CODE_FREEZE_POLICY.md` 的 exit condition 是 Claim 的证明责任；
- `case_manifest.json`、JSON/NPZ 和哈希是证据链的一部分，不因存在而自动证明 Claim；
- `LEGACY / EXPERIMENTAL / CANONICAL` 是架构地位，晋级必须引用相应 Gate 决议；
- 测试通过首先支持 implementation claim，是否支持更高层声明必须另行审查；
- 人类仍拥有高后果身份声明和架构晋级的最终决策权。

## 8. 失败处置

当声明超出证据时：

1. 保留已有实现和有效证据，不伪造整体失败；
2. 将 Claim 缩小到证据实际覆盖的范围；
3. 保持 `EXPERIMENTAL` 或原有权限，不提前晋级；
4. 记录缺失证据、排除条件和下一次验证方法；
5. 若原声明已进入文档、界面或发布材料，同步修正语言；
6. 若既有 Claim 回归，评估依赖它的权限、规则和下游声明。

## 9. 激活条件

ME-002 从 `PROPOSED` 变为 `ACTIVE` 前，需要：

- 用最小 Gate 记录审查一个真实 experimental operator；
- 证明它能区分“代码已完成”和“能力已成立”；
- 确认 Gate 决议不会与现有 Phase I freeze 权威冲突；
- 再决定是否建立机器可读 Claim Ledger 或 CI 校验。
