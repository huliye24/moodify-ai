# DSK-MFY-DECISION-INTELLIGENCE-011｜制作决策智能训练地基 v0.1

**计划日期：** 2026-08-03  
**执行 Worker：** DeepSeek  
**最终 Judge：** Codex / 授权用户  
**依赖：** 010已形成可读HANDOFF；否则HOLD  
**执行窗口：** 010之后串行；不足时顺延，不并行

## 1. 唯一目标

把每次制作从“输入—参数—输出”升级为可训练的决策episode：

```text
Context -> Evidence -> Decision -> Candidate Outcomes
        -> Owner Preference -> Limitations -> Provenance
```

建立数据合同、确定性builder、防泄漏split、CPU离线baseline和晋级门。
不训练生成音频模型，不做在线强化学习，不让模型替代Owner。

## 2. 必读事实源

完整读取：

```text
E:\moodify\docs\tasks\deepseek\DSK-MFY-DECISION-INTELLIGENCE-011\00_TASK_ORCHESTRATION.md
E:\moodify\docs\tasks\deepseek\DSK-MFY-DECISION-INTELLIGENCE-011\02_CODEX_ACCEPTANCE_MATRIX.md
E:\moodify\docs\tasks\deepseek\DSK-MFY-DECISION-INTELLIGENCE-011\03_PRINCIPLE_SEED.md
E:\moodify\docs\tasks\deepseek\DSK-MFY-IDENTITY-CORE-010\HANDOFF.md
E:\moodify\moodify_runtime\learning_store.py
E:\moodify\moodify_runtime\learning_surface.py
E:\moodify\moodify_runtime\craft_memory.py
E:\moodify\moodify_runtime\listening.py
E:\moodify\scripts\v01_create_treatment_record.py
E:\moodify\scripts\v01_update_treatment_feedback.py
E:\moodify\scripts\v01_aggregate_treatment_records.py
E:\moodify\docs\treatment_records\README.md
E:\moodify\reports\listening_probe\human_label_taxonomy.md
E:\moodify\reports\listening_probe\reviewer_bias_risk_map.md
E:\moodify\science\Moodify_Power_Reward_Model_v0_1_Package\README.md
E:\moodify\docs\decisions\ADR-004-evidence-before-superiority-claims.md
```

检查适用AGENTS.md、Git/dirty状态、Python依赖、样本权利和现有schema。所有
既有修改/数据属于用户，只读审计；不得整理、修正或回填历史记录。

## 3. 允许范围

```text
E:\moodify\science\Moodify_Decision_Intelligence_v0_1_Package\
E:\moodify\docs\architecture\DECISION_INTELLIGENCE_ARCHITECTURE.md
E:\moodify\docs\tasks\deepseek\DSK-MFY-DECISION-INTELLIGENCE-011\
E:\moodify\outputs\deepseek_validation\DSK-MFY-DECISION-INTELLIGENCE-011\
```

禁止修改生产Core/Runtime/Bridge/DSP/MRS/Preset、008—010实现、历史Treatment
Records和真实资产；禁止联网、新依赖、GPU要求、migration和Git操作。只通过
只读adapter读取现有数据；不复制音频/歌词正文进入训练集。

## 4. Stage 0｜学习命题、权利与数据合同（75分钟）

编码前完成：

- `00_IMPLEMENTATION_AUDIT.md`：现有数据数量、完整性、冲突和可用性；
- `DECISION_EPISODE_CONTRACT.md`：Context/Evidence/Decision/Outcome/Human/Provenance；
- `LABEL_AND_UNCERTAINTY_CONTRACT.md`：选择/拒绝/平局/不确定/未评审；
- `PRIVACY_RIGHTS_RETENTION.md`：权利基础、去标识、删除、派生数据边界；
- `LEAKAGE_AND_SPLIT_CONTRACT.md`：按work/creator/project分组，禁止同源跨split；
- `MODEL_CLAIM_AND_PROMOTION_GATE.md`：offline-only、shadow、human approval；
- `STAGE_0_GATE.md`。

必须区分：记录缺失、人工未评审、人工不确定、模型不确定和冲突标签。
不能把空字段当负样本，不能把MRS或技术Gate当人类偏好标签。

## 5. Stage 1｜DecisionEpisode Builder（105分钟）

在隔离science package实现严格schema、只读adapters和CLI：

```text
python -m moodify_decision_data audit ...
python -m moodify_decision_data build ... --output-dir NEW_DIR
python -m moodify_decision_data validate ...
```

要求：稳定episode ID；源记录/资产哈希；schema/version；证据引用；动作与参数；
候选结果；Owner显式标签与理由；限制；生成器版本。默认只输出JSONL/manifest/
dataset card，不复制媒体正文。坏记录进入rejected ledger，不静默丢弃。

测试：重复记录、哈希冲突、缺标签、平局、不确定、未知字段、Unicode、路径
逃逸、顺序扰动、重复构建、源数据不变、敏感内容泄漏。

## 6. Stage 2｜防泄漏数据集与CPU离线基线（105分钟）

1. group split按work_id优先，存在creator/project时建立更严格隔离；记录随机种子。
2. 生成train/validation/test及split audit；重复/近重复不得跨split。
3. 只做可解释CPU基线：majority/dummy、简单规则、可选线性分类/排序；若现有
   数据不足，使用合成fixture验证代码并明确`DATA_NOT_READY`。
4. 指标至少含coverage、abstention、balanced accuracy/F1（适用时）、pairwise
   accuracy、calibration（样本足够时）；同时按作品/曲风/creator分组检查。
5. baseline不能读取评审后字段预测评审结果；执行target leakage scan。
6. 不做在线RL、不自动执行DSP、不将baseline接入生产路由。

## 7. Stage 3｜治理、验证与路线（75分钟）

1. 双构建确定性、split重放、拒绝账本、至少12类失败注入。
2. package测试、Ruff、Mypy、CLI smoke；记录未运行项。
3. `DATASET_CARD.md`、`BASELINE_REPORT.md`、`BIAS_AND_FAILURE_REPORT.md`、
   `MODEL_PROMOTION_PROTOCOL.md`、`VALIDATION_REPORT.md`、`PROGRESS.md`、`HANDOFF.md`。
4. 路线只允许：规则/Codex记录→模仿学习→偏好学习→离线策略评估→shadow→
   受约束建议；任何自动执行必须是未来独立任务并重新授权。
5. 明确当前数据是否足以训练；若不足，给出缺口和最小采集计划，不生成虚假模型。

## 8. P0门禁

必须成立：Owner标签不可伪造；无同源split泄漏；无媒体正文复制；源数据只读；
未评审不等于负样本；MRS不等于偏好；baseline不进生产；结果可重放；隐私/
权利/删除链明确；不宣称模型已具备制作判断能力。

立即停止：010无HANDOFF、Stage 0未PASS即编码、需要修改生产代码/历史数据、
需联网/新依赖、发现真实数据无权用于训练、target leakage无法排除、样本不足
却继续拟合并宣称效果、范围外写入或既有用户修改被还原。

最终只能`READY_FOR_CODEX_REVIEW / DATA_NOT_READY / REWORK / HOLD`；DeepSeek
不得宣布生产模型完成、可自主决策或优于人工。

