# ADR-MFY-002｜Ocean Listen 听觉传感器吸收桥

**状态：** 已采纳（2026-08-08）
**领域：** WSE（hear + represent 层）
**任务包：** DSK-MFY-OCEAN-ABSORPTION-001（补丁包 06）

## 背景

外部开源工具 Ocean Listen（上游 ennisaaaaaaaa-stack/ocean-listen，pin `928dfba6`）
提供浅/深两级音频分析（预分类、stem MIDI、逐音符 RMS 动态、人声特征、歌词、
结构化 JSON 报告）。Moodify 需要把这类"听音"能力接入，但必须保持
**传感器不是权威**的边界：它不批准艺术决策、不干预、不越权转换。

## 决策

> Ocean Listen 以隔离的听觉传感器适配器接入 case 生命周期的
> ANALYZING 阶段；所有输出作为证据注册，质量门决定证据是否可作为
> 分析材料并入，但任何情况下都不能由传感器产生状态推进。

### 具体决策

1. **落点**：桥接代码入 `src/moodify/adapters/auditory/ocean_listen/`
   （隔离适配器，不并入核心命名空间；零运行时依赖）。
2. **状态机**：`CaseState` 新增 `ANALYZING`（SPECIFIED → ANALYZING → ANALYZED），
   传感器在 ANALYZING 窗口内执行；`case analyze` 默认不启用传感器
   （config `enabled: false`），显式 `--sensor ocean` 或配置开启才运行。
3. **上游 pin**：`third_party/ocean-listen/`（git clone + detach 928dfba6，
   不入 git）；21 文件不可变快照 `third_party/ocean_listen_snapshot/` 入库 +
   `MOODIFY_VENDOR_MANIFEST.json`（per-file sha256）入库；`allow_unreviewed_commit`
   默认 false 强制 pin 校验。
4. **证据注册**：`<case_root>/06_ocean_listen/evidence_registry.json`
   （schema `moodify.evidence-registry/1.0`，6 类 artifact × 10 字段），
   原子写 + 确定性 run_id 幂等（绝不覆盖既有证据）。
5. **语义修正**（包内 note_evidence 强制）：velocity 是置信度代理不是响度；
   RMS 是声能证据；绝不删 note（全部候选 + evidence_score）；
   分类/音色/人声部分标签标 experimental；不推广性别推断；
   NetEase 歌词非默认生产依赖。
6. **质量门**：gate FAIL 的证据仍注册留痕，但 observation **不并入**
   case.analysis，warnings 附加；sensor 从不触发 PLANNED/TECHNICALLY_VALIDATED。

### 覆盖范围

Ocean Listen 覆盖 Moodify 的 **hear + represent** 层。judge/intervene/verify/learn
完整闭环仍由 Moodify 权威（人耳审批、对比验证、学习记录）控制。

## 后果

正面：

- 外部听音能力可插拔接入，证据链完整（源哈希/配置哈希/上游 commit/artifact 哈希）；
- 状态机显式表达"分析进行中"（ANALYZING），不再是一步瞬态；
- 能力注册表声明 quarantine 语义，防止未来误用。

负面/风险：

- vendored 上游依赖 pin 纪律（更新 pin 必须重新评审 + 更新 manifest）；
- 双跑/重跑成本（幂等靠确定性 run_id，重跑不覆盖但会消耗磁盘）；
- 语义修正依赖 mapper/note_evidence 代码约束，无强制机制防未来绕过。

## 回滚

- 删除 `06_ocean_listen/` 证据目录与 `--sensor` 接线即可回到无传感器路径；
- 状态机回退：`ALLOWED[SPECIFIED]={ANALYZED}`、移除 ANALYZING 与 begin_analysis
  （需要同步 cmd_case_analyze）；
- vendored 上游删除 third_party/ocean-listen + 快照 + manifest；config 默认
  enabled:false 已保证不启用即零影响。

## 被拒方案

- **直接 import Ocean 进核心**：破坏依赖隔离，拒绝；
- **传感器自行推进状态**：违反 authority 边界，拒绝；
- **更新 pin 到未评审 commit**：`allow_unreviewed_commit` 默认 false 强制拒绝；
- **传感器输出直接并入 analysis 无门控**：gate 是必须的，拒绝。

## 参考

- `docs/operator/OCEAN_LISTEN_RUNBOOK.md`（启停/基准计划/已知局限）
- `docs/technical/OCEAN_LISTEN_FIELD_MAPPING.md`（字段映射）
- `MOODIFY_VENDOR_MANIFEST.json`（上游 pin 与 per-file 哈希）
- 上游许可证备份：`docs/third_party/ocean-listen/`
