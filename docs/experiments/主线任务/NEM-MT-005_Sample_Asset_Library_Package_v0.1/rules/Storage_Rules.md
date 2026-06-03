# Storage Rules

1. 原始文件必须保存为 original 文件，不可覆盖。
2. 所有处理结果必须进入 processed/{run_id}/。
3. 所有评分记录进入 metadata 或 lineage 目录中的 jsonl 文件。
4. 所有特征文件进入 features/。
5. 所有报告进入 reports/。
6. 目录移动时必须同步更新 sample_registry。
7. 删除样本前必须先标记 archived 或 restricted，不直接物理删除。
