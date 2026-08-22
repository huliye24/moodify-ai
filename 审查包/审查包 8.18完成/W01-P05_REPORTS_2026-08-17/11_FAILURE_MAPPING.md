# 11 — Failure Mapping

**W01-P05 · 2026-08-17 · 底层异常 → P04 taxonomy（禁止发明第二套）**

## 映射表（§17）

| Pipeline Failure | P04 Failure Class | 触发点 |
|---|---|---|
| decode failed / 损坏源 | INPUT_INVALID | VALIDATE（TST-02） |
| source hash 不符 | INPUT_INVALID | ACQUIRE |
| 空音频 | INPUT_INVALID | VALIDATE |
| OSS 获取超时 | STORAGE_TRANSIENT | ACQUIRE |
| 对象不存在 | STORAGE_PERMANENT | ACQUIRE |
| separator API 429 | EXTERNAL_API_RATE_LIMIT | STEM |
| separator 超时/瞬时 | EXTERNAL_API_TRANSIENT | STEM（TST-04） |
| separator 永久拒绝 | EXTERNAL_API_PERMANENT | STEM |
| OOM / 资源不足 | WORKER_RESOURCE_EXHAUSTED | worker 侧（P05 后） |
| FFmpeg/stage 超时 | PROCESS_TIMEOUT | stage 层 |
| 工具崩溃 | PROCESS_CRASH | INTERVENE/RENDER |
| verify 目标未达 | VERIFICATION_FAILED | VERIFY（TST-08） |
| 意外不变量/异常 | INTERNAL_BUG | ANALYZE/JUDGE |

## 实现

- `PipelineError(failure_class, failure_code, summary)`——所有 stage 异常经此包装。
- 调用方（worker 循环）捕获后调用 P04 `fail()`（failure_class 直接映射 retry 预算）。

## 禁止

- worker 自创顶层 failure class；
- 为每个 traceback 创造独立类；
- 无结构 traceback 而无 failure record（P04 §15）。
