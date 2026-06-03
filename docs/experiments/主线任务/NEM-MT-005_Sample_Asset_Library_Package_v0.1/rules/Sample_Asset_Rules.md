# Sample Asset Rules

## 样本必备字段

- sample_id
- original_filename
- source_platform
- source_type
- collected_at
- registered_at
- file_format
- duration_sec
- sample_rate
- bit_depth
- channels
- genre_tags
- emotion_tags
- quality_tier
- rights_status
- storage_path
- status

## 样本状态

- raw_inbox
- registered
- baseline
- validation
- stress_test
- production_candidate
- archived
- restricted

## 权限规则

- uncertain：权限不确定，仅可内部低风险检查，不能公开展示或商业使用。
- internal_research_only：仅用于内部研究和质量评估。
- user_owned：用户拥有或明确授权。
- licensed：已授权。
- public_domain：公共领域。
- restricted：不可继续使用。

## 禁止事项

- 禁止无来源样本进入正式资产库；
- 禁止无权限状态样本进入 validation / production_candidate；
- 禁止原始文件和处理结果混放；
- 禁止修改 sample_id；
- 禁止删除 lineage 历史。
