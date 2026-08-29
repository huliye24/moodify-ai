# ME-003 — 整体一致性与同源派生

**状态：** PROPOSED  
**版本：** 0.1  
**适用对象：** 新概念、新实体、新 subsystem、跨层接口、状态或证据语义变更、重复实现收敛  
**不适用对象：** 已证明不改变语义边界的局部实现修复

## 1. 来源命题

软件不是功能集合，而是一个由对象、关系、状态、权威、边界、历史和证据组成的形式世界。局部代码即使能够运行，如果它使用另一套概念、复制一份权威、截断历史关系或让上下游对同一对象产生不同理解，整体仍然会变弱。

思想来源：

- `ODSC-002 — Software as an Unfolding Ontology`；
- `ODSC-003 — From Origin to Architecture`；
- `ODSC-004 — Necessary Structures and Accidental Features`；
- `POSC-001 — Software as a Constructed World`；
- `POSC-002 — Function Is Not Form`；
- `POSC-014 — Architecture as Inheritance`。

来源文件位于外部研究目录 `E:\软件建造的哲学`。本约束不要求接受其全部哲学论证，只把“系统整体必须可持续保持同一世界”转译为 Moodify 工程纪律。

## 2. Moodify 工程命题

Moodify 的整体感不是视觉风格或文件排列，而是同一组意义贯穿所有层：

```text
Origin
  -> Ontology
  -> Architecture
  -> Contracts
  -> Runtime
  -> Evidence
  -> Product / API / CLI
  -> History and learning
```

例如，`ProductionCase` 在 contract、runner、queue、API、Android、artifact 和 dataset 中可以有不同表示，但必须保持同一个身份、生命周期、来源关系和完成语义。任何一层都不能为了局部方便，偷偷创造“另一种 case”。

因此：

> 局部正确是必要条件，整体可解释才是完成条件。

## 3. 整体一致性的七个维度

### ME-003-D1：Identity

同一对象在不同层必须具有稳定身份。不得仅依靠文件名、目录位置、显示名称或临时数据库行推断它是谁。

### ME-003-D2：Meaning

同一术语、状态和指标在 contract、实现、证据与产品表面中必须保持兼容含义。不得发生 silent semantic drift。

### ME-003-D3：Authority

每项状态和判断只能有一个权威所有者。缓存、UI、worker、adapter 和报告可以复制视图，不能复制决定权。

### ME-003-D4：Relation

`derived-from`、`measured-by`、`supported-by`、`failed-because-of`、`supersedes` 等关键关系必须显式保存，不能依赖人类从目录和日志中猜测。

### ME-003-D5：Evidence

每个重要结论都必须能够回到支持它的输入、配置、实现、测量和规则。孤立报告不是完整证据。

### ME-003-D6：Failure

失败语义必须跨层一致。底层失败不能在上层变成成功、空结果或无历史重试；恢复不能重写已经发生的事实。

### ME-003-D7：Continuity

实现、供应商和界面变化时，既有对象、历史证据和公共承诺必须仍可解释。架构应让未来继承理由，而不只是继承代码。

## 4. 约束

### ME-003-C1：先定位，后创建

新增代码前必须先指出它位于哪个 canonical subsystem、哪一层、拥有哪项责任。无法定位的能力默认保持实验性，不为它新建平行主线。

### ME-003-C2：先扩展既有世界，后创造新世界

新需求应优先扩展既有 entity、relation、contract 或窄 adapter。只有现有本体无法诚实表达已观察到的现实，且迁移关系明确时，才引入新核心概念。

### ME-003-C3：一个概念，一个权威语义

同一概念可以有多个读取模型和序列化形式，但只能有一个 authoritative definition。重复 schema、状态枚举、规则表和 orchestrator 必须明确标记为 adapter、experimental、legacy 或待收敛对象。

### ME-003-C4：跨层变化必须成套检查

改变核心对象或语义时，必须检查 contract、runtime、evidence、API/CLI/App、tests、documentation 和历史兼容性。只修改最先报错的一层不构成完成。

### ME-003-C5：不得产生孤儿能力

一个能力若没有合法输入来源、输出消费者、证据归属、失败路径或下一案例复用位置，就不能进入 canonical。它可以作为有边界的研究工具存在。

### ME-003-C6：整体不为局部便利让位

不得为了减少一次映射、少写一个 adapter、快速展示 UI 或复用供应商字段，而让外部实现细节侵入永久 contract、权威状态或产品身份。

### ME-003-C7：整体演化必须显式

如果变更实际改变了 Moodify 的主要对象、责任或边界，应作为架构修订提出，而不能伪装成普通 feature。必须说明旧世界如何迁移、新旧 Claim 如何关联以及哪些不变量继续成立。

## 5. Whole Impact Record

适用变更在进入主线前应回答：

```text
Change ID:
Canonical subsystem:
Layer and responsibility:
Existing entity / relation reused:
New entity / relation introduced:
Authoritative definition owner:
Upstream source:
Downstream consumers:
Evidence produced or preserved:
Failure and recovery semantics:
Historical / migration impact:
Terms whose meanings may change:
Duplicate authority check:
Whole-system verification:
```

如果某一项为“不适用”，应说明理由，不能留给后续实现者猜测。

## 6. 整体性审阅问题

审阅者不只问“代码能否工作”，还要问：

1. 删除具体库、供应商或界面后，这项责任是否仍然成立？
2. 新代码是否使用了 Moodify 已有的 case、measurement、evidence 和 authority 语言？
3. 上游与下游是否对同一对象具有一致认识？
4. 是否出现第二份状态、schema、规则或 orchestration truth？
5. 成功、失败、重试和恢复在每一层是否表达同一事实？
6. 新产物能否进入 Asset Loop，而不是停留为孤立文件？
7. 未来维护者能否从 contract、测试和决策记录理解为什么这样设计？

## 7. 失败处置

发现局部功能破坏整体一致性时：

1. 不否定局部实现中已经验证的技术价值；
2. 阻止其直接成为 canonical；
3. 将其隔离为 experimental operator 或 execution adapter；
4. 找出缺失的 entity、relation、contract 或 evidence link；
5. 优先通过窄适配器接入现有权威；
6. 若确需改变本体，提交显式架构修订与迁移方案；
7. 保存冲突案例，使下一次设计不再重复同一概念债务。

## 8. 与 ME-001、ME-002 的关系

```text
ME-001：这项能力是否从 Moodify 的起源和真实责任中产生？
ME-002：关于这项能力的声明是否已经被足够证据证明？
ME-003：它进入系统后，是否仍与整个 Moodify 属于同一个世界？
```

三条约束分别保护方向、真实性和整体性，不能互相替代。

## 9. 激活条件

ME-003 从 `PROPOSED` 变为 `ACTIVE` 前，需要：

- 用 Whole Impact Record 审查一个真实跨层变更；
- 至少识别一次局部正确但整体不完整的缺口；
- 验证审阅能够复用现有 authority，而不是创造新的治理系统；
- 再决定哪些字段应进入任务模板、PR 模板或自动架构检查。
