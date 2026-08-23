# 02 — Unified Pipeline Architecture

**W01-P05 · 2026-08-17 · 唯一 canonical compute pipeline（§3 硬规则：不塞历史代码）**

## 管线

```text
ACQUIRE → VALIDATE → STEM(optional) → ANALYZE → JUDGE
       → INTERVENE/BYPASS → PROFILE → RENDER → VERIFY → REGISTER
       → CompletionCandidate（P04 控制面决定 VERIFYING→READY）
```

- 内部生产线，非用户 UI。
- 不是所有歌曲都走全部步骤（STEM 默认 BYPASS；JUDGE 可 BYPASS）。
- **Worker 不直接写 READY**：管线返回 CompletionCandidate；READY 由 P04 `complete()` 决定（TST-15）。

## 分层

| 层 | 组件 | 责任 |
|---|---|---|
| 控制面 | P04 JobControlPlane | lease/state/READY（本包只调用 checkpoint 与 complete） |
| 数据面 | P03 repository + adapter | 对象注册/获取 |
| 计算线 | P05 PipelineRunner | 阶段编排（本包） |
| 能力适配 | analyzer/judger/renderer/separator | 注入式 adapter（v01 三件套为默认实现） |

## 关键规则

1. **注入式依赖**：PipelineRunner 通过构造参数注入 analyzer/judger/renderer/separator；JobContext 显式携带全部运行输入（无全局变量/隐式目录）。
2. **Lease checkpoint**：before_acquire / before_external_submit / before_durable_upload / before_register 四处检查；失效 → STALE_ATTEMPT_ABORT（TST-09）。
3. **失败即停**：任一 stage PipelineError → 抛出携带 P04 failure_class（调用方上报 fail()）；无半成品 candidate。
4. **BYPASS 一等决策**：JUDGE 无证据 → INTERVENE BYPASS；无 renderer → identity copy（保留原信号）。
5. **Scratch 生命周期**：`scratch/{job_id}/{attempt_id}/`，成功/失败后清理（TST-11）。
6. **Durable 输出**：RENDER/VERIFY 产物经 `_register_durable()` 走 P03 adapter + repository（TST-14）。

## 实现

- `moodify.data_plane.pipeline`：PipelineRunner / StageResult / CompletionCandidate / JobContext / ScratchManager / production_fingerprint / PipelineError。
- 默认 analyzer/judger/renderer 由上层注入（v01 三件套；本包测试用最小实现 + 合成 wav）。
