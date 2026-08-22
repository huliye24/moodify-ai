# Codex Execution Prompt — W01-P03

你正在执行：

**Moodify Cognitive Wave 01 / W01-P03 — Data Plane: OSS + PolarDB**

## 必须先通过三个 Gate

- P00 Reality
- P01 Canon
- P02 Topology

如果 metadata DB 或 object storage role 未明确：

`STOP`

## 三个任务

### T03-1
建立 OSS object namespace：
- source
- stems
- analysis
- intermediate
- render
- evidence

source object 不可覆盖。

### T03-2
建立 metadata model：
- tracks
- jobs
- objects
- evidence
- versions（如现有系统无等价权威）

不要在这里定义最终 state machine。

### T03-3
建立唯一 Data Identity Contract：
- Track
- Job
- Object
- Hash
- Version
- Evidence
- Provenance

## 写入 Gate

没有明确授权：

- 不执行 production schema migration
- 不创建/修改 OSS bucket
- 不上传真实音频

可以完成 migration files、adapter、tests 和 dry-run。

## 禁止

- 第二套 Job authority
- queue scheduler
- retry engine
- audio pipeline expansion
- playback API
- public-read bucket
- Android 长期云密钥
- large audio blob in DB

完成 P04 Handoff 后停止。
