# Moodify Studio Workspace v2 — MVP 产品边界

**状态：已冻结**
**版本：Scope 1.0**
**冻结日期：2026-07-24**
**对应执行步骤：P0 / Step 1**

## 1. MVP 目标

Moodify v2 MVP 的目标不是增加一个新的音频增强按钮，而是把现有分析、诊断、DSP、质量门和交付能力组织成一个可持续迭代的音乐项目工作流。

MVP 必须跑通以下闭环：

```text
创建项目
→ 保存 Creative Brief
→ 执行音频诊断
→ 生成 Treatment Plan
→ 处理并产生候选版本
→ Judge 质量审查
→ 人工批准或退回
→ Final 归档
```

## 2. MVP 必须包含

### 2.1 项目系统

- 创建、读取和更新 AudioProject。
- 保存原始音频、项目名称、目标、状态和当前版本。
- 一个项目可跨多次运行持续维护，而不是一次性 `process(audio)`。

### 2.2 Creative Brief

- 保存 `goal`、`preserve`、`avoid`、`platform` 和 `reference`。
- Brief 是诊断、方案设计、处理和审查的共同输入。
- Brief 可以修改，但修改必须留下更新时间和版本记录。

### 2.3 工作线程状态

- 支持 Producer、Analyst、Designer、Worker、Judge、Archive 六类逻辑角色。
- 角色在 MVP 中实现为可测试的工作流节点，不要求每个角色运行独立大模型。
- 每个线程记录状态、输入、输出、错误、开始时间、结束时间和重试次数。

### 2.4 Treatment Plan

- 至少支持 Natural Repair 和 Release Ready 两类结构化方案。
- 每个方案记录目标、动作、理由、风险、保护项和预期指标。
- 首版允许规则模板生成；LLM 只作为后续可插拔实现。

### 2.5 音频版本

- 支持原始版本、候选版本、分支版本和 Final。
- 每个版本必须记录父版本、音频路径、处理方案、参数、报告和创建原因。
- 回退通过创建新版本实现，不删除或覆盖历史音频。

### 2.6 Judge 与人工审批

- Judge 检查 clipping、失真、响度、动态损失、MRS/proxy 和现有安全门。
- Judge 必须输出 `pass`、`reject` 或 `reprocess` 及结构化理由。
- 没有人工 ApprovalDecision 的版本不得标记为 Final。

### 2.7 比较与归档

- 至少支持两个版本的指标、处理记录和试听路径比较。
- Final 归档必须包含原始音频引用、版本历史、Treatment Plan、处理参数、Judge 结果、人工决定和交付文件。

### 2.8 API

MVP 必须提供以下能力的 API：

- Project CRUD；
- Brief 创建与更新；
- Thread 状态查询；
- Version 创建、列表、详情、分支与回退；
- Version Compare；
- Human Approval；
- Workflow Run / Resume。

## 3. MVP 明确不包含

以下内容不进入本轮 MVP：

- 用户注册、登录、权限计费和订阅系统；
- 多租户隔离和企业组织管理；
- 云 GPU 自动扩缩容与跨区域调度；
- 实时多人协作编辑；
- 移动端应用；
- DAW 插件、VST/AU 插件；
- 自研大模型训练或音频基础模型训练；
- 对 Spotify、Apple Music、YouTube 的自动发布；
- 复杂数据库集群和微服务拆分；
- 无人监督的全自动 Final 交付；
- 任意 stem 级跨版本合并界面；
- 生产级高并发和商业 SLA。

这些能力可以登记为 Phase 2/3 候选项，但不得阻塞 MVP。

## 4. 技术约束

- 优先复用现有 `StudioProject`、`OperatorJob`、`CandidateVersion`、质量门、Delivery Record 和 Craft Chain。
- 新 Workspace 层不得破坏现有 `/studio/*` 与 `/operator/*` 接口。
- 首版存储继续使用 JSON/JSONL，但通过 Repository 边界隔离，方便后续迁移数据库。
- 音频产物只新增，不覆盖历史版本。
- MRS 不可用时允许 proxy 降级，但必须在结果中明确标记。
- 所有状态转换、版本血缘和审批门禁必须有自动测试。

## 5. MVP 完成定义

只有同时满足以下条件，MVP 才可宣布完成：

1. 使用真实音频创建项目并保存 Brief。
2. 可从项目启动 Diagnosis、Design、Process、Judge 工作流。
3. 至少生成两个可追踪候选版本。
4. 可查看版本差异和每个版本的血缘、参数及报告。
5. Judge 拒绝时可以退回处理节点，且不会无限重试。
6. 只有人工批准后的版本才能成为 Final。
7. 服务重启后项目、线程、版本和审批状态保持一致。
8. 当前两轨歌曲完成一次从项目创建到 Final 归档的黄金路径测试。
9. 所有 P0 测试通过，无未处理的致命风险。
10. 操作者可依据运行手册独立完成一次完整流程。

## 6. 范围变更门禁

冻结后，新增需求必须先登记到“决策与风险”，并回答：

1. 是否是上述 MVP 完成定义的必要条件？
2. 是否可以推迟到 Phase 2/3？
3. 是否会改变数据模型、历史兼容或 Final 门禁？
4. 增加多少预计人日和测试成本？

只有明确影响 MVP 闭环或数据安全的需求可以进入当前范围。其他需求进入后续待办，不直接插入开发主线。

## 7. 首个验收样本

首个黄金路径样本使用：

`pre-music/2026-07-24_1441_split_by_lalalai`

现有 Moodify 分轨处理产物：

`pre-music/2026-07-24_1441_split_by_lalalai/moodify_post_v1`

该样本用于验证项目创建、版本登记、Judge、人工审批和 Final 归档，不作为所有音乐类型的质量代表。

## 8. 冻结结论

Moodify v2 MVP 的产品范围正式冻结为：

> 项目系统 + Creative Brief + 工作线程状态 + Treatment Plan + 音频版本树 + Judge + 人工审批 + 比较归档 + API。

在 MVP 黄金路径跑通前，不开发账户、云端商业化、真实多 Agent 自治、模型训练或自动发布能力。
