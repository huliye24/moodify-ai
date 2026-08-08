# Moodify 能力—证据—缺口矩阵｜D1-03

**记录日期：2026-07-30**  
**任务：D1-03｜建立能力—证据—缺口清单**  
**当前代码状态：`v2.0.0-mvp-dirty`**  
**门禁结果：G3 PASS**

## 1. 状态口径

- `IMPLEMENTED`：代码、配置或接口存在，但没有当前脏工作区的本轮运行证据；
- `VERIFIED`：存在可定位的当前环境或封存基线测试/运行证据，且相关核心文件未发现本轮工作区修改；
- `PRODUCTION-PROVEN`：在有权使用的真实生产材料上重复运行，并经过专业、响度匹配的听感验证。

补充规则：

1. 封存基线证据可以支持`VERIFIED`，但必须明确它验证的是`v2.0.0-mvp`，不是所有未提交修改；
2. 当前被修改或新增的处理、MRS、Runtime代码，在D1-04重新运行前最多标记为`IMPLEMENTED`；
3. 测试通过不等于`PRODUCTION-PROVEN`；
4. 当前没有任何一项核心声音能力达到`PRODUCTION-PROVEN`。

## 2. 能力矩阵

| 编号 | 能力 | 当前状态 | 实现证据 | 验证证据 | 当前限制 | 生产验证影响 |
|---|---|---|---|---|---|---|
| C01 | 音频导入与格式检查 | IMPLEMENTED | `v01_analyzer.py`、`v01_pipeline.py`、Workspace sources接口 | v2封存Manifest及历史测试文件 | Analyzer和类型文件存在未提交修改；当前HEAD未冒烟 | P0：无法确认5首输入在当前代码下稳定读取 |
| C02 | 声学诊断与指标提取 | IMPLEMENTED | `diagnosis/`、`features/`、`reality_metrics.py`、`mrs_robust.py` | 历史Treatment和Inspector报告 | 频段、感知指标及鲁棒评分代码正在变化；旧报告不能代表当前结果 | P0：所有处理与Judge依赖诊断可信度 |
| C03 | ProductionSpec前身：Creative Brief | VERIFIED | `domain/creative_brief.py`、Workspace API | v2 179/179封存证据；`test_creative_brief.py`、API测试 | 仍使用Creative Brief命名；尚未形成正式ProductionSpec及权利字段 | P1：不阻塞声音冒烟，但阻塞公司级稳定合同 |
| C04 | Treatment Plan与方案设计 | VERIFIED | `domain/treatment_plan.py`、`services/designer.py` | `test_treatment_plan.py`、`test_designer_service.py`及v2封存证据 | 计划结构已验证，处理建议是否产生更好声音尚未证明 | P1：可支撑流程，不能证明工艺有效 |
| C05 | DSP与声音处理 | IMPLEMENTED | `processing/`、`v01_pipeline.py`、`services/dsp_worker.py` | 历史Treatment/Inspector/Calibration产物 | operators、spectral_chain及多项新处理模块处于未提交状态；无当前冒烟 | P0：本周真实验证的核心生产能力 |
| C06 | 候选版本与版本血缘 | VERIFIED | `domain/audio_version.py`、`services/version_compare.py`、Workspace store/API | v2黄金路径：2候选、lineage PASS；版本API测试 | 当前持久化Workspace项目目录为空；证据主要来自Manifest和JUnit | P1：流程成立，需要在新运行中重新产生可查项目树 |
| C07 | MRS与技术质量门 | IMPLEMENTED | `mrs_engine.py`、`mrs_adapter.py`、`mrs_robust.py`、`diagnosis/quality_gate.py` | MRS历史报告和测试文件 | 历史Gate accuracy 9.1%；pseudo-MRS相关性约0.19；当前MRS代码未冒烟 | P0：不能让不可靠分数单独决定通过 |
| C08 | Judge结构化判断 | VERIFIED | `services/judge.py`、GateResult及Judge线程 | v2黄金路径Judge披露PASS、相关v2测试 | 已证明技术门工作流，不等于技术门与真实听感一致 | P1：可以记录判断，但需与人工听感并列使用 |
| C09 | 人工批准与Final归档 | VERIFIED | `domain/approval.py`、`services/archive.py`、Workspace approval API | v2 Manifest：approval fixture和archive integrity PASS；审批测试 | 封存证据中的人工批准是自动验收fixture，不是专业制作人真实选版 | P1：流程门禁可靠，艺术判断仍需真实人员完成 |
| C10 | Runtime、Queue与失败恢复 | IMPLEMENTED | `queue.py`、`runtime_failures.py`、`supervisor.py`、Workspace retry | 历史Runtime测试与v2 failure recovery测试 | Runtime配置、Supervisor、Cloud Worker和关键测试存在未提交修改 | P0：D1-04必须确认最小运行没有环境或队列回归 |
| C11 | Report、Delivery与证据归档 | IMPLEMENTED | `report.py`、`pdf_report.py`、Operator Report、Delivery模块 | 历史报告目录及封存Manifest | 当前报告来自多个历史版本；缺统一的本周运行ID证据包 | P1：不阻塞处理本身，但阻塞可审计交付 |
| C12 | Craft Library与工艺写回 | IMPLEMENTED | `craft_memory.py`、`craft_evidence.py`、`craft_selector.py`、`craft_processes.py` | 历史Craft/Data Loop测试与记录 | craft_presets/processes及新Evidence模块未提交；旧Treatment汇总不一致 | P1：不应把错误或低置信度结果写入工艺记忆 |
| C13 | Stem级与多轨处理 | IMPLEMENTED | Workspace注册样本、`pre-music`分轨项目、DSP Worker | v2注册样本封存证据 | 证明了两轨项目流转，不代表复杂stem平衡达到专业标准 | P2：本周先验证全链，不扩展stem范围 |
| C14 | 响度匹配与专业听感验证 | IMPLEMENTED | `listening.py`、评分卡模板、`after_matched.wav`资产 | 3条实际完成Treatment反馈；历史Listening报告 | 反馈仅3/27；评分卡大多为空；未完成有权真实材料上的重复盲听 | P0：这是从“功能成立”进入“声音成立”的关键缺口 |

## 3. 状态汇总

| 状态 | 数量 | 解释 |
|---|---:|---|
| VERIFIED | 5 | 主要是Workspace v2结构、版本和审批能力 |
| IMPLEMENTED | 9 | 声音、MRS、Runtime、报告和Craft需当前冒烟或真实验证 |
| PRODUCTION-PROVEN | 0 | 尚无能力满足真实材料、重复运行、专业盲听三项条件 |

这不是对系统价值的否定。它说明Moodify已经拥有相对完整的工业骨架，但当前阶段的核心任务确实应从“继续增加模块”切换到“证明现有生产能力”。

## 4. 已验证能力与声音能力的分界

### 已经较强的部分

- 项目对象和Creative Brief；
- Treatment Plan结构；
- 候选版本和不可覆盖的血缘关系；
- Judge到人工审批再到Final归档的门禁；
- 封存测试和验收证据的组织方法。

这些能力回答：

> 一次音乐处理任务能否被组织、追踪、审查和归档？

### 尚未证明的部分

- 当前处理代码是否稳定运行；
- 处理后的声音是否在响度匹配后更好；
- MRS和技术门是否与专业人员判断一致；
- 不同曲风和声音问题能否稳定达到最低交付标准；
- 失败结果是否会被可靠拒绝而不污染Craft Library。

这些能力回答：

> Moodify组织起来的生产线，是否真的持续生产更好的声音？

## 5. 缺口优先级

缺口按“是否阻塞真实生产验证”排序，而不是按开发兴趣排序。

### P0｜必须先解决

| 排名 | 缺口 | 当前证据 | 本轮动作 |
|---:|---|---|---|
| 1 | 当前脏工作区尚未通过最小冒烟 | 多个处理、Runtime和测试文件被修改或新增 | D1-04运行Core、Runtime和Workspace最小测试 |
| 2 | 验证音频缺权利确认 | 7类MHP-026源文件均未找到权利元数据 | 荣景文川确认5首仅用于内部验证 |
| 3 | Treatment汇总与实际文件冲突 | summary为30/6，实际为27/3 | 从实际文件重建汇总并查明3个缺失记录 |
| 4 | MRS不能可靠代表听感 | 历史Gate 9.1%，偏好相关性约0.19 | MRS只作技术证据，不作单独放行依据 |
| 5 | 专业听感覆盖不足 | 实际完成反馈3条，评分卡大多为空 | 对5首执行响度匹配盲听并保留失败 |

### P1｜完成首轮真实运行后处理

| 排名 | 缺口 | 下一步 |
|---:|---|---|
| 6 | ProductionSpec还没有公司级合同 | 加入素材权利、参考维度、保护项、禁止项和验收条件 |
| 7 | 报告和证据分散于多个历史目录 | 为每轮验证生成独立run_id和Manifest |
| 8 | Craft写回缺少置信度门禁 | 只有人工批准且证据完整的结果才能写回 |
| 9 | Workspace黄金项目树当前不驻留 | 新建一次隔离的验证项目并保留完整树 |

### P2｜本周不做

- 扩展新的Preset或模型；
- 扩展复杂stem制作能力；
- 重做创作者前端；
- 采购硬件；
- 建设发行、人才或艺人运营功能。

## 6. D1-04最小冒烟范围建议

为了控制在一小时内，D1-04建议只运行以下四组：

1. Core基础处理测试：`test_v01_analyzer_diagnostics_exporter.py`及与当前新增声学模块直接相关的单测；
2. Runtime关键链：Queue、Failure、Real Audio、Operator Job和Product Integration；
3. Workspace v2关键链：项目、版本、审批、失败恢复和Golden Path；
4. CLI只读检查：`moodify presets`和Runtime health/help入口。

若任一组失败，记录原始失败并停止扩大范围；D1-04不承担修复工作。

## 7. G3验收

| 检查项 | 结果 | 证据 |
|---|---|---|
| 每项能力只有一个当前状态 | PASS | 第2节 |
| 每项状态有代码、测试、产物或报告证据 | PASS | 第2节实现与验证证据列 |
| 每项至少一个当前限制 | PASS | 第2节限制列 |
| 明确尚未达到PRODUCTION-PROVEN的能力 | PASS | 第3、4节 |
| 缺口按阻塞真实生产验证程度排序 | PASS | 第5节P0/P1/P2 |

**G3结论：PASS。D1-03完成。下一步可以进入D1-04最小冒烟测试。**

