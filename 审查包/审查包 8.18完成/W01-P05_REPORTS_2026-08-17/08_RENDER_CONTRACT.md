# 08 — Render Contract

**W01-P05 · 2026-08-17**

## RENDER 输出规范（§12）

首阶段固定**稳定可验证格式**（不设计自有加密音频格式）：

| 属性 | 首阶段默认 |
|---|---|
| container | WAV |
| codec | PCM 16-bit |
| sample rate | 44.1kHz（源一致时保持） |
| bit depth | 16 |
| channels | 与 source 一致 |
| loudness policy | 不改变响度（identity/BYPASS 语义）；处理时遵循 profile |
| dither/resample | 不主动 resample（保持源）；resample 仅 profile 显式要求 |
| source lineage | CompletionCandidate.source_object_id |
| profile/pipeline version | candidate 内嵌 |

## RENDER 行为

- 输入：intervene 产物（若 INTERVENE）或 source（BYPASS）。
- 无 renderer 注入时：**identity copy**（保留原信号，合法 BYPASS 语义）——不失败。
- 输出：`scratch/{job}/{attempt}/render/candidate.wav` → REGISTER 阶段转 durable object（artifact_type=renders, artifact_role=render_candidate）。

## 未来（不在 P05）

- 自有格式 / 加密 / 流式：P06+ 评估。
- 高保真无损（Media3 播放器支持）：P06 播放面评估。
