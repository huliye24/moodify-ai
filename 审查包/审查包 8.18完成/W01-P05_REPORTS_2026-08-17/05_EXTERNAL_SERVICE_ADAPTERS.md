# 05 — External Service Adapters

**W01-P05 · 2026-08-17 · STEM stage 通过统一 adapter（§7.1）**

## Separator Adapter 契约

```text
separate(input_object_path, requested_roles, context)
→ StemResult
```

StemResult 至少：provider / provider_version_or_model / requested_roles / produced stems / content hashes / duration alignment / sample rate / channel count / evidence / provider_job_reference。

## 外部 API 规则（§7.2）

- timeout：适配器实现（stage 超时见 03 表）。
- rate-limit → `EXTERNAL_API_RATE_LIMIT`；transient → `EXTERNAL_API_TRANSIENT`；permanent → `EXTERNAL_API_PERMANENT`（TST-04 验证映射）。
- 不 log secret；provider job id 记录（evidence_refs）。
- input/output provenance 保留（object refs）。
- provider version/model 记录（如可得）。
- cost/usage metadata（如可得）。

## 后端现状

| 后端 | 状态 | 说明 |
|---|---|---|
| audiolla 容器（LA）+ LALAL.AI | EXTERNAL_AVAILABLE | 已部署健康；无自动调用证据 → STEM 默认 BYPASS |
| Demucs | UNAVAILABLE | 权重未下载；不引入 |

## 实现

- `PipelineRunner(separator=...)` 注入；测试用 fake separator（TST-03/04）。
- 真实 lalal 适配器：P05 提供契约，接入在授权 + 自动 pipeline 批准后（P07 Golden Song 前置）。
