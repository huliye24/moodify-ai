# W01-P07 — Golden Song 001

Moodify Cognitive Wave 01 的第八个任务包。

## 两个原子任务

1. **Select & Run Golden Song 001**
2. **Blocker-Only Fix + Evidence Freeze**

## 从这一包开始，停止功能扩张

P07 不再问：

> 还能加什么？

只问：

> 前面建立的整个 Moodify，能不能真的把一首歌从源音跑到手机 PLAY？

完整主链：

```text
Source
→ Hash
→ OSS / Data Plane
→ Job
→ Lease / Attempt
→ Compute
→ Verify
→ READY
→ Delivery
→ Android
→ PLAY
```

## Golden Song 必须由人类明确指定

Codex 不允许自己从互联网抓一首歌。

没有真实、熟悉、合法授权的输入：

`STOP — GOLDEN_SONG_NOT_SELECTED`

## 成功有两层

**Engineering Verdict**：系统是否真正跑通。

**Listening Verdict**：处理结果是否真的值得使用。

即使最终人耳认为 Source 更好，只要系统正确选择 BYPASS 或保留原始信号，也可以是一个有价值的 Golden Case。
