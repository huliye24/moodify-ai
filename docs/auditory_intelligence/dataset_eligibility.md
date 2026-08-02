# 数据集资格（DSK-MFY-AUDITORY-INTELLIGENCE-RECLASSIFICATION-001）

## 资格状态

ELIGIBLE / INELIGIBLE / PENDING_REVIEW / RESTRICTED_INTERNAL_RESEARCH / UNKNOWN

**默认 UNKNOWN 或 PENDING_REVIEW，绝不默认 ELIGIBLE。**

## 权利元数据（rights_review.json）

- audio_origin / rights_holder
- processing_authorization
- research_use_authorized / model_training_authorized
- derivative_data_authorized / commercial_training_authorized
- retention_policy / consent_reference / jurisdiction_notes
- reviewed_by / reviewed_at

## 资格计算

- 任一训练相关授权显式否定（NO/FALSE/DENIED）→ INELIGIBLE；
- 权利持有人未知 → PENDING_REVIEW；
- 任一训练相关授权未显式授予（YES/TRUE/AUTHORIZED）→ PENDING_REVIEW；
- 无审查记录 → PENDING_REVIEW；
- 全部显式授予且已审查 → ELIGIBLE。

## 受控导出（learning dataset export）

```bash
python -m moodify learning dataset export \
  --dataset-id MFY-AUDITORY-DATASET-001 \
  --project-dir <proj> --output ./exports/D
```

- 只导出 ELIGIBLE 记录；UNKNOWN/PENDING_REVIEW 失败关闭并报告；
- 校验哈希与 schema 版本；保留 provenance 与权利元数据；
- 保留成对标签；剔除原始个人标识符；
- 产出 manifest；可复现（记录文件无导出时间戳）。

## 铁律

- 仅被处理 ≠ 可训练；权利必须显式满足；
- 客户、授权、私有或第三方音频绝不因被处理而进入训练集；
- 本任务不训练模型；只建立数据契约与受控导出。
