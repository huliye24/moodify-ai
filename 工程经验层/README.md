# Moodify 工程经验层

## 定位

工程经验层把经过审视的软件建造理念转译为 Moodify 可执行、可审计、可修订的工程约束。

它回答的不是“我们相信什么”，而是：

```text
理念来源
  -> 工程命题
  -> 适用范围
  -> 可判定约束
  -> 验证证据
  -> 失败处置
  -> 后续修订
```

工程经验层不是新的产品身份、运行时子系统或权威状态机。它不直接控制
`ProductionCase`，不定义测量真值，也不取代人工对产品起源和架构方向的最终权威。

## 权威边界

本层服从仓库既有权威顺序：

1. 当前明确的人类任务；
2. 根 `AGENTS.md`；
3. 当前 canonical constitution 与 architecture；
4. 已验证的主线行为和测试；
5. 工程经验层中的约束；
6. 实验、历史与外部哲学材料。

外部材料 `E:\软件建造的哲学` 是思想来源，不是仓库运行依赖，也不会因被引用而自动获得 canonical authority。

## 约束进入条件

一条理念只有同时满足以下条件，才能进入约束注册表：

- 能指出它保护的 Moodify 起源、对象、责任或证据关系；
- 能明确适用范围和不适用范围；
- 能转写为可以检查的问题、测试、门禁或审阅证据；
- 能说明违反时如何阻断、降级、隔离或记录；
- 不创建第二套 authority、lifecycle、metric truth 或 orchestration；
- 允许被生产证据修订，而不是成为不可证伪的口号。

## 约束状态

- `PROPOSED`：完成转译，尚未进入日常工程门禁；
- `ACTIVE`：已被当前架构采纳，并有明确检查方法；
- `EXPERIMENTAL`：只约束指定实验范围；
- `SUPERSEDED`：被新版本替代，保留历史；
- `RETIRED`：证据表明不再适用，保留撤销理由。

## 当前内容

- [约束注册表](CONSTRAINT_REGISTRY.md)
- [ME-001：起源先于功能](constraints/ME-001_ORIGIN_BEFORE_FEATURE.md)
- [ME-002：证据门控发展](constraints/ME-002_EVIDENCE_GATED_DEVELOPMENT.md)
- [ME-003：整体一致性与同源派生](constraints/ME-003_WHOLE_SYSTEM_COHERENCE.md)

## 渐进原则

每次只吸收少量理念。先完成语义转译和人工审阅，再决定是否增加自动检查。不得把整套哲学文档一次性复制为规则，也不得为了形式完整批量制造无验证价值的约束。
