# Creator Lifecycle State & Failure Contract — MFY_MUSIC_CREATOR_LIFECYCLE_001

状态权威：PolarDB moodify_dev（现有实体，不建第二套状态机）。
媒体权威：LA `/opt/moodify/music-media/audio`（BFF 上传落盘，nginx /audio/ 公开）。

## 阶段映射（服务器事实派生）

| 阶段 | 服务器事实 | 可恢复动作 |
|---|---|---|
| media_ready | 媒体已上传（asset_key/SHA-256 已返回，文件在 LA） | 创建草稿；若已建则跳过 |
| draft | Track 存在且 status=draft、无 current_version | 补版本或放弃 |
| version_ready | current_version 存在、无 passport | 补护照或确认发布 |
| passport_ready | passport 存在、未发布 | 人工确认发布 |
| published | Track status=published | 查看公开页；重复发布安全返回 |
| archived（abandoned） | Track status=archived | 只读；媒体进入引用检查 |

## 客户端恢复记录（允许）

`localStorage.mfy_workflow_v1`：workflow_id、draft_id、media {asset_key, sha256, filename, size, mtime}、
幂等键 {creator, track, version, passport, publish}、last_step。

禁止：邀请码、Cookie、服务密钥、音频正文。客户端记录只用于恢复提示，
必须与服务器 `resume` 端点对账，不得直接驱动发布结论。

## 失败矩阵

| 失败 | 服务器行为 | 恢复 |
|---|---|---|
| 上传中断 | 临时文件清理（BFF allocate/promote 分离） | 重传或重试；无媒体记录残留 |
| 上传成功、建草稿失败 | 媒体保留在 LA（引用检查保护） | resume：media_ready → 建草稿 |
| API 超时 | 幂等键不变 | 同键重放（POST 幂等）；禁止新键试探 |
| 版本成功、护照失败 | 草稿+版本已持久 | resume：version_ready → 补护照（不重复建版本） |
| 发布响应丢失 | Track 可能已 published | resume 读 Track 状态 → 已发布则查看，未发布则确认 |
| 放弃草稿 | status→archived + audit | 媒体不删；进入引用检查（保留期后 dry-run 候选） |

## 审计动作（audit_events）

track.abandoned、media.audit_dry_run、media.audit_applied（逐项，actor=system）。

## 不可破坏约束

- BFF 不直连 PolarDB；客户端 actor header 不具权威（服务器身份绑定）。
- 删除媒体前必须零版本引用 + 保留期；dry-run 默认；删除用精确路径。
- Creation Passport 是来源声明，非版权认证。
