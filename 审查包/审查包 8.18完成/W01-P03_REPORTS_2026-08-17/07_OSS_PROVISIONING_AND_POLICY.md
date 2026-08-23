# 07 — OSS Provisioning & Policy

**W01-P03 · 2026-08-17 · 状态：`OSS_WRITE_BLOCKED`（NOT_PROVISIONED，未创建/未上传）**

## Provisioning Gate（§6）逐项

- [x] P02 确定 object storage（ADR-004 → OSS OBJECT_STORAGE）
- [ ] bucket 已由人类开通或明确授权 Codex 创建 —— **否（NOT_PROVISIONED）**
- [ ] region/endpoint 已确认 —— **否**
- [ ] credential source 已确认 —— **否（P00 TT-036；无凭据）**
- [ ] lifecycle/versioning decision 已确认 —— **否**
- [ ] public access policy 已确认 —— **否（默认禁止 public-read）**
- [ ] test prefix 已定义 —— 本包已定义（`moodify/tracks/` 结构即 prefix 方案）
- **结论：OSS_WRITE_BLOCKED**

## 开通后配置意图（不执行）

| 项 | 建议 |
|---|---|
| Region | cn-hangzhou（与杭州/PolarDB 同地域，P02 NW 原则） |
| Bucket | 单 bucket `moodify`（prefix 分域；如后续需要公开/私有隔离再评估多 bucket） |
| Access | 私有；服务端 STS/RAM 角色；客户端永不持长期凭据（INV-13/R7） |
| Versioning | 建议开启（source 不可覆盖语义 + 恢复） |
| Lifecycle | intermediate → 30 天；renders → 长期；source/evidence → long-lived（P03 §10 意图表） |
| Test prefix | `moodify/tracks/{trk_*/source/` 等 dry-run 路径 |

## Retention 意图表（§10）

| Artifact | Retention | 说明 |
|---|---|---|
| source | long-lived / user policy | INV-01 不可覆盖 |
| stems | configurable | P05 决定 |
| intermediate | short / cleanup candidate | lifecycle 候选 |
| render | versioned / user-facing | 每次渲染新 object_id |
| evidence | long-lived | 追溯审计 |
| logs | operational | 不落 OSS（journald） |
| temp scratch | ephemeral | worker 本地 |

## 代码现状

- `moodify.data_plane.adapter.OSSAdapter`：占位（所有方法 raise `OSS_WRITE_BLOCKED`），开通后实现。
- `LocalFileAdapter`：dry-run/测试实现（Test 已用）。
