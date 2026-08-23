# 08 — Failure Taxonomy

**W01-P04 · 2026-08-17 · 实现：FailureRecord + FAILURE_CLASSES（control.py）**

## 结构

每个失败必须至少有（CP-INV-12）：

```text
failure_class   : 顶层类（14 种，固定词表）
failure_code    : 具体代码（如 LALAL_TIMEOUT、SOURCE_FORMAT_UNSUPPORTED）
summary         : 人类可读摘要（可选）
retryable       : 由 class 推导
```

## 14 个顶层类

| class | retryable | max_attempts | 示例 code |
|---|---|---|---|
| INPUT_INVALID | 否 | 1 | SOURCE_FORMAT_UNSUPPORTED / SOURCE_HASH_MISMATCH |
| STORAGE_TRANSIENT | 是 | 3 | OSS_UPLOAD_TIMEOUT |
| STORAGE_PERMANENT | 否 | 1 | OBJECT_NOT_FOUND |
| DB_TRANSIENT | 是 | 3 | DB_CONNECTION_LOST |
| EXTERNAL_API_RATE_LIMIT | 是 | 3 | LALAL_RATE_LIMITED |
| EXTERNAL_API_TRANSIENT | 是 | 3 | LALAL_TIMEOUT |
| EXTERNAL_API_PERMANENT | 否 | 1 | LALAL_REJECTED |
| WORKER_RESOURCE_EXHAUSTED | 是 | 2 | WORKER_MEMORY_LOW |
| PROCESS_TIMEOUT | 是 | 2 | PIPELINE_STAGE_TIMEOUT |
| PROCESS_CRASH | 是 | 3 | WORKER_CRASHED（recover 默认） |
| VERIFICATION_FAILED | 否 | 1 | IDENTITY_GATE_FAILED |
| INTERNAL_BUG | 否 | 1 | UNEXPECTED_EXCEPTION |
| CANCELED_BY_USER | 否 | 1 | USER_CANCELED |
| UNKNOWN_FAILURE | 是 | 2 | UNKNOWN |

## 规则

- 不为每个 traceback 创造独立顶层类（§8 禁止）。
- 具体 code 自由扩展，class 固定。
- 日志要求（§15）：日志带 track_id/job_id/attempt_id/correlation_id/stage/worker_id；不输出 Secret；不留无结构 traceback 而无 failure record。
