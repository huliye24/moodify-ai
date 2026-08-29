# Codex Execution Prompt — W01-P05

你正在执行：

**Moodify Cognitive Wave 01 / W01-P05 — Cloud Audio Compute Pipeline**

## 第一步

读取 P03 + P04，然后生成：

`CURRENT_AUDIO_CAPABILITY_MAP.md`

不要先写新的 pipeline。

## 两个任务

### T05-1
收敛一条 canonical compute pipeline：

Acquire
→ Validate
→ optional Stem
→ Analyze
→ Judge
→ Intervene/BYPASS
→ Profile
→ Render
→ Verify
→ Register

### T05-2
固定：

- stage contract
- pipeline version
- production fingerprint
- profile version
- external adapter contract
- BYPASS
- scratch
- failure mapping
- verification
- CompletionCandidate

## 必须遵守

- State != Stage
- worker 不能直接 READY
- external API 不可成为黑箱无 provenance
- durable output 必须 P03 register
- failures 必须映射 P04 taxonomy
- stale lease/attempt 不能 commit
- uncertainty 可导致 BYPASS/HUMAN_REVIEW
- 不强制每首歌分轨
- 不强制每首歌干预

## 完成标准

用测试环境或授权样本完成一次 compute E2E。

不是 Golden Song。

完成后停止，不进入 P06。
