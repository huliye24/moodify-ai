# AI Execution Rules｜MT-007

1. 先读 Manifest，再读 Node Status，再读当前 AEP。
2. 每次只执行一个 AEP。
3. 不要扩大 MVP 范围。
4. 不要先做复杂 GUI。
5. 所有输出必须关联 import_id、job_id、preset_id、mrs_result_id、report_id、export_id。
6. 报告必须可读，元数据必须可机器解析。
7. 每次修改必须更新 Decision Log。
8. 若发现依赖未完成，标记 BLOCKED，不要伪造结果。
