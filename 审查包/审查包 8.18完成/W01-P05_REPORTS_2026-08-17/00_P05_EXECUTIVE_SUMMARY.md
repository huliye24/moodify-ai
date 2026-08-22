# 00 — P05 Executive Summary

**Package:** W01-P05 — Cloud Audio Compute Pipeline
**执行时间:** 2026-08-17 23:20–23:55 CST
**性质:** 音频计算主链建设（代码 + 契约 + 测试 + 集成 run）

## 两个原子任务

- **T05-1 Unified Pipeline**：Capability Map（14 项能力分类）→ 收敛唯一 canonical pipeline（ACQUIRE→VALIDATE→STEM(optional)→ANALYZE→JUDGE→INTERVENE/BYPASS→PROFILE→RENDER→VERIFY→REGISTER→CompletionCandidate）。
- **T05-2 契约**：pipeline version / production fingerprint / stage vocabulary / failure mapping / BYPASS / scratch / external adapters / output registration / CompletionCandidate。

## 关键决策

1. **不塞历史代码**（硬规则 §3）：主线只用 v01 三件套（analyze/diagnose/process）+ FFmpeg + algorithmic_review（可选）+ stems adapter；MAMSE/era/identity/reconstruction 全部保留 INTERNAL/EXPERIMENTAL 域。
2. **STEM 默认 BYPASS**：audiolla 已部署但无自动调用证据；adapter 契约就绪，接入待授权。
3. **BYPASS 是一等决策**：无证据 → 保留原信号（identity render 合法）。
4. **Worker 无 READY 权限**：管线返回 CompletionCandidate，READY 由 P04 complete() 决定。
5. **Lease checkpoint**：4 个检查点（acquire 前/外部提交前/上传前/注册前）。

## 验证

- **16/16 测试**（TST-01..15 + 集成 compute run）PASS；ruff 干净。
- 集成 run：合成 wav 全链 claim→…→complete→READY（证明计算链工程可用，非 P07 Golden）。

## Gate

- P03/P04 Gate 通过（identity/control 契约齐备）。
- 无部署（测试环境端到端；生产 worker 切换 CONTROL_PLANE_DEPLOY_BLOCKED 延续）。

**完成后停止，等待人类审核，不进入 P06。**
