# Moodify Power Reward Model v0.1 - 研究状态

## 当前状态

本文件包是一套前瞻性项目规格，不是已完成模型报告。尚未产生训练结果、模型权重或商业性能声明。

## 最先执行的任务

1. 冻结力量感标注语言；
2. 选择 20-24 首曲目开展小规模试点；
3. 验证响度匹配流程和片段长度；
4. 检查听者一致性；
5. 一致性达到最低门槛后再扩张数据。

## 关键科学边界

- 力量感不等同于响度；
- 成对偏好是特定任务和上下文下的相对判断，不是主观意识的证明；
- 偏好模型回答“人更可能选择什么”，不能单独证明声学因果；
- v0.1 不需要完整强化学习，先完成奖励模型验证。

## 文件说明

- `Moodify_Power_Reward_Model_v0.1_Project_Spec.pdf`：正式阅读版；
- `Moodify_Power_Reward_Model_v0.1_Project_Spec.docx`：可编辑版；
- `Moodify_Power_Reward_Model_v0.1_Project_Spec.md`：Markdown 母稿；
- `Power_Preference_Annotation_Guideline.md`：标注说明；
- `power_pair_annotation_template.csv`：标注记录模板；
- `power_pair_record_schema_v0.1.json`：数据结构；
- `PWRM_v0.1_Experiment_Package.yaml`：首个实验包。
