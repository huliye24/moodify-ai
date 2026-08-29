# 10 — Local Scratch Contract

**W01-P05 · 2026-08-17 · 本地磁盘只是 scratch（P02 R5），实现：ScratchManager**

## 规则

| 项 | 值 |
|---|---|
| scratch root | 由 ScratchManager 注入（测试/部署配置） |
| per-job 目录 | `scratch/{job_id}/{attempt_id}/` |
| naming | job/attempt 前缀目录，禁止用户文件名做路径段 |
| max disk budget | 未专门限制（当前单 worker；P08 容量契约再定） |
| cleanup on success | 是（run() finally 清理，TST-11） |
| cleanup on failure | 是（finally 清理） |
| cleanup after crash | 进程崩溃残留 → 下次 worker 启动按 job 目录清理（P05 后 worker 循环） |
| preserve-on-debug | `keep=True` 参数保留（调试用） |
| path traversal guard | object key 由 P03 约定生成（track_id/job_id 均为 UUID 前缀 ID，无用户输入）；adapter 内部路径拼接安全 |

## 允许内容

- downloaded source（scratch/source/input.wav）
- 临时 stems
- 中间文件（analyze/intervene/render）
- 瞬时日志

## 禁止

- scratch 作为长期资产权威（P03/P02 R5）。
- 用户原始文件名直接作为路径段。
