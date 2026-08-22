# 13 — Pipeline Test Report

**W01-P05 · 2026-08-17 · 16/16 PASS（tests/test_pipeline.py）**

| 测试 | 验证 | 结果 |
|---|---|---|
| TST-01 Source Integrity | 下载 hash 与 P03 record 一致 | PASS |
| TST-02 Invalid Audio | 损坏输入 → INPUT_INVALID | PASS |
| TST-03 Optional Stem Bypass | profile 无 STEM → separator 不调用 | PASS |
| TST-04 External API Transient | 模拟超时 → EXTERNAL_API_TRANSIENT | PASS |
| TST-05 Judgment BYPASS | 无证据 → 合法 BYPASS 继续至候选 | PASS |
| TST-06 Profile Version Binding | 参数变化 → fingerprint 变化 | PASS |
| TST-07 Render Provenance | candidate 追溯 source/job/pipeline | PASS |
| TST-08 Verification Failure | 验证失败 → VERIFICATION_FAILED，无 PASS candidate | PASS |
| TST-09 Stale Lease Before Upload | lease 失效 → abort | PASS |
| TST-10 Duplicate Pipeline Replay | 同语义 → 同 fingerprint | PASS |
| TST-11 Scratch Cleanup | 成功/失败后清理 | PASS |
| TST-12 No Secret Logging | manifest 无凭据形态 | PASS |
| TST-13 Stage Result Completeness | 每执行 stage 有 StageResult | PASS |
| TST-14 Object Registration | durable 输出经 adapter 注册 | PASS |
| TST-15 No Direct READY Mutation | worker 不直接写 READY | PASS |
| Integration | 合成 wav 端到端：claim→…→complete→READY | PASS |

## 执行

```text
python -m pytest moodify-core-package/tests/test_pipeline.py
16 passed in ~7s
ruff：All checks passed
```

## 集成 compute run（§22）

测试环境端到端（合成 1s 正弦 wav，非真实音频）：

```text
claim → ACQUIRE → VALIDATE → STEM(BYPASS) → ANALYZE → JUDGE(BYPASS)
     → INTERVENE(BYPASS) → PROFILE → RENDER(identity) → VERIFY(PASS)
     → REGISTER(render+evidence) → CompletionCandidate → complete() → READY
```

- 证明计算链作为工程系统可工作（非 P07 Golden Song）。
