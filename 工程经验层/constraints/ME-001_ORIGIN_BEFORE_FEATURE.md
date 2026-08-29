# ME-001 — 起源先于功能

**状态：** PROPOSED  
**版本：** 0.1  
**适用对象：** 新 subsystem、新 canonical capability、新产品表面、主线语义变更  
**不适用对象：** 不改变行为的修复、已授权维护、纯证据补录、明确标记且隔离的研究原型

## 1. 来源命题

长期软件不应通过无边界地拼装功能成长，而应从稳定的起源推导必要结构。执行能力越充足，错误方向被快速实现的代价越高。

思想来源：

- `ODSC-001 — The Origin Before the Feature`；
- `ODSC-003 — From Origin to Architecture`；
- `ODSC-004 — Necessary Structures and Accidental Features`；
- `MODM-001 — The Origin of Moodify`。

来源文件位于外部研究目录 `E:\软件建造的哲学`。本约束是对这些材料的 Moodify 工程转译，不等同于复制其全部主张。

## 2. Moodify 工程命题

Moodify 的当前起源是：

> **The Ear of AI — an Auditory Intelligence System.**

新能力只有在能够服务以下循环中的明确责任时，才有资格进入主线：

```text
Listen -> Represent -> Judge -> Intervene -> Verify -> Learn
```

“技术上能实现”“竞争产品已有”“比赛需要”或“界面上看起来完整”，都不能单独构成进入 canonical 的理由。

## 3. 必须回答的六个问题

任何适用范围内的变更，在成为 canonical 之前必须回答：

1. 它服务哪个 Production Case，或解决哪个已观察到的听觉问题？
2. 它属于 Listen、Represent、Judge、Intervene、Verify、Learn 中哪一环？
3. 它新增的是必要责任，还是当前工具/界面造成的偶然功能？
4. 它产生什么 Measurement Record、Evidence Artifact 或可复现结果？
5. 为什么现有 canonical subsystem、窄适配器或实验 operator 不能承担这项责任？
6. 失败时如何阻断、降级、隔离或留下可供下一案例复用的失败证据？

任一问题没有答案，不等于永久拒绝该能力；默认结论应是保持 `EXPERIMENTAL`、缩小范围或延后决策。

## 4. 约束

### ME-001-C1：来源可追溯

进入主线的能力必须能追溯到一个明确的产品责任、生产案例或经验证的结构缺口。

### ME-001-C2：主线唯一

变更不得创建第二套 authoritative lifecycle、judgment authority、metric truth 或 orchestration path。

### ME-001-C3：实验先于权威

尚未证明增量价值的高级算法、表示或工作流必须保持 `EXPERIMENTAL`，不能因代码可运行而自动成为 canonical。

### ME-001-C4：必要结构与偶然实现分离

长期责任应以稳定 contract、schema、invariant 或 evidence relation 表达；具体库、模型、供应商、界面和文件格式应尽量保持可替换。

### ME-001-C5：证据先于身份声明

不得在真实案例和验证证据之前，宣称 Moodify 已获得新的产品身份、成熟能力或生产真值。

## 5. 当前验证方式

v0.1 采用人工差异审阅，不立即增加新的 CI 阻断器。适用变更应在任务说明、PR 或证据报告中提供六个问题的答案，并检查：

- 是否修改 `PHASE1_CONSTITUTION.md` 所列 canonical authority；
- 是否与 `LEGACY_AND_EXPERIMENTAL_POLICY.md` 的状态标签一致；
- 是否产生或引用可定位的验证证据；
- 是否说明失败语义和恢复路径；
- 是否避免把 provider、算法或 UI 误写成 Moodify 的产品身份。

## 6. 失败处置

发现违反本约束时，按最小影响原则处理：

1. 停止 canonical promotion；
2. 将能力保持或降级为 `EXPERIMENTAL`；
3. 记录缺失的案例、证据或权威决策；
4. 优先寻找窄适配器或复用现有主线；
5. 只有在明确的人类架构决策后，才修改 constitution 或 authority map。

## 7. 激活条件

ME-001 从 `PROPOSED` 变为 `ACTIVE` 前，需要：

- 人工确认这六个问题足以约束首批变更；
- 至少在一个真实变更中试用并记录审阅结果；
- 确认它没有与当前 Phase I freeze 和 authority order 冲突；
- 再决定是否把部分检查自动化。
