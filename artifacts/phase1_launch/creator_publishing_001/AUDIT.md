# Creator Publishing V1 — Audit & Evidence

**Package:** MFY_MUSIC_CREATOR_PUBLISHING_V1_001 (50)
**Date:** 2026-08-14

## 1. 现状审计（KEEP / ADAPT / COMPLETE / ISOLATE）

| 资产 | 分类 | 结论 |
|---|---|---|
| Creator Profile / Track / Version / Passport / Publish（服务端） | **KEEP** | 30/32 包成果：所有权检查、幂等写、不可变版本齐全 |
| 恢复阶段派生（media_ready→published→archived） | **KEEP** | test_lifecycle 覆盖 resume/stage 隔离 |
| 幂等（同键同载荷重放 / 异载荷冲突） | **KEEP** | test_idempotency_audit 覆盖 |
| Studio 确认预览卡 | **KEEP（本包验证）** | 真实公开 URL + SHA-256 指纹 + 非版权声明 + creator_writes 门 |
| 发布响应丢失恢复 | **KEEP（本包补测）** | 读服务端 Track 状态恢复（GET /tracks/{id} 带 actor） |
| Passport 越权 | **KEEP（本包补测）** | PUT passport 非 owner → 403 OWNERSHIP_DENIED |
| Abandon 媒体保留 | **KEEP（本包补测）** | 归档不删媒体；无媒体删除端点（404） |
| BFF 上传（媒体根） | **KEEP** | 51 包已收敛 actor；51 包测试覆盖 |

## 2. 本包新增测试（tests/test_creator_publishing.py，4 项）

| 场景 | 断言 |
|---|---|
| Passport IDOR（B 写 A 的 passport） | 403 OWNERSHIP_DENIED |
| 发布需 Passport blocker + 响应丢失后读权威状态 | 409 PUBLISH_REQUIRES_PASSPORT → 补 passport → published → GET 状态 published + current_version_id |
| Abandon 保留引用媒体 | archived + current_version_id 保留 + 无媒体删除端点 |
| 同键同载荷发布重放 | 200 published + idempotency_keys 仅 1 行（无重复动作） |

## 3. 客户端静态检查（tests/creator-studio.test.mjs，6 项）

- Passport 免责声明存在且不声称认证；
- 全部 creator 写操作携带 Idempotency-Key（client + studio 生成）；
- 恢复读服务端 stage，不信任 localStorage；
- 无伪发布按钮（handler 必须真实动作）；
- 预览/blocker 明确（CONFIRM 卡：公开 URL、指纹、非版权声明、creator_writes 门）；
- 客户端不持久化秘密/音频正文。

## 4. 验收对照（50 包 P0）

| 要求 | 结果 |
|---|---|
| 服务端派生恢复阶段，无第二状态机 | ✓ 既有 + test_lifecycle |
| Creator 是 User 的资料非第二账号 | ✓ 51 包 ensure-user + 1:0..1 creator_profiles |
| handle 唯一可变、ID 不可变、服务端 ownership | ✓ 既有测试 |
| 客户端 actor 头不具权威 | ✓ 51 包（BFF 忽略客户端 actor） |
| 跨用户读草稿/版本/Passport/Inbox 失败 | ✓ 既有（draft isolation）+ 本包（passport IDOR） |
| allocate/upload/promote 分离、失败清理 | ✓ 既有（BFF media + test_bff） |
| 资产可验证（SHA-256/size/mime/duration） | ✓ 既有（media 测试） |
| 删除前零引用/保留期/dry-run，V1 不自动删 | ✓ 本包（无删除端点） |
| Passport 免责声明固定显示 | ✓ 客户端检查 |
| 发布幂等、响应丢失读状态、恢复记录不存秘密 | ✓ 既有 + 本包 |
| abandoned → archived + audit，不删媒体 | ✓ 既有 + 本包 |
| Inbox intent 非支付/法律许可 | ✓ 既有（51 契约文档） |

## 5. 事实边界

- 发布"真实公开"验证依赖线上 BFF（54 包端到端）；本包为服务端契约 + 客户端静态证据。
- 上传中断的分片续传不在 V1 范围（既有 resume 覆盖到 media_ready）。
