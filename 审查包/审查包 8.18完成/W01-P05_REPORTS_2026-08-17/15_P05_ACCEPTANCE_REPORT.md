# 15 — P05 Acceptance Report

**W01-P05 · 2026-08-17 · base: P00..P04（HEAD 9ca0bbd）**

## 验收标准逐项（任务书 §27）

- [x] P03/P04 Gate 通过（Data Identity + Control Plane 契约齐备）
- [x] Current Audio Capability Map 完成（01 报告，14 项）
- [x] 只有一条 canonical compute pipeline（PipelineRunner）
- [x] stage vocabulary 固定（10 阶段，03 报告）
- [x] stage input/output 显式（03 报告 + StageResult）
- [x] 无关键"神秘本地文件"依赖（唯一例外 ACQUIRE 显式声明的 scratch source）
- [x] external API 通过 adapter（separator 注入契约）
- [x] JUDGE 输出 evidence + uncertainty（judgment 结构）
- [x] BYPASS 是合法一等决策（TST-05）
- [x] profile/preset 版本化（TST-06 fingerprint 绑定）
- [x] render contract 固定（WAV/PCM16/44.1k 首阶段）
- [x] VERIFY 是 completion 前硬门（TST-08）
- [x] pipeline version 固定（04 报告）
- [x] production fingerprint 可生成（production_fingerprint()，TST-10）
- [x] scratch 生命周期明确（10 报告，TST-11）
- [x] stale attempt 不能提交结果（TST-09 lease checkpoint）
- [x] failure 映射到 P04 taxonomy（11 报告）
- [x] durable output 通过 P03 注册（TST-14）
- [x] worker 不直接写 READY（TST-15）
- [x] integration compute test 通过（合成 wav 全链）
- [x] P06 Handoff 完成（14 报告）
- [x] 完成后停止，不进入 P06

## 代码清单（本包新增）

```
moodify-core-package/src/moodify/data_plane/pipeline.py   (PipelineRunner/StageResult/CompletionCandidate/JobContext/ScratchManager/production_fingerprint/PipelineError)
moodify-core-package/tests/test_pipeline.py               (16 测试)
```

## 验证

- pytest：16/16（pipeline）+ 12（control）+ 9（data plane）+ 3（guard）= **40 passed**
- ruff：All checks passed
- 集成 run：合成 wav 全链 READY

## 事实边界

1. 使用合成正弦 wav（无真实音频）；真实曲目 P07 Golden Song。
2. analyzer/judger/renderer 为注入式默认实现（v01 三件套接入在 worker 层）；测试用最小实现。
3. STEM/lalal 真实适配器未接（授权后）。
4. 生产 worker 循环未实现（P04 deploy block 延续）。
