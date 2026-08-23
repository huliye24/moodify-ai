# 03 — Pipeline Stage Contract

**W01-P05 · 2026-08-17 · Stage vocabulary 固定（State≠Stage，CP-INV-16）**

## Stage 总表

| stage_id | 名称 | required/optional | 输入 | 输出 | executor | 超时 | failure 映射 | bypass 资格 | 证据 |
|---|---|---|---|---|---|---|---|---|---|
| 01 | ACQUIRE | required | source object ref | scratch/source/input.wav | worker | 10m | STORAGE_TRANSIENT / INPUT_INVALID（hash 不符） | 否 | hash_ok |
| 02 | VALIDATE | required | scratch source | 元数据（duration/rate/channels） | wave/ffmpeg | 2m | INPUT_INVALID | 否 | metrics |
| 03 | STEM | optional（profile 决定） | scratch source | stems（暂不落盘于主线） | separator adapter（lalal/audiolla） | 30m | EXTERNAL_API_RATE_LIMIT / EXTERNAL_API_TRANSIENT / EXTERNAL_API_PERMANENT | 是（默认） | provider_job_id |
| 04 | ANALYZE | required | scratch source | 听觉/工程特征 metrics | v01_analyzer（注入） | 10m | INTERNAL_BUG | 否 | metrics |
| 05 | JUDGE | required | ANALYZE metrics | 判断（INTERVENE/BYPASS/HUMAN_REVIEW） | judger（注入） | 2m | INTERNAL_BUG | 否 | decision |
| 06 | INTERVENE | conditional（JUDGE=INTERVENE） | source+judgment+profile | 处理对象（intermediate） | renderer（注入） | 20m | PROCESS_CRASH | 是（BYPASS 合法） | params |
| 07 | PROFILE | required | judgment+config | profile 决策（id/version/params） | pipeline | — | — | 否 | decision |
| 08 | RENDER | required | source/intermediate+profile | candidate wav | renderer 或 identity copy | 20m | PROCESS_CRASH | 否 | params |
| 09 | VERIFY | required（hard gate） | render+evidence | PASS/FAIL/HUMAN_REVIEW_REQUIRED | pipeline+verify | 5m | VERIFICATION_FAILED | 否 | decision |
| 10 | REGISTER | required | render+verify 结果 | render_candidate object + evidence object | P03 adapter+repo | 5m | STORAGE_TRANSIENT | 否 | object refs |

## Stage Result 统一结构

```json
{
  "stage": "ANALYZE", "status": "SUCCEEDED", "attempt_id": "...",
  "input_objects": [], "output_objects": [], "evidence_refs": [],
  "metrics": {}, "decision": null, "failure": null,
  "producer_version": "...", "started_at": "...", "finished_at": "..."
}
```

- 状态仅 `SUCCEEDED / BYPASSED / FAILED`（不创造第二套 job lifecycle）。
- 每个执行 stage 必有 StageResult（TST-13）。

## 输入规则（§5.1）

stage 输入只来自：P03 object ref / 显式 config / pipeline context / 前 stage result manifest。禁止"上一步留下的神秘本地文件"（唯一例外：ACQUIRE 写入的 scratch/source/input.wav，由 ACQUIRE 显式声明）。

## 输出规则（§5.2）

| 输出 | 持久化 | 进 OSS | 进 DB | 清理 |
|---|---|---|---|---|
| render candidate | 是 | 是（REGISTER） | objects 行 | — |
| evidence json | 是 | 是（REGISTER） | evidence 行 | — |
| scratch 中间文件 | 否 | 否 | 否 | scratch cleanup |
| stage metrics | 是（候选内嵌） | 否 | 否 | — |
