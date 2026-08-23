# 09 — Verification Contract

**W01-P05 · 2026-08-17 · VERIFY 是 completion 前硬门（§13）**

## 三层验证

### 1. Technical Verification（必须）

- 文件存在、非空
- hash 可计算
- decode 成功（wave/ffmpeg）
- duration sane（>0 帧）
- sample rate/channels 符合预期
- 无 NaN/无效数据（PCM16 无 NaN 风险；浮点格式时检查）
- 无灾难性 clipping/overflow（wave 读帧校验）
- 无截断（frames 与 header 一致）

### 2. Comparative Verification（INTERVENE 时）

- before/after metrics（algorithmic_review 可复用——CANONICAL_AVAILABLE）
- 无不支持的质量退化
- judgment target 改善/保持
- evidence 完整

### 3. Human Verification（policy 要求时）

- human verdict / reviewer / date / comparison ref

## Verify Result

只允许：`PASS` / `FAIL` / `HUMAN_REVIEW_REQUIRED`。**只有 PASS 才能提交 completion candidate**（TST-08）。

## 实现

- VERIFY stage：技术验证（wave decode + 非空）；失败 → PipelineError(VERIFICATION_FAILED)（调用方上报 P04 fail）。
- 比较验证（algorithmic_review 接入）：P07 Golden Song 前置（本包提供接口，默认不启用）。
- verification evidence：REGISTER 阶段写 verify json 到 evidence object（TST-14）。
