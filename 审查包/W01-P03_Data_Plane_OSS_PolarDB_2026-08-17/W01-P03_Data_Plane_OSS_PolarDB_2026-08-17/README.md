# W01-P03 — Data Plane: OSS + PolarDB

Moodify Cognitive Wave 01 的第四个任务包。

## 三个原子任务

1. OSS Object Space & Object Identity
2. PolarDB Metadata Model
3. Track / Job / Object / Hash / Version / Evidence Contract

## 本包第一次进入“建设”

但不是无条件改生产环境。

数据库写入和 OSS 写入都有独立 Gate。

如果权限、备份、区域、bucket 或 metadata DB authority 没有明确：

- `SCHEMA_WRITE_BLOCKED`
- `OSS_WRITE_BLOCKED`

仍然可以完成：

- 数据模型
- migration
- adapters
- object key convention
- provenance contract
- tests

## 目标

以后任意一个 READY render 都可以反向回答：

> 我来自哪一首 Track、哪一个 Source、哪一次 Job、哪一套 Pipeline、哪一个 Preset/Tool Version、有哪些 Evidence。

这就是 Moodify 数据平面的主脊梁。
