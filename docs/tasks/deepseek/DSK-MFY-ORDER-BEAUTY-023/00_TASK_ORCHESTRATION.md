# DSK-MFY-ORDER-BEAUTY-023｜城门：建立任务与变更的单一秩序

**计划日期：** 2026-08-02  
**执行 Worker：** DeepSeek  
**任务所有者与最终 Judge：** Codex / 授权用户  
**依赖：** 022 ACCEPT  
**建议投入：** 5–10 小时  
**任务状态：** PLANNED

## 1. 任务意图

城墙的秩序来自有限、明确、可守的城门。Moodify 当前的问题不是没有记录，而是计划、handoff、验收文档和工作区状态同时发声。高级秩序要求“一个事实只从一个入口改变”，其他视图由它派生。

数据依据：分析快照记录 22 个正式任务包、已开始任务验收率 57.1%、4 处状态来源冲突、55 个已跟踪修改和 140 个未跟踪条目。数字属于带时间戳快照；任务执行必须同时保留快照与实时状态，不能用新扫描覆盖历史事实。

## 2. 核心目标

1. 建立机器可读、追加式的任务账本，形成唯一当前状态；
2. 定义 orchestration、handoff、acceptance 的职责与冲突优先级；
3. 将工作区变更分类为产品代码、测试、文档、分析产物、生成物和未知项；
4. 给每个变更桶添加归属、验证状态、回滚边界和下一动作；
5. 让常态化分析从账本生成状态报告，而不是重复猜测目录含义。

## 3. 允许范围

```text
docs/tasks/
project_analytics/
tools/project_governance/
outputs/deepseek_validation/DSK-MFY-ORDER-BEAUTY-023/
```

原则上只读产品代码与测试代码。禁止移动、删除、提交或丢弃任何现有工作区变更；禁止改写历史验收文档；禁止自动把“存在 acceptance 文件”等同于所有后续状态都正确。

## 4. 状态模型

唯一状态集合：

```text
PLANNED -> IN_PROGRESS -> READY_FOR_REVIEW -> REWORK -> ACCEPTED
                         -> HOLD
```

- orchestration：描述授权范围与计划，不证明完成；
- handoff：描述执行方当前交付状态，不证明验收；
- acceptance：由 Judge 写入的验收事实；
- ledger：根据有序事件计算当前状态，不覆盖历史事件；
- 冲突必须显式暴露，禁止“最后修改时间获胜”。

## 5. 执行阶段

### Stage A｜建立追加式任务账本

- 定义版本化 schema：task_id、event_id、event_type、actor、timestamp、source、evidence、supersedes；
- 从现有任务目录导入事件，保留无法判定项；
- 对快照中的 4 处冲突逐项生成 reconciliation 记录；
- 任何修正通过新增事件完成，不修改历史事件。

### Stage B｜工作区分桶

- 生成带时间戳 inventory，不移动文件；
- 每个条目记录 tracked/untracked、area、bucket、owner、validation、risk、recommended_action；
- 未知项保持 `UNKNOWN`，不得自动删除或忽略；
- 目录型 untracked 条目需展开文件数，解决“一个条目包含多个文件”的口径限制。

### Stage C｜派生视图与门禁

- 从账本生成任务总表、冲突表、在制品表和待验收表；
- 从 inventory 生成工作区分桶表与高风险清单；
- 增加校验：非法状态跳转、重复 event_id、缺失证据、多个当前状态、已验收后被静默降级；
- 更新 `project_analytics` 采集器，引用账本并保留向后兼容说明。

### Stage D｜治理节奏

- 定义每日轻量检查、每周状态复核、阶段结束 reconciliation；
- 同时在制品超过约定上限时只告警，不自动关闭任务；
- 产出“下一任务包是否可开启”的可审计判断。

## 6. P0 验收门槛

- 所有正式任务包恰好有一个派生当前状态，冲突数为 0 或明确 HOLD；
- 历史文件未被改写，修正全部追加；
- 55/140 快照口径与实时 inventory 分开显示；
- 当前工作区每个变更都有桶或显式 UNKNOWN；
- 未发生删除、移动、stash、clean、reset、checkout、commit 或 push；
- 同一输入连续生成两次，账本视图字节一致（时间戳元数据除外且需隔离）。

## 7. 停止条件

若需要替用户决定未知文件归属、删除生成物、修改历史 acceptance、改变产品代码，立即停止并提交 `SCOPE_CHANGE_REQUEST.md`。最终状态只能是 `READY_FOR_CODEX_REVIEW / REWORK / HOLD`。

