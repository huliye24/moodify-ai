# 12 — Completion Candidate Contract

**W01-P05 · 2026-08-17 · 实现：CompletionCandidate（pipeline.py）**

## 字段

| 字段 | 说明 |
|---|---|
| job_id / track_id / attempt_id / lease_id | 身份 + fencing |
| pipeline_version | 生产语义版本 |
| production_fingerprint | 确定性指纹 |
| source_object_id | 追溯起点 |
| ready_candidate_object_id | 最终候选对象（renders） |
| supporting_object_ids | evidence 等辅助对象 |
| evidence_refs | 证据引用 |
| verification_result | PASS（硬门后） |
| resource_summary | 预留 |
| stage_results | 全 stage 记录（TST-13） |
| completed_at | 完成时间 |

## 契约（§18）

- P05 不返回"一个路径"——返回 CompletionCandidate。
- P04 控制平面验证后决定 `VERIFYING -> READY`（TST-15：worker 无直接写 READY 权限）。
- 对象注册走 P03：renders/render_candidate（ready_candidate_object_id）+ evidence/verification。

## 集成调用路径（测试验证）

```text
claim (P04) → run_pipeline(ctx) → CompletionCandidate
→ complete(job_id, lease_id, worker_id, ready_object_id, verification_evidence=True) (P04)
→ READY
```

（test_integration_full_compute_run 全链验证，合成 wav。）
