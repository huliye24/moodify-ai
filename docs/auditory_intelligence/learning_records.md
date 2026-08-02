# 学习记录（DSK-MFY-AUDITORY-INTELLIGENCE-RECLASSIFICATION-001）

## 什么是学习记录

`LearningRecord` 把一个案例的全部可学习证据绑定在一起：

- 源哈希与候选 ID 列表；
- before/after 扫描引用；
- 观察、干预、比较、人耳评估引用；
- 成对偏好（pairwise_preferences.jsonl）；
- 候选结果（candidate_outcomes.jsonl，接受/拒绝/中性/失败/过度处理）；
- 失败标签、标注质量；
- 权利元数据与训练资格；
- 排除原因、审查状态、提交者与时间。

## 工作流

```text
build  →  review  →  commit | exclude
```

- **build**：从案例目录聚合全部证据；证据缺失 → 失败关闭
  （LEARNING_RECORD_INCOMPLETE）。
- **review**：记录权利审查（rights_review.json）并计算资格；资格默认
  UNKNOWN/PENDING_REVIEW。
- **commit**：仅审查后可提交；ELIGIBLE → COMMITTED，其他 → EXCLUDED
  （原因显式）。

## 案例布局（09_learning）

```text
09_learning/
├── learning_record.json
├── rights_review.json
├── training_eligibility.json
├── pairwise_preferences.jsonl
├── candidate_outcomes.jsonl
└── learning_manifest.json
```

## 规则

- 案例未提交学习记录前不算"学习完成"；
- 生产案例 COMPLETED 但学习 EXCLUDED 是合法的，原因必须显式；
- 训练导出只包含显式 ELIGIBLE 记录。
