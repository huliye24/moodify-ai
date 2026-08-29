# W01-P05 — Cloud Audio Compute Pipeline

这是 Moodify Cognitive Wave 01 的第六个任务包。

## 两个原子任务

1. **Unified Audio Compute Pipeline**
2. **Pipeline Version / Failure / BYPASS / Recovery / Output Contract**

## 这一包第一次真正进入“声音计算主河道”

P04 已经解决 Job 怎么流动。

P05 只负责：

> 一个合法 RUNNING Job 到底怎样被算完。

目标主链：

```text
Acquire
→ Validate
→ Stem (optional)
→ Analyze
→ Judge
→ Intervene / BYPASS
→ Profile
→ Render
→ Verify
→ Register
→ CompletionCandidate
```

## 三条硬边界

**Worker 不直接写 READY。**

**BYPASS 是合法结果，不是失败。**

**同一个最终 Render 必须能追溯到 Source + Job + Pipeline + Profile + Tool Version + Evidence。**

P07 才是真正的 Golden Song。P05 只证明计算链工程上成立。
